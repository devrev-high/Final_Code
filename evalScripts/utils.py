from transformers import AutoTokenizer, AutoModelForCausalLM

sample_query = open('./Queries/sample_query_P1.txt', 'r').read()
sample_query_bonus = open('./Queries/sample_query_bonus_P1.txt', 'r').read()

prompt_begin ='''
The only code you know to write is of type "var_i = function_call(function_argument)", where i is the ith variable in use.\
You never output anything else other than this format. You follow the sequence of completing query religiously.
You have a given set of functions and you must use them to answer the query. You are not allowed to use any other functions.
Here are the allowed functions-
'''

prompt_end ='''
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
def get_inference(model_name, user_prompt):
  
  tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
  
  model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).cuda()
  
  sys_prompt = """You are a helpful and faithful coding assistant. You follow the given instructions\
      meticulously and ensure an efficient interaction by prioritizing user needs."""
  
  prompt = f"""<s> [INST] <<SYS>>\\n{sys_prompt}\\n<</SYS>>\\n\\n{user_prompt}[/INST]"""
  
  inputs = tokenizer.apply_chat_template(prompt, return_tensors="pt").to(model.device)

  outputs = model.generate(inputs, max_new_tokens=1024, do_sample=False, top_k=50, top_p=0.5, temperature=0.5, num_return_sequences=1, eos_token_id=32021)
  ans = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
  return ans

def completionP1StaticDynamic(model, data_dict):
  prompt = prompt_begin+data_dict['docstring']+"Here are some sample queries \
    and their respective responses:"+sample_query+prompt_end+data_dict['query']
  return get_inference(model,prompt)


def completionP1Bonus(model, data_dict):
  prompt = prompt_begin+data_dict['docstring']+ "If the query requires the use of conditional logic or iterations, use if, else or for loop,\
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
       Here are some sample queries and their respective responses:"+sample_query+prompt_end+data_dict['query']
  
  return get_inference(model,prompt)


def completionP1Modified(model, data_dict):
  prompt = prompt_begin+data_dict['docstring']+prompt_end+data_dict['query']
  return get_inference(model,prompt)


  