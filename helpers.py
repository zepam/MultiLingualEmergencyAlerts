import os
from clients.gemini import GeminiClient
from clients.deepseek import DeepSeekClient
from clients.chatgpt import ChatGPTClient
from clients.cloud_translation import GoogleCloudTranslationClient

def chat_gemini(language, disaster, prompt):
  gemini_client = GeminiClient(key=os.getenv("GEMINI_API_KEY"))
  return gemini_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_deepseek(language, disaster, prompt):
  deepseek_client = DeepSeekClient(key=os.getenv("OPENROUTER_API_KEY"))
  return deepseek_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_chatgpt(language, disaster, prompt):
  chatgpt_client = ChatGPTClient(key=os.getenv("AZURE_OPENAI_API_KEY"), base_url=os.getenv("AZURE_OPENAI_ENDPOINT"), deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"))
  return chatgpt_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_google_translate(language, disaster, prompt):
  google_translate_client = GoogleCloudTranslationClient()
  return google_translate_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def generate_output_schema():
  return {
    "chatgpt": {
      "spanish": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "haitian_creole": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "vietnamese": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "arabic": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "mandarin": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      }
    },
    "gemini": {
      "spanish": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "haitian_creole": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "vietnamese": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "arabic": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "mandarin": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      }
    },
    "deepseek": {
      "spanish": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "haitian_creole": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "vietnamese": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "arabic": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      },
      "mandarin": {
        "flood": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "extreme_wind": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "fire": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "boil_water_notice": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        },
        "911 outage": {
          "prompt_simple.txt": [],
          "prompt_persona.txt": [],
          "prompt_one_shot.txt": [],
          "prompt_cross_lingual_alignment.txt": [],
          "prompt_chain_of_translation.txt": []
        }
      }
    },
    "google_translate": {
      "spanish": { 
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "arabic": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "mandarin": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "vietnamese": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "haitian_creole": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      }
    }
  }