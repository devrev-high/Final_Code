import re
import csv
import math
import random
import numpy as np
from openai import OpenAI


class Static_dataGen():
    def __init__(self,key) -> None:
        self.tools_list = open('../resources/Tool_list/tool_list.txt', 'r').read()
        self.sample_query = open('../resources/Tool_list/sample_queries.txt', 'r').read()
        self.sample_query_with_op = open('../resources/Tool_list/sample_queries_with_output.txt', 'r').read()
        self.query_list = []
        self.outputCompletion = []
        self.client = OpenAI(api_key=key) 
        self.no_of_Queries2beGenerated = 0
    
    def genQuery(self, n):
        self.no_of_Queries2beGenerated = math.ceil(n/10)
        for j in range(0, self.no_of_Queries2beGenerated):
            response = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant. You always \
                          strictly adhere to the output format given. You are very creative as well.\
                          You generate outputs which are creatively different from the sample."},

                    {"role": "user", "content": f"Select any 4 tools from {self.tools_list}. Generate\
                          10 queries similar to {self.sample_query} using the tool set, without numbering.\
                          Return the queries in the following format: '''<query>''' "}

                ],
                temperature=0.7,
            )
            query_block = response.choices[0].message.content
            Qr = []
            Qr = re.findall(r"'''(.*?)'''", query_block, re.DOTALL)
            for q in Qr:
                self.query_list.append(q)         
        return self.genOutput()

    def genOutput(self):
        cnt = 0
        while(cnt<self.no_of_Queries2beGenerated*10):
            usrInp = "Answer these queries one by one, making sure to reset to var_1 after\
                  each query. All the var must be printed in seperate lines and print the \
                  output in the following format '''<output>'''\n"
            for i in range(0,10):
                usrInp += f"{i}. {self.query_list[cnt+i-1]}\n"
                completion = self.client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages= [{
                           "role": "system",
                           "content" : f"You are an extremely helpful and extremely faithful chatbot.\
                            You call given functions calls to complete a query. You only know these functions and nothing else: \n{self.tools_list}\n\
                            The only code you know to write is of type 'var_name = function_call(function_argument)'. You never output anything \
                            else other than this format. You follow the sequence of completing query religiously. Here are some sample queries and \
                            their respective responses that I want from you:\n Example output: {self.sample_query_with_op}\n\
                            The user will prompt you with a list of queries similar to the example. Answer very strictly in the same format shown above. \
                            Use indexing for the output.Make sure to mention type wherever relevant when calling works_list. Any missing type arguments is not acceptable.\
                            Don't make unnecessary calls to any functions. When given names make sure to call search_object_by_name() to get work_ids."
                       },
                                  {
                            'role':'user',
                            'content':usrInp
                       }],
                  temperature = 0
                )
            output_blocks = re.findall(r"\'\'\'(.*?)\'\'\'", completion.choices[0].message.content, re.DOTALL)
            for block in output_blocks:
                self.outputCompletion.append(block.strip())
            cnt += 10
        return self.merge()
    
    def merge(self):
        merged_data = [{'Query': query, 'Output': output} for query, output in zip(self.query_list, self.outputCompletion)]
        return merged_data
    

