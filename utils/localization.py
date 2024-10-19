import json
import os

def load_translations(language_code):
    try:
        filepath = os.path.join('locales', f'messages_{language_code}.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        filepath = os.path.join('locales', 'messages_en.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
