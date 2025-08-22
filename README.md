# Multilingual Emergency Alerts
A toolkit for generating, collecting, and evaluating multilingual emergency alert messages using a variety of large language models (LLMs) and translation APIs.


## Features

- **Automated Response Collection:** Query multiple LLMs and translation services (ChatGPT, Gemini, DeepSeek, Google Translate, DeepL) for emergency alert translations in many languages.
- **Prompt Engineering:** Test and compare different prompt strategies for each service and scenario.
- **Evaluation Suite:** Evaluate generated outputs using metrics such as ROUGE, BLEU, BERTScore, and COMET.
- **Result Aggregation:** Combine and visualize results from multiple runs and services.
- **Extensible:** Easily add new languages, services, or evaluation metrics.

---

## Directory Structure

```python
MultiLingualEmergencyAlerts/

├── clients/ # Service-specific client code and shared translation map
├── data/ # Gold standard/reference data for evaluation
├── prompts/ # Prompt templates for LLMs
├── results/ # Output CSVs and combined results
├── source/ # Utility scripts (e.g., combine_all_results.py)
├── output_file.json # Main output file for collected responses
├── collect_responses.py # Main script to collect responses from all services
├── evaluation.py # Script to evaluate outputs against references
├── plot_results.py # Script to visualize results
├── run_all_evaluations.sh # Shell script to run all evaluations and combine results
├── requirements.txt # Python dependencies
└── README.md # This file
```

---

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd MultiLingualEmergencyAlerts
2. **Install dependencies:**

* Create and activate a Python environment (e.g., with conda or venv).
* Install required packages:
    ```python
    pip install -r requirements.txt
    ```
* Set up API keys. See the README in clients for more info.


## Usage
1. **Collect Multilingual Responses**  
    Run the main collection script to query all services for all languages, disasters, and prompts:
    ```python
    python collect_responses.py
    ```
    * You can skip specific services with flags like --skip_SERVICENAME
  
2. **Evaluate Results**
   Run the main evaluation script:
    ```python
    ./run_all_evaluations.sh
    ```

    This will evaluate the generated outputs against gold standards. This script evaluates all of the services individually as `results/results_SERVICENAME.csv` then combines results into `results/all_results_combined.csv`

## Logging
`output.log` is the log file for collect_resposes.py. This will reset with every run.

`evaluation.log` is the file for evaluations. This will append with every run.

## Extensions

The file `clients/translation_map.py `contains all of the language names and their corresponding language codes for evaluation.

The file `data/evaluation_gold_standards.json` contains all of the gold standards for each language and each prompt.

To add a new language for evaluation:
* add the language name and language code to the translation map.
* add the gold standard results the json 






