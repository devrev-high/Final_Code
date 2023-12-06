from openai import OpenAI
import random
import re

class Static_dataGen():
    def __init__(self,key) -> None:
        self.tools_list = open('/home/mayanksony/scripts/dataGen/tool_list.txt', 'r').read()
        self.sample_query = open('/home/mayanksony/scripts/dataGen/sample_queries.txt', 'r').read()
        self.query_list = []
        self.outputCompletion = []
        self.client = OpenAI(api_key=key) 
        self.no_of_Queries2beGenerated = 0
    
    def genQuery(self, n):
        self.no_of_Queries2beGenerated = round(n/10)*10
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
            content = response.choices[0].message.content
            query = []
            query = re.findall(r"'''(.*?)'''", content, re.DOTALL)
            for q in query:
                self.query_list.append(q)         
        return self.genOutput()

    def genOutput(self):
        cnt = 0
        while(cnt<self.no_of_Queries2beGenerated):
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
                            their respective responses that I want from you:\n Example output: {self.sample_query}\n\
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
        self.tools_list = open('/home/mayanksony/scripts/dataGen/tool_list.txt', 'r').read()
        self.sample_query = open('/home/mayanksony/scripts/dataGen/sample_queries.txt', 'r').read()
        self.query_list = []
        self.DynamicTool_list = []
        self.outputCompletion = []
        self.client = OpenAI(api_key=key) 
        self.no_of_Queries2beGenerated = 0

    def genDynamicTools(self):
        
        for j in range(0, 100):
            response = self.client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages= [
                        {"role": "system", "content": "You are a helpful assistant. You always strictly adhere to the output format given. You are very creative as well. You generate outputs which are creatively different from the sample."},
                        {"role": "user", "content": f"Here is a list 10 tools given in a docstring format, each performing a specific function: {self.tools_list}. Select any 3 tools from the list of tools and generate 10 tools similar to the chosen 4 \
                        tools but performing different tasks, without numbering. Keep the tools function simple. Give output in the same format as the tools in the given tool list. Make sure that the argument values doesn't ask for for large files,\
                        but instead asks for something shorter like file IDs. Make sure that the type of parameters is and return type is always mentioned in the exact format as in the provided tool list. The return type and type of parameters of the\
                        new functions should be limited to int, str, bool, float, list and None. The generated tools could have default values. Make sure the tool has all the paremeters required for it to achieve that function, even the one it needs to\
                        make a change to. After every tool add three hyphens on the next line. Dont add three hyphens after the last tool."}
                       ],
                temperature=1,
            )
            content = response.choices[0].message.content
            tools2 = content.split('---')
            self.DynamicTool_list.extend(tools2)        
        return 
    
    def genDynamicQueryOutputPair(self):
        cnt = 0
        while(cnt<self.no_of_Queries2beGenerated):
             sec2str = random.sample(self.DynamicTool_list, k=10)
             temp_str = ' '
             for j in sec2str:
                temp_str += j
             
             completion = self.client.chat.completions.create(
             model="gpt-4-1106-preview",
            messages= [sys_prompt_query,
            {'role':'user', 'content':user_prompt_content_1+temp_str+user_prompt_content_3+user_prompt_content_4_20}],
            temperature = 0.5
            )
             queries = completion.choices[0].message.content
             completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages= [sys_prompt_query,
            {'role':'user', 'content':user_prompt_output_content_1+temp_str+user_prompt_output_content_3+queries}],
            temperature = 0.8
            )

             output = completion.choices[0].message.content
             cnt=cnt+1


    

        


    


         


        

        