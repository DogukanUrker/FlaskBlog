from json import load
from os.path import exists, abspath

from utils.log import Log

# 硬编码一个最小化的翻译字典，确保关键功能可用
MINIMAL_TRANSLATIONS = {
    "history": {
        "title": "Browsing History",
        "viewedAt": "Viewed at:",
        "postedAt": "Posted at:",
        "editedAt": "Edited at:",
        "noHistoryTitle": "No browsing history yet",
        "noHistoryMessage": "You haven't viewed any posts recently. Start exploring to build your history.",
        "explorePosts": "Explore Posts"
    },
    "searchBar": {
        "placeholder": "Search posts..."
    }
}

def loadTranslations(language):
    """
    Load the translations for the specified language.

    Paremters:
        language (str): The language code for the translations to be loaded.

    Returns:
        dict: A dictionary containing the translations for the specified language.
    """
    # 使用绝对路径以确保正确加载翻译文件
    translationFile = abspath(f"./translations/{language}.json")
    Log.info(f"Attempting to load translation file: {translationFile}")
    
    # 始终返回包含最小化翻译的字典，确保关键功能可用
    result = MINIMAL_TRANSLATIONS.copy()
    
    try:
        if exists(translationFile):
            try:
                with open(translationFile, "r", encoding="utf-8") as file:
                    translations = load(file)
                    Log.info(f"Loaded translations for language: {language}")
                    # 将加载的翻译合并到结果中，保留已存在的键
                    result.update(translations)
            except Exception as e:
                Log.error(f"Error loading translation file {translationFile}: {str(e)}")
        else:
            Log.warning(f"Translation file not found: {translationFile}")
            # 尝试回退到英文翻译
            if language != 'en':
                Log.info(f"Attempting to load English translations as fallback")
                en_translationFile = abspath("./translations/en.json")
                if exists(en_translationFile):
                    try:
                        with open(en_translationFile, "r", encoding="utf-8") as file:
                            en_translations = load(file)
                            Log.info("Loaded English translations as fallback")
                            result.update(en_translations)
                    except Exception as e:
                        Log.error(f"Error loading English translation file: {str(e)}")
    except Exception as e:
        Log.error(f"Unexpected error in loadTranslations: {str(e)}")
    
    # 确保history键存在
    if 'history' not in result:
        result['history'] = MINIMAL_TRANSLATIONS['history']
        Log.warning("Using minimal history translations")
    
    return result
