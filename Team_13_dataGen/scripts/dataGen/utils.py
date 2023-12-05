import toolslist as tl
from openai import OpenAI

class Static_dataGen():
    def __init__(self) -> None:
        self.tools_list = tl.tool()
        self.sample_query = tl.query()
        self.query_list = []
        self.client = OpenAI() 
    
    def genQuery(self, n):
        for j in range(0, n):
            response = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant. You always \
                     strictly adhere to the output format given. You are very creative as well. \
                     You generate outputs which are creatively different from the sample."},

                    {"role": "user", "content": f"Select any 4 tools from {self.tools_list}. Generate \
                     10 queries similar to {self.sample_query} using the tool set, without numbering."}

                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            
            self.query_list.append(content)


        

        