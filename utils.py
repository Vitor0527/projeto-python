import json
import os

## READ JSON FILE

def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

## WRITE JSON FILE

def save_json(filename, data):
    if os.path.isfile(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
