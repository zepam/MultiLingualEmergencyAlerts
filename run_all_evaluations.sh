#!/bin/bash

echo "Beginning evaluations..."

# Script to run Google Translate evaluation

python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_google_translate.csv --service_name google_translate

# Script to run ChatGPT evaluation

python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_chatgpt.csv --service_name chatgpt

# Script to run Deepseek evaluation

python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_deepseek.csv --service_name deepseek

# Script to run Gemini evaluation

python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_gemini.csv --service_name gemini

