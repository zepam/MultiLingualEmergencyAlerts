from openai import AzureOpenAI
from clients.client import Client

# Client to interact with the ChatGPT API via Azure
class ChatGPTClient(Client):
    def __init__(self, key, base_url, deployment_name):
        super().__init__(key)
        self.base_url = base_url
        self.azure_model = "2024-12-01-preview"
        self.deployment_name = deployment_name

    def chat(self, prompt_files, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompts = self.gather_prompts(prompt_files=prompt_files, disaster=disaster, language=language, sending_agency=sending_agency, location=location, time=time, url=url)
        for prompt in prompts:
            client = AzureOpenAI(
            azure_endpoint=self.base_url, 
            api_key=self.key,  
            api_version=self.azure_model
        )

        # roles: system, user, assistant...which one? System?
        response = client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        print(response.choices[0].message.content)

