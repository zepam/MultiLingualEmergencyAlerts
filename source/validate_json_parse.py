import json

with open("/home/jen/MultiLingualEmergencyAlerts/output_file.json", "r", encoding="utf-8") as f:
    json.load(f)   # raises json.JSONDecodeError if braces/brackets don't match

print("OK: JSON parses (all objects/braces are properly closed)")