from flask import render_template


def csrf_error_handler(e):
    """
    Handle CSRF token validation errors.

    Args:
        e: The CSRFError exception object.

    Returns:
        A tuple containing the rendered error template and HTTP status code 400.
    """
    return render_template("csrf_error.html"), 400
