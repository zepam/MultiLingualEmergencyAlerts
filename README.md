# Evaluate coverage of FCC Multi-Lingual Emergency Alerts

## Setup

To run `collect_responses`, you'll need to configure several environmental variables for API access inside a file called `.env`.

```
GEMINI_API_KEY="" # https://aistudio.google.com/app/apikey
VERTEX_AI_PROJECT_ID="" # https://cloud.google.com/vertex-ai?hl=en
```

### Google setup

Claude and Google Translate are accessed via Google. Download the gcloud CLI (https://cloud.google.com/sdk/docs/install) and then run `gcloud init`, `gcloud auth application-default login` to set up your credentials.