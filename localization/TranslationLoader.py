import json
import os


class TranslationLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationLoader, cls).__new__(cls)
            cls._instance.translations = {}
        return cls._instance

    def load_translations(self, language_code):
        if language_code not in self.translations:
            try:
                filepath = os.path.join('locales', f'messages_{language_code}.json')
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.translations[language_code] = json.load(f)
            except FileNotFoundError:
                print(f'messages_{language_code}.json is not found')
            except Exception as e:
                print(f"error: {e}")

    def get_translation(self, keyword, language_code):
        try:
            self.load_translations(language_code)
            return self.translations.get(language_code, {}).get(keyword, keyword)
        except Exception as e:
            print(f"error: {e}")
            return keyword
