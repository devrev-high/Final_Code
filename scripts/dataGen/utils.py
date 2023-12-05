from toolslist import tool, query, outputMessage
from openai import OpenAI

class Static_dataGen():
    def __init__(self) -> None:
        self.tools_list = tool()
        self.sample_query = query()
        self.outputMessage = outputMessage()
        self.query_list = []
        self.client = OpenAI() 
        self.no_of_Queries2beGenerated = 0
    
    def genQuery(self, n):
        self.no_of_Queries2beGenerated = n

        for j in range(0, self.no_of_Queries2beGenerated):
            response = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant. You always \
                          strictly adhere to the output format given. You are very creative as well.\
                          You generate outputs which are creatively different from the sample."},

                    {"role": "user", "content": f"Select any 4 tools from {self.tools_list}. Generate\
                          10 queries similar to {self.sample_query} using the tool set, without numbering.\
                          Return the queries in the following format: '''<queries>''' "}

                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            self.query_list.append(content)
        return

    def genOutput(self):

        cnt10 = 0
        newans = [] 

        while(cnt10<=self.no_of_Queries2beGenerated):
            usrInp = "Answer these queries one by one, making sure to reset to var_1 after\
                  each query. Give a empty line as well between queries.\n"
            for i in range(1,21):
                usrInp += f"{i}. {self.query_list[cnt10+i-1]}\n"
                completion = self.client.chat.completions.create(
                       model="gpt-4-1106-preview",
                       messages= [self.outputMessage,{
                                       'role':'user',
                                      'content':usrInp
            }],
                  temperature = 0
                )
            newans.append(completion.choices[0].message.content)
            cnt10+=10
         


        

        