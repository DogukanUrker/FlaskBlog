from flask import request, session
from settings import Settings
from utils.log import Log


def browser_language():
    """
    Set the user's language based on the browser's preferred language.

     Parameters:
        None

    Returns:
        None
    """
    if "language" not in session:
        browser_language = request.headers.get("Accept-Language")
        if browser_language:
            browser_language = browser_language.split(",")[0].split("-")[0]
            if browser_language in Settings.LANGUAGES:
                session["language"] = browser_language
                Log.info(f"Browser language detected and set to: {browser_language}")
            else:
                session["language"] = "en"
                Log.warning(
                    f"Browser language '{browser_language}' not supported. Defaulting to English."
                )
        else:
            session["language"] = "en"
            Log.warning("No browser language detected. Defaulting to English.")
    else:
        Log.info(f"Language already set in session: {session['language']}")
