#!/bin/bash



# Script to run Google Translate evaluation

echo "Evaluating google translate results..."
python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_google_translate.csv --service_name google_translate

# Script to run ChatGPT evaluation

echo "Evaluating chatgpt results..."
python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_chatgpt.csv --service_name chatgpt

# Script to run Deepseek evaluation

echo "Evaluating deepseek results..."
python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_deepseek.csv --service_name deepseek

# Script to run Gemini evaluation

echo "Evaluating gemini results..."
python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_gemini.csv --service_name gemini

# Script to run Gemini evaluation

echo "Evaluating deepL results..."
python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_deepL.csv --service_name deepL

# Combine all results

echo "Combining files..."
python source/combine_all_results.py

