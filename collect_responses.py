import os
from dotenv import load_dotenv
from google import genai
from anthropic import AnthropicVertex
from google.cloud import translate_v2
from openai import AzureOpenAI
from openai import OpenAI

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")

# Gemini test
""" client = genai.Client(api_key=gemini_key)
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text) """

"""
# Claude test via Vertex AI
# https://docs.anthropic.com/en/api/claude-on-vertex-ai
# This can't be used with the free $300 trial. Maybe the $50 student credits?
LOCATION="us-east5"
client = AnthropicVertex(region=LOCATION, project_id=os.getenv("VERTEX_AI_PROJECT_ID"))

message = client.messages.create(
 max_tokens=1024,
 messages=[
   {
     "role": "user",
     "content": "Send me a recipe for banana bread.",
   }
 ],
 model="claude-3-7-sonnet@20250219"
)
print(message.model_dump_json(indent=2))
"""

# Google translate test

# Deepseek
# Deepseek directly costs money... try OpenRouter. 50 free requests a day? https://openrouter.ai/deepseek/deepseek-chat-v3/api
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)

# ChatGPT via Azure
"""
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

response = client.chat.completions.create(
    model="gpt-4o", # model = "deployment_name".
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}
    ]
)

print(response.choices[0].message.content)
"""