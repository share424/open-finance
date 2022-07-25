import json

def load_config(config_path: str = 'config.json') -> dict:
  with open(config_path, 'r') as f:
    return json.load(f)