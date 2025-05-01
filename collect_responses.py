import os
from dotenv import load_dotenv
from clients.gemini import GeminiClient

from google.cloud import translate_v2 as translate
from openai import AzureOpenAI
from openai import OpenAI

if __name__ == "__main__":
  load_dotenv()

  gemini_client = GeminiClient(key=os.getenv("GEMINI_API_KEY"))
  gemini_client.chat(
    prompt_files=["prompts/prompt_simple.txt"],
    language="Spanish",
    disaster="tornado"
  )



  """
  # Google translate test
  translate_client = translate.Client()
  input_text = "Hello world!"

  if isinstance(input_text, bytes):
      text = input_text.decode("utf-8")

  # Text can also be a sequence of strings, in which case this method
  # will return a sequence of results for each text.
  # See https://g.co/cloud/translate/v2/translate-reference#supported_languages
  result = translate_client.translate(input_text, target_language="es")

  print("Text: {}".format(result["input"]))
  print("Translation: {}".format(result["translatedText"]))
  print("Detected source language: {}".format(result["detectedSourceLanguage"]))
  """


  # Deepseek
  """
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ]
  )
  gcloud auth application-default print-access-token

  print(completion.choices[0].message.content)
  """

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