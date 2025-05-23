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

1) Go to the Azure AI Foundry and deploy an instance of GPT-4o; I did "global standard" as the deployment option as it seemed to be the only one I could with my quota and chose version "2024-12-01-preview". Whichever name you choose for this deployment needs to go in `AZURE_DEPLOYMENT_NAME`
2) Once it deploys, you should see your endpoint and API key. These are your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`.

### OpenRouter

DeepSeek is accessed via OpenRouter.

Sign up to OpenRouter and create an API key: https://openrouter.ai/settings/keys

## Running the Script

`collect_responses.py` supports several arguments:

- `--output_file`: specify the file to write to. It will be a JSON object of the responses.

- `--total_responses`: the number of responses to collect per service. The script will loop until all are collected or it can't collect anymore (API errors, rate limiting, etc.)

- `--preserve_output`: if a matching output file exists, read in the existing data and append to it. Useful when combatting rate limits

You can also choose to skip calling certain API endpoints with these bools:

- `--skip_gemini`

- `--skip_chatgpt`

- `--skip_deepseek`

- `--skip_google_translate`

You can `tail -f output.log` to keep an eye on how things are running.

## Known Rate Limits
OpenRouter allows 50 free requests per day.

Gemini rate limits to 10 requests per minute.
