from settings import Settings


def is_registration():
    """
    Returns a dictionary with a constant registration is enabled or not.

    Returns:
        dict: A dictionary with a constant registration is enabled or not.
    """

    return dict(is_registration=Settings.REGISTRATION)
