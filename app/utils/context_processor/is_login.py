from settings import Settings


def is_login():
    """
    Returns a dictionary with a constant login is enabled or not.

    Returns:
        dict: A dictionary with a constant login is enabled or not.
    """

    return dict(is_login=Settings.LOG_IN)
