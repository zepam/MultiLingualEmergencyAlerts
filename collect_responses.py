import os
from dotenv import load_dotenv
from google import genai
from anthropic import AnthropicVertex
from google.cloud import translate_v2

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")

# Gemini test
client = genai.Client(api_key=gemini_key)
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)


# Claude test via Vertex AI
"""
https://docs.anthropic.com/en/api/claude-on-vertex-ai
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

# ChatGPT via Azure
