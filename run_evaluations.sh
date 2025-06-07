#!/bin/bash

# Script to run evaluation.py twice with hard-coded arguments

echo "Running first evaluation..."
python evaluation.py output_file.json evaluation_gold_standards.json --output_csv results.csv --no_bertscore

echo "Running second evaluation..."
python evaluation.py -output_file.json evaluation_gold_standards.json --output_csv results.csv --no_comet

echo "Evaluations completed."
