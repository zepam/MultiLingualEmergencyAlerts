import json
import pandas as pd

def collect_entries(service, language, disaster, node, prompt=None):
    """
    Recursively collect entries from a JSON node.
    node can be:
        - a list of dicts (entries)
        - a dict with further nesting (like prompt files)
    """
    records = []
    if isinstance(node, list):
        for entry in node:
            if isinstance(entry, dict):
                records.append({
                    "service": service,
                    "language": language,
                    "disaster": disaster,
                    "prompt": prompt,
                    "text": entry.get("text"),
                    "date": entry.get("date")
                })
            else:
                records.append({
                    "service": service,
                    "language": language,
                    "disaster": disaster,
                    "prompt": prompt,
                    "text": entry,
                    "date": None
                })
    elif isinstance(node, dict):
        for key, value in node.items():
            new_prompt = key if isinstance(value, list) else prompt
            records.extend(collect_entries(service, language, disaster, value, new_prompt))
    return records

# Load JSON
with open("output_file.json", "r") as f:
    data = json.load(f)

all_records = []

# Traverse JSON
for service, langs in data.items():
    for language, disasters in langs.items():
        for disaster, node in disasters.items():
            all_records.extend(collect_entries(service, language, disaster, node))

# Convert to DataFrame
df = pd.DataFrame(all_records)

# 1️⃣ Counts per Service × Disaster
counts_service_disaster = df.groupby(["service", "disaster"]).size().reset_index(name="count")
counts_service_disaster.to_csv("./data/counts_service_disaster.csv", index=False)

# 2️⃣ Counts per Service × Disaster × Language
counts_service_disaster_lang = df.groupby(["service", "disaster", "language"]).size().reset_index(name="count")
counts_service_disaster_lang.to_csv("./data/counts_service_disaster_language.csv", index=False)

# 3️⃣ Counts per Service × Disaster × Language × Prompt
counts_service_disaster_lang_prompt = df.groupby(["service", "disaster", "language", "prompt"]).size().reset_index(name="count")
counts_service_disaster_lang_prompt.to_csv("./data/counts_service_disaster_language_prompt.csv", index=False)

print("CSV files created:")
print(" - counts_service_disaster.csv")
print(" - counts_service_disaster_language.csv")
print(" - counts_service_disaster_language_prompt.csv")

# Total number of responses
total_responses = len(df)
print(f"Total number of responses: {total_responses}\n")
