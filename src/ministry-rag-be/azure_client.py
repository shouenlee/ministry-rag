import os
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Load environment variables from .env file
load_dotenv()

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default")


class AzureClient:
    def __init__(self):
        self.client = self.get_azure_client()
        #self.client = OpenAI()
        
    def get_azure_client(self):
        return AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_GPT_ENDPOINT"),
            #azure_ad_token_provider=token_provider,
            api_key=os.getenv("AZURE_GPT_API_KEY"),
            api_version="2023-03-15-preview"
            )
    
    def get_completion(self, question: str, context: list):
        system_prompt, user_prompt = self.generate_prompt(question, context)
        #print(prompt)
        
        completion = self.client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT"),
        messages= [
        {
            "role": "user",
            "content": user_prompt
        },
        {
            "role": "system",
            "content": system_prompt
        }],
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
        )  
        '''
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello world"}]
        )
        '''
        return completion.choices[0].message.content

    def generate_prompt(self, question: str, context: list) -> str:
        formatted_context = ""
        for i, c in enumerate(context):
            formatted_context += f"Context {i}: {c}\n"
        user_prompt = f"The user asks: '{question}'"
        system_prompt = f"You are a chatbot with the task of answering the user's questions with only the context information provided and no other information. \
            All the context information comes from a set of spoken messages compiled into the Life-Study of the Bible. \
            You must include all references of the contexts used to answer the question in your response in natural language using parentheses (). For example, if the reference is '..\\..\\Data\\Life-study_of_Galatians\\Life-study_of_Galatians_30.txt' then you should cite 'Life-study of Galatians message 30'. \
            The context is: \n {formatted_context}"

        return (system_prompt, user_prompt)