# Evaluate coverage of FCC Multi-Lingual Emergency Alerts

## Setup

Install all the libraries in requirements.txt: `pip install -r requirements.txt`.

Then you'll need to configure several environmental variables for API access inside a file called `.env`.

```
GEMINI_API_KEY=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_DEPLOYMENT_NAME=""
OPENROUTER_API_KEY=""
```

### Google

Gemini and Google Translate are accessed via Google. 

1) Enable the Cloud Translation API in your project
1) Download the gcloud CLI (https://cloud.google.com/sdk/docs/install)
2) Run `gcloud init`
3) Run `gcloud auth application-default login` to set up your credentials. This will save a credentials file in a set location based on your OS (https://cloud.google.com/translate/docs/authentication#user-credentials-adc)
4) (If needed; gcloud init will generally handle this for you) Get your project ID and set a billing quota (https://cloud.google.com/docs/authentication/troubleshoot-adc#user-creds-client-based); make sure your user has an IAM role for "service usage" (https://cloud.google.com/docs/authentication/troubleshoot-adc)

### Microsoft Azure

ChatGPT is accessed via Azure.

1) Go to the Azure AI Foundry (https://ai.azure.com) and deploy an instance of GPT-4o; I did "global standard" as the deployment option as it seemed to be the only one I could with my quota and chose version "2024-12-01-preview". Whichever name you choose for this deployment needs to go in `AZURE_DEPLOYMENT_NAME`
2) Once it deploys, you should see your endpoint and API key. These are your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`.

### OpenRouter

DeepSeek is accessed via OpenRouter.

Sign up to OpenRouter and create an API key: https://openrouter.ai/settings/keys

## Running the Script

`collect_responses.py` supports several arguments:

You can choose to skip calling certain API endpoints with the following bools:

- `--skip_gemini`

- `--skip_chatgpt`

- `--skip_deepseek`

- `--skip_google_translate`

You can `tail -f output.log` to keep an eye on how things are running.

## Known Rate Limits
OpenRouter allows 50 free requests per day.

Gemini rate limits to 10 requests per minute.

The `collect_responses.py` script will automatically stop bugging a given endpoint if 3 consecutive requests fail.

## Evaluation
```
./run_all_evaluations
```
This will evaluate the generated outputs against gold standards. This script evaluates all of the services individually as `results/results_SERVICENAME.csv` then combines results into `results/all_results_combined.csv`

## Prompts
All prompts can be found in `/prompts`. {LANGUAGE} and {DISASTER} variables are replaced during run-time before sending the prompt to the service.

## Images
Contains charts of our demographic analysis for language needs in Washington state.

## Clients
These are objects used to interact with the various service APIs. Each client inherits from a base Client object.

## Translation Map
This contains all the languages that will be used as the target language. Additional languages may be added to the evaluation stream in this file by including the lowercase language name and [language code](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).
