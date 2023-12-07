import os
import argparse
from copy import deepcopy
from random import randrange
from functools import partial
import torch
import accelerate
import bitsandbytes as bnb
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
    get_peft_model,
    PeftModel
)
from trl import SFTTrainer

def find_all_linear_names(model):
    cls = bnb.nn.Linear4bit #if args.bits == 4 else (bnb.nn.Linear8bitLt if args.bits == 8 else torch.nn.Linear)
    lora_module_names = set()
    for name, module in model.named_modules():
        if isinstance(module, cls):
            names = name.split('.')
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])
    # lm_head is often excluded.
    if 'lm_head' in lora_module_names:  # needed for 16-bit
        lora_module_names.remove('lm_head')
    return list(lora_module_names)
# get max length based on hardware constraints
def get_max_length(model):
    conf = model.config
    max_length = None
    for length_setting in ["n_positions", "max_position_embeddings", "seq_length"]:
        max_length = getattr(model.config, length_setting, None)
        if max_length:
            print(f"Found max length: {max_length}")
            break
    if not max_length:
        max_length = 1024
        print(f"Using default max length: {max_length}")
    return max_length
# function to preprocess the dataset
def preprocess_dataset(model, tokenizer: AutoTokenizer, max_length: int, dataset: str, seed: int = 42):
    # Format each prompt.
    print("Preprocessing dataset...")
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    with torch.no_grad():
      model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = tokenizer.pad_token_id
    def preprocess_batch(batch, tokenizer, max_length):
        return tokenizer(
            batch["data"],
            max_length=max_length,
            truncation=True,
        )

    # Apply preprocessing to each batch of the dataset & and remove "conversations" and "text" fields.
    _preprocessing_function = partial(preprocess_batch, max_length=max_length, tokenizer=tokenizer)
    dataset = dataset.map(
        _preprocessing_function,
        batched=True,
        remove_columns=["data"],
    )
    # Shuffle dataset.
    dataset = dataset.shuffle(seed=seed)
    return dataset

def main(args):
    dataset_name = args.dataset
    model_name = args.model
    epochs = args.n
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # Quantization configurations
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    # Finding LORA supporting layers
    modules = find_all_linear_names(model)
    lora_alpha = args.lora_alpha
    lora_dropout = args.lora_dropout
    lora_r = args.lora_r
    peft_config = LoraConfig(
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=modules,
        r=lora_r,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)

    dataset = load_dataset(dataset_name)
    # Change the max length depending on hardware constraints.
    max_length = get_max_length(model)
    #preprocess the dataset
    formatted_dataset = deepcopy(dataset)
    dataset = preprocess_dataset(model, tokenizer, max_length, dataset)
    training_args = TrainingArguments(
        output_dir="./checkpoints/outputs",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,  # Powers of 2.
        learning_rate=args.learning_rate,
        max_grad_norm=1.0,
        lr_scheduler_type="linear",
        warmup_steps=5,
        fp16=True,
        logging_strategy="steps",
        logging_steps=1,
        save_strategy="epoch",
        optim="paged_adamw_8bit",
        num_train_epochs=args.n,
        evaluation_strategy='steps',
        eval_steps=100
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        train_dataset=dataset['train'],
        eval_dataset=dataset['validation']
    )

    results = trainer.train()  # Now we just run train()!
    trainer.save_model('./checkpoints/outputs_best')
    return

if '__name__' == '__main__':
    parser = argparse.ArgumentParser(description="Script for fine-tuning")
    # Add argument(s) here
    parser.add_argument("--dataset", type=str, default="Insight244/p3-stage-1-data-no-dynamic-no-random-no-bonus", help="Name of dataset to finetune")
    parser.add_argument("--model", type=str, default="codellama/CodeLlama-7b-Instruct-hf", help="Name of model to finetune")
    parser.add_argument("--n", type=int, default=5, help="Number of epochs")
    parser.add_argument("--lora_alpha", type=int, default=16, help="Alpha parameter value for LoRA")
    parser.add_argument("--lora_dropout", type=float, default=0.1, help="Dropout parameter value for LoRA")
    parser.add_argument("--lora_r", type=int, default=8, help="R parameter value for LoRA")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Value of learning rate")
    args = parser.parse_args()

    main(args)