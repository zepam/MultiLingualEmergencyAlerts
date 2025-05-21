# Evaluate coverage of FCC Multi-Lingual Emergency Alerts

## Setup

To run `collect_responses`, you'll need to configure several environmental variables for API access inside a file called `.env`.

```
GEMINI_API_KEY=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_DEPLOYMENT_NAME=""
OPENROUTER_API_KEY=""
```

### Google setup

Gemini and Google Translate are accessed via Google. 

1) Enable the Cloud Translation API in your project
1) Download the gcloud CLI (https://cloud.google.com/sdk/docs/install)
2) Run `gcloud init`
3) Run `gcloud auth application-default login` to set up your credentials. This will save a credentials file in a set location based on your OS (https://cloud.google.com/translate/docs/authentication#user-credentials-adc)
4) (If needed; gcloud init will generally handle this for you) Get your project ID and set a billing quota (https://cloud.google.com/docs/authentication/troubleshoot-adc#user-creds-client-based); make sure your user has an IAM role for "service usage" (https://cloud.google.com/docs/authentication/troubleshoot-adc)

### Microsoft Azure setup

ChatGPT is accessed via Azure.

1) Go to the Azure AI Foundry and deploy an instance of GPT-4o; I did "global standard" as the deployment option as it seemed to be the only one I could with my quota and chose version "2024-12-01-preview". Whichever name you choose for this deployment needs to go in `AZURE_DEPLOYMENT_NAME`
2) Once it deploys, you should see your endpoint and API key. These are your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`.

### DeepSeek setup

Sign up to OpenRouter and create an API key: https://openrouter.ai/settings/keys