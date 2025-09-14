import json

with open("data/evaluation_gold_standards.json", "r", encoding="utf-8") as f:
    data = json.load(f)

language = "english"
sources = {}

if language in data:
    for disaster, content in data[language].items():
        if "source" in content:
            sources[disaster] = content["source"]

# Save to a new JSON file
with open("english_sources.json", "w", encoding="utf-8") as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

print("Extracted sources:", sources)
