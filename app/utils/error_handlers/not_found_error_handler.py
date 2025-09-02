from flask import render_template
from utils.log import Log


def not_found_error_handler(e):
    """
    Handle 404 Not Found errors.

    Args:
        e: The 404 error exception object.

    Returns:
        A tuple containing the rendered error template and HTTP status code 404.
    """
    Log.error(f"404 Not Found: {str(e)}")
    return render_template("not_found.html"), 404
