"""
Author: share424

Helper functions
"""

import json

def parse_int(value: str) -> int:
    '''Return int value of string'''
    try:
        return int(value)
    except ValueError:
        return 0

def load_config() -> dict:
    '''Return config data'''
    with open('config.json', 'r', encoding="utf-8") as file:
        return json.load(file)
