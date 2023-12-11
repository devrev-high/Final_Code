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
    def __init__(self) -> None:
      self.sample_query = open('../resources/Queries/sample_query_bonus_P1.txt', 'r').read()
      self.sample_query_bonus = open('../resources/Queries/sample_query_bonus_P1.txt', 'r').read()
      self.prompt_begin ='''
      The only code you know to write is of type "var_i = function_call(function_argument)", where i is the ith variable in use.\
      You never output anything else other than this format. You follow the sequence of completing query religiously.
      You have a given set of functions and you must use them to answer the query. You are not allowed to use any other functions.
      Here are the allowed functions-
      '''

      self.prompt_end ='''
      Answer very strictly in the same format shown above. Make sure to mention type argument wherever relevant when calling works_list.\
      Any missing type arguments is not acceptable. Don't make unnecessary calls to any functions. When given names make sure to call \
      search_object_by_name() to get work_ids. Ensure logical continuity at each step. Ensure that the query is answered fully.
      You are not allowed to nest function calls. You are not allowed to output "python" or any other statement apart from the given format.
      Do not use any other format for output than the one given above. Do not put any comment in your answer. Anything else other \
      than the format specified is not acceptable. Do not define any new helper functions or any other python functions apart from \
      the ones provided.

      Do not output any text apart from the final output code.
      If you are unable to answer a query, you can output "Unanswerable_query_error".
      Answer the query:
      '''
      self.sys_prompt = """You are a helpful and faithful coding assistant. You follow the given instructions\
          meticulously and ensure an efficient interaction by prioritizing user needs."""

    def completionP1StaticDynamic(self, model, data_dict):
      prompt = self.prompt_begin+data_dict['docstring']+"Here are some sample queries \
        and their respective responses:"+self.sample_query+self.prompt_end+data_dict['query']
      
      return self.get_inference(model,prompt)


    def completionP1Bonus(self, model, data_dict):
      
      prompt = self.prompt_begin+data_dict['docstring']+ "If the query requires the use of conditional logic or iterations, use if, else or for loop,\
          in the same format shown in the examples below. In case of a condition or loop, use temp_x in place of var_i inside the block, where x \
          is an integer starting from 1, denoting the index of variable.Do not use temp except in case of a condition or iteration. Variables var_i \
          cannot be called inside the block, only temp_x variables can be used as function arguments in this case. The format is as follows-\
            if (<condition>):\
                temp_1 = function_call(function_argument)\
                temp_2 = ... \
            else:\
                temp_1 = function_call(function_argument)\
                temp_2 = ...\
            for loop_var in <list or range only>:\
                temp_1 = function_call(function_argument)\
                temp_2 = ...\
          Here are some sample queries and their respective responses:"+self.sample_query+self.prompt_end+data_dict['query']
      
      return self.get_inference(model, prompt)
    
    def completionP1Modified(self, model, data_dict):
      
      prompt = self.prompt_begin+data_dict['docstring']+ self.prompt_end+ data_dict['query']
      return self.get_inference(model,prompt)
    
    def get_inference(self, model_name, user_prompt):
      tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
      model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).cuda()
      prompt = "<s> [INST] <<SYS>>\\n"+self.sys_prompt+"\\n<</SYS>>\\n\\n"+user_prompt+"[/INST]"
      inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
      start = time.time()
      outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=False, top_k=50, top_p=0.5, temperature=0.5, num_return_sequences=1, eos_token_id=32021)
      ans = tokenizer.decode(outputs[0], skip_special_tokens=True)
      end = time.time()
      latency = end - start
      return ans, latency

class P2_P3_inferencing():
    def __init__(self) -> None:
      self.model = None
      self.tokenizer = None
   
    def P2_P3_load_model(self, model_name, infer_model):
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

    def P2_P3_get_inference(self, input):
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
       

  