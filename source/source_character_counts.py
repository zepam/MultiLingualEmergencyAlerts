import json
"""
Calculate and output character counts for reference texts by language and disaster type.

This script reads evaluation gold standards data from a JSON file, counts the characters 
in reference texts for each language and disaster type, and writes the results to a new JSON file.

Input:
    - JSON file containing evaluation gold standards with reference texts organized by language and disaster type

Output:
    - JSON file with character counts for reference texts by language and disaster type

Note:
    The code for counting source characterscan be uncommented if needed.
"""

input_file = "data/evaluation_gold_standards.json"
output_file = "data/source_character_counts.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

char_counts = {}
for language in data:
    char_counts[language] = {}
    for disaster, content in data[language].items():
        char_counts[language][disaster] = {}
        # if "source" in content:
        #     char_counts[language][disaster]["source"] = len(content["source"])
        if "reference" in content:
            char_counts[language][disaster]["reference"] = len(content["reference"])

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(char_counts, f, ensure_ascii=False, indent=2)

print(f"Character counts for 'source' and 'reference' by language written to {output_file}")
