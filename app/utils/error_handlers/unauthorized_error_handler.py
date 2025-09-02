from flask import render_template
from utils.log import Log


def unauthorized_error_handler(e):
    """
    Handle 401 Unauthorized errors.

    Args:
        e: The 401 error exception object.

    Returns:
        A tuple containing the rendered error template and HTTP status code 401.
    """
    Log.error(f"401 Unauthorized: {str(e)}")
    return render_template("unauthorized.html"), 401
