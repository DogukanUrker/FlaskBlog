from json import load
from os.path import exists

from utils.log import Log


def load_translations(language):
    """
    Load the translations for the specified language.

    Paremters:
        language (str): The language code for the translations to be loaded.

    Returns:
        dict: A dictionary containing the translations for the specified language.
    """

    file = f"./translations/{language}.json"
    if exists(file):
        with open(file, "r", encoding="utf-8") as file:
            translations = load(file)
            Log.info(f"Loaded translations for language: {language}")
            return translations
    Log.warning(f"Translation file not found: {language}")
    return {}
