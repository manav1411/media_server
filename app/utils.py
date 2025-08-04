import os
import json

def load_progress(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_progress(path, data):
    with open(path, "w") as f:
        json.dump(data, f)