class Dynamic_dataGen():
    def __init__(self,key) -> None:
        self.tools_list = open('../resources/Tool_list/tool_list.txt','r').read()
        self.dyQuGenPrompt = open('../resources/Prompts/DynamicQueryGenPrompt.txt', 'r').read()
        self.dyOpGenPrompt = open('../resources/Prompts/DynamicOutputGenPrompt.txt', 'r').read()
        self.query_list = []
        self.DynamicTool_list = []
        self.outputCompletion = []
        self.added_tools = []
        self.client = OpenAI(api_key=key) 
        self.no_of_Queries2beGenerated = 0

    def genDynamicTools(self, x):
        no_of_tools = math.ceil(x/10)
        for j in range(0, no_of_tools):
            response = self.client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages= [
                        {"role": "system", "content": "You are a helpful assistant. You always strictly adhere to the output format given. You are very creative as well. You generate outputs which are creatively different from the sample."},
                        {"role": "user", "content": f"Here is a list of 9 tools given in a docstring format, each performing a specific function: {self.tools_list}. Select any 3 tools from the list of tools and generate 10 tools similar to the chosen 3 \
                        tools but performing different tasks, without numbering. Keep the tools function simple. Give output in the same format as the tools in the given tool list. Make sure that the argument values doesn't ask for for large files,\
                        but instead asks for something shorter like file IDs. Make sure that the type of parameters is specified and return type is always mentioned in the exact format as in the provided tool list. The return type and type of parameters of the\
                        new functions should be limited to int, str, bool, float, list and None. The generated tools could have default values. Make sure the tool has all the paremeters required for it to achieve that function, even the one it needs to\
                        make a change to. After every tool add three hyphens on the next line. Dont add three hyphens after the last tool."}
                       ],
                temperature=1,
            )
            tool_block = response.choices[0].message.content
            tools2 = tool_block.split('---')
            self.DynamicTool_list.extend(tools2)        
        return 
    
    def genDynamicQueryOutputPair(self, n):
        cnt = 0
        self.no_of_Queries2beGenerated = n
        while(cnt<self.no_of_Queries2beGenerated):
            sec2str = random.sample(self.DynamicTool_list, k=10)
            temp_str = ' '
            for j in sec2str:
                temp_str += j
             
            completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages= [{'role':'system', 'content': 'You are an extremely helpful and faithful assistant. \
                      You stritcly adhere to the output format given. You are very creative and generate \
                      examples similar yet different to the given examples.'},
                      {'role':'user', 'content':f'Given below are 2 sections, each having a docstring\
                      description of tools, its parameters and return type:{self.tools_list}\nSection-2:'+temp_str
                      +self.dyQuGenPrompt}],
            temperature = 0.5
            )
            query = completion.choices[0].message.content
            query = re.sub(r"^\d+\.\s*",'', query)
            self.query_list.append(query)
             
            completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages= [{'role' : 'system', 'content' : 'You are an extremely helpful and extremely faithful\
                      chatbot. You strictly adhere to the output format given.You can only call given functions\
                      calls to complete a query. You only know these functions and nothing else.'},
                       {'role':'user', 'content':f'You call given functions calls to complete a query. You only know\
                         these functions and nothing else:{self.tools_list}'
                         +temp_str+self.dyOpGenPrompt+query}],
            temperature = 0.8
            )
            output = completion.choices[0].message.content
            lines = output.split('\n')
            code_str = '\n'.join(lines[1:])
            self.outputCompletion.append(code_str)
            self.added_tools.append(sec2str)
            cnt=cnt+1
        
        merged_data = [{'Added_Tools':added_tools,'Query': query, 'Output': output} for added_tools, query, output in zip(self.added_tools,self.query_list, self.outputCompletion)]
        return merged_data     

