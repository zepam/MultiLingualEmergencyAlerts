# Scripts Reference

This file lists runnable scripts in this repository, what they do, and what they output.

## Core pipeline

| Script | What it does | Output |
|---|---|---|
| collect_responses.py | Collects multilingual alert responses from configured services (Gemini, ChatGPT, DeepSeek, Google Translate, DeepL). Supports skip flags and output path selection. | Writes responses JSON to output_file.json by default (or --output_file path). Writes run logs to logs/output.log (overwritten each run). Writes warnings/errors summary to logs/errors.log. Prints total execution time to console. |
| evaluation.py | Evaluates generated responses against gold standards using ROUGE, BLEU, BERTScore, COMET, and CHRF metrics, optionally filtered to one service. | Writes evaluation CSV when --output_csv is provided (saved under results/ using the provided filename). Appends logs to logs/evaluation.log. Prints completion info to console. |
| run_all_evaluations.sh | Runs evaluation.py once per service and then combines per-service CSV files. | Creates results/results_google_translate.csv, results/results_chatgpt.csv, results/results_deepseek.csv, results/results_gemini.csv, results/results_deepL.csv, then results/all_results_combined.csv.Prints status lines to console.|

## Utility scripts

| Script | What it does | Output |
|---|---|---|
| source/combine_all_results.py | Merges all results/results*.csv files into one combined CSV (single header). | Writes results/all_results_combined.csv. Prints which files were added. |
| source/count_responses.py | Flattens output JSON into records and computes response-count summaries by service/disaster/language/prompt. | Writes data/counts_service_disaster.csv, data/counts_service_disaster_language.csv, data/counts_service_disaster_language_prompt.csv. Prints total response count and created-file messages. |
| source/reformat_json.py | Normalizes output_file.json entries into a consistent shape for downstream use. | Writes output_file_normalized.json. Prints info/error messages to console. |
| source/validate_json_parse.py | Validates that output_file.json is valid JSON and reports parse location on failure. | Prints OK/ERROR status to console, including line/column caret diagnostics for invalid JSON. Exit code 0 valid, 1 invalid JSON, 2 missing file. |
| source/source_character_counts.py | Counts characters in reference text from data/evaluation_gold_standards.json by language and disaster. | Writes data/source_character_counts.json. Prints completion message to console. |
| source/evaluate_spanish_google_bleu.py | Runs Spanish Google Translate BLEU checks across several tokenizers and per-disaster slices. | Prints overall and per-disaster BLEU scores to console. No file output. |
| source/swift/export_language_codes.py | Exports unique non-English language codes from translation_map. | Writes target_languages.txt. |
| source/swift/export_prompts.py | Extracts English source prompts from gold standards for use in external tooling. | Writes english_sources.json and prints extracted data summary. |

## Shell and scheduler wrappers

| Script | What it does | Output |
|---|---|---|
| source/collect_responses.sh | Thin wrapper that forwards all arguments to collect_responses.py. | Same outputs as collect_responses.py. |
| run_collect_responses.cmd | HTCondor submission file to run collect_responses.py on a cluster worker. | Condor logs: collect_responses.out, collect_responses.err, collect_responses.log. |
| run_all.cmd | HTCondor submission file to run run_all_evaluations.sh on a cluster worker. | Condor logs: all_evals.error, all_evals.log. |
| eval.cmd | HTCondor submission file to run run_all_evaluations.sh. | Condor logs: eval_condor.out, eval_condor.err, eval_condor.log. |
| source/auto_collect_responses.cmd | HTCondor cron submission file for periodic collect_responses.sh execution. | Condor logs: auto_collect_responses.log, auto_collect_responses.err. |
