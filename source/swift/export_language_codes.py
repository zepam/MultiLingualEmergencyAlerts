from clients.translation_map import TRANSLATION_MAP

# Get all unique language codes except English
codes = set(TRANSLATION_MAP.values()) - {"en"}

with open("target_languages.txt", "w", encoding="utf-8") as f:
    for code in sorted(codes):
        f.write(f"{code}\n")