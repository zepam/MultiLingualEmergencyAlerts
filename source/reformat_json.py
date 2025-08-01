import json
import os

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error in {path}: {e}")
        return {}

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Saved normalized JSON to: {path}")

def normalize_entry(entry):
    if isinstance(entry, str):
        return {"message": entry, "collected_at": None}
    elif isinstance(entry, dict) and "message" in entry and "collected_at" in entry:
        return entry
    else:
        return entry  # Could be malformed or already structured differently

def normalize_deep(data):
    if isinstance(data, dict):
        return {k: normalize_deep(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_entry(e) for e in data]
    else:
        return data

def main():
    input_path = "output_file.json"
    output_path = "output_file_normalized.json"

    if not os.path.exists(input_path):
        print(f"[ERROR] Input file '{input_path}' does not exist.")
        return

    print(f"[INFO] Loading: {input_path}")
    data = load_json(input_path)

    print("[INFO] Normalizing entries...")
    normalized = normalize_deep(data)

    print(f"[INFO] Saving output to: {output_path}")
    save_json(normalized, output_path)

if __name__ == "__main__":
    main()
