from openai import AzureOpenAI
from clients.client import Client

# Client to interact with the ChatGPT API via Azure
class ChatGPTClient(Client):
    def __init__(self, key, base_url, deployment_name, logger):
        super().__init__(key, logger)
        self.base_url = base_url
        self.azure_model = "2024-12-01-preview"
        self.deployment_name = deployment_name

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language,
                                    sending_agency=sending_agency, location=location, time=time, url=url)
        client = AzureOpenAI(azure_endpoint=self.base_url, 
                             api_key=self.key,  
                             api_version=self.azure_model)

        response = client.chat.completions.create(model=self.deployment_name,
                                                  messages=[
                                                    {"role": "user", "content": prompt}
                                                  ],
                                                  temperature=self.temperature,
                                                  max_tokens=self.max_tokens,
                                                  top_p=self.top_p)

        return response.choices[0].message.content