class Bonus_dataGen():
    def __init__(self,key) -> None:
        self.tools_list = open('../resources/Tool_list/tool_list.txt', 'r').read()
        self.extra_tools = open('../resources/Tool_list/bonustools.txt','r').read()
        self.user_prompt_output_content = open('../resources/Prompts/BonusOutputPrompt.txt','r').read()
        self.user_prompt_query_content = open('../resources/Prompts/BonusQueryPrompt.txt','r').read()
        self.query_list = []
        self.outputCompletion = []
        self.client = OpenAI(api_key=key) 
        self.no_of_TimesLoopRuns = 0

    def genBonusQueryOutputPair(self, n):
        self.no_of_TimesLoopRuns = n
        for j in range(0, self.no_of_TimesLoopRuns):
            completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                    {"role": "system", "content": "You are an extremely helpful and faithful assistant. \
                            You strictly adhere to the query format given. You are very creative and generate examples \
                            similar yet different to the given examples. The queries that you generate do not contain \
                            nested if-else statements or nested for loops. The queries should not require if-else statements \
                            inside a for loop. Similarly, the queries should not require for loops inside an if-else statement.\
                            You are given a list of tools and their descriptions. You are given a list of specifications for\
                            the queries that you need to generate."},
                    {"role": "user", "content": f"Given below are 2 sections, each having a docstring description of tools, its \
                            parameters and return type: Section-1: {self.tools_list} \n Section-2: {self.extra_tools} \n \
                            {self.user_prompt_query_content}"}
            ],
            temperature=0.4
            )

            query = completion.choices[0].message.content
            query = re.sub(r"^\d+\.\s*",'', query)
            self.query_list.append(query)
            
            completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages= [
                    {'role' : 'system', 'content' : 'You are an extremely helpful and extremely faithful chatbot.\
                        You strictly adhere to the output format given. You can only call given functions calls to \
                        complete a query. You only know these functions and nothing else.'},
                    {'role':'user', 'content':  f"You call given functions calls to complete a query. You only know these functions \
                        and nothing else: {self.tools_list} \n {self.extra_tools} \n {self.user_prompt_output_content}\n{query}"},
            ],
            temperature = 0.8
            )

            output = completion.choices[0].message.content
            lines = output.split('\n')
            code_str = '\n'.join(lines[1:])
            self.outputCompletion.append(code_str)

        merged_data = [{'Query': query, 'Output': output} for query, output in zip(self.query_list, self.outputCompletion)]
        return merged_data
        
class Preprocessing():
    def __init__(self) -> None:
        self.staticTool_list = [row[0] for row in csv.reader(open('../resources/Tool_list/final-static-toollist.csv', 'r'))]
        self.dynamicTool_list = [row[0] for row in csv.reader(open('../resources/Tool_list/final-dynamic-toolset.csv', 'r'))]

    def p1_static(self, additional_tools=list()):
        used_tools = additional_tools + self.staticTool_list
        used_len = len(used_tools)
        add_len = math.floor(np.random.uniform(0, 18-used_len))
        random_tools = random.sample(self.dynamicTool_list, add_len)
        added_tools = list(set(used_tools + random_tools))
        added_tools = '\n'.join(added_tools)
        return added_tools

    def p1_dynamic(self, additional_tools):
        used_tools = additional_tools + self.staticTool_list
        used_len = len(used_tools)
        add_len = math.floor(np.random.uniform(0, 18-used_len))
        random_tools = random.sample(self.dynamicTool_list, add_len)
        added_tools = list(set(used_tools + random_tools))
        added_tools = '\n'.join(added_tools)
        return added_tools

    def p1_bonus(self, additional_tools):
        used_tools = additional_tools + self.staticTool_list
        added_tools = list(set(used_tools))
        added_tools = '\n'.join(added_tools)
        return added_tools

    def prompt_p2_pipeline(self, query, output, additional_tools=list()):
        len_add = len(additional_tools)
        add_len = math.floor(np.random.uniform(0, 10-len_add))
        random_tools = random.sample(self.dynamicTool_list, add_len)
        added_tools = list(set(additional_tools + random_tools))
        added_tools = '\n'.join(added_tools)
        prompt = f'''
        <s>
        [INST]
        Added Tools: 

        {added_tools}

        Query: {query} [/INST]

        ```
        {output}
        ```
        </s>
        '''
        return prompt
    
    def prompt_p3_pipeline(self, query, output, additional_tools=list()):
        used_tools = additional_tools + self.staticTool_list
        used_len = len(used_tools)
        add_len = math.floor(np.random.uniform(0, 18-used_len))
        random_tools = random.sample(self.dynamicTool_list, add_len)
        allowed_tools = list(set(used_tools + random_tools))
        allowed_tools = '\n'.join(allowed_tools)

        prompt = f'''
        <s>
        [INST]
        Allowed Tools: 

        {allowed_tools}

        Query: {query} [/INST]

        ```
        {output}
        ```
        </s>
        '''
        return prompt


    


         


        

        