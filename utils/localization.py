import json
import os

# Load the messages based on the selected language from the 'locales' folder
def load_messages(language_code):
    try:
        filepath = os.path.join('locales', f'messages_{language_code}.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English if the file is not found
        filepath = os.path.join('locales', 'messages_en.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
