from random import randrange
from functools import partial

import torch
import accelerate
import bitsandbytes as bnb

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import PeftModel
import time
class P1_inferecening():    
    
    def get_inference(self, model_name, user_prompt):
      tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
      model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).cuda()
      inputs = tokenizer(user_prompt, return_tensors="pt").to(model.device)
      start = time.time()
      outputs = model.generate(**inputs, max_new_tokens=512, do_sample=False, top_k=50, top_p=0.5, temperature=0.5, num_return_sequences=1, eos_token_id=32021)
      ans = tokenizer.decode(outputs[0], skip_special_tokens=True)
      end = time.time()
      latency = end - start
      return ans, latency

class P2_inferencing():
    def __init__(self) -> None:
      self.model = None
      self.tokenizer = None
   
    def P2_load_model(self, model_name, infer_model):
      self.tokenizer = AutoTokenizer.from_pretrained(model_name)
      self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
      self.tokenizer.add_special_tokens({'bos_token': '<s>'})
      self.tokenizer.add_special_tokens({'eos_token': '</s>'})
      
      bnb_config = BitsAndBytesConfig(
          load_in_4bit=True,
          bnb_4bit_use_double_quant=True,
          bnb_4bit_quant_type="nf4",
          bnb_4bit_compute_dtype=torch.bfloat16,
      )

      inf_model = AutoModelForCausalLM.from_pretrained(
          model_name,
          quantization_config=bnb_config,
          device_map="auto",
      )

      self.model = PeftModel.from_pretrained(inf_model, infer_model, device_map='auto', timeout=120)
      
      with torch.no_grad():
        self.model.resize_token_embeddings(len(self.tokenizer))
      self.model.config.pad_token_id = self.tokenizer.pad_token_id
      self.model.config.bos_token_id = self.tokenizer.bos_token_id
      self.model.config.eos_token_id = self.tokenizer.eos_token_id
      
      return 

    def P2_get_inference(self, input):
      device = "cuda" if torch.cuda.is_available() else "cpu"
      model_input = self.tokenizer(input['query'], return_tensors="pt").to(device)

      _ = self.model.eval()
      with torch.no_grad():
        start = time.time()
        out = self.model.generate(**model_input, top_k = 250,
                                    top_p = 0.98,
                                    max_new_tokens = 250,
                                    do_sample = True,
                                    temperature = 0.1)
        op = self.tokenizer.decode(out[0], skip_special_tokens=True)
        end = time.time()
        latency = end - start

        return op, latency
       
class P3_inferencing():
    def __init__(self) -> None:
      self.model = None
      self.tokenizer = None
   
    def P3_load_model(self, model_name, infer_model_1, infer_model_2):
      self.tokenizer = AutoTokenizer.from_pretrained(model_name)
      self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
      self.tokenizer.add_special_tokens({'bos_token': '<s>'})
      self.tokenizer.add_special_tokens({'eos_token': '</s>'})
      
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

      model = PeftModel.from_pretrained(model, infer_model_1, device_map='auto')
      with torch.no_grad():
          model.resize_token_embeddings(len(self.tokenizer))
      model.config.pad_token_id = self.tokenizer.pad_token_id
      model.config.bos_token_id = self.tokenizer.bos_token_id
      model.config.eos_token_id = self.tokenizer.eos_token_id
      
      self.model = PeftModel.from_pretrained(model, infer_model_2, device_map='auto')

      with torch.no_grad():
        self.model.resize_token_embeddings(len(self.tokenizer))
      self.model.config.pad_token_id = self.tokenizer.pad_token_id
      self.model.config.bos_token_id = self.tokenizer.bos_token_id
      self.model.config.eos_token_id = self.tokenizer.eos_token_id

      
      return 

    def P3_get_inference(self, input):
      device = "cuda" if torch.cuda.is_available() else "cpu"
      model_input = self.tokenizer(input['query'], return_tensors="pt").to(device)

      _ = self.model.eval()
      with torch.no_grad():
        start = time.time()
        out = self.model.generate(**model_input, top_k = 250,
                                    top_p = 0.98,
                                    max_new_tokens = 250,
                                    do_sample = True,
                                    temperature = 0.1)
        op = self.tokenizer.decode(out[0], skip_special_tokens=True)
        end = time.time()
        latency = end - start

        return op, latency
  