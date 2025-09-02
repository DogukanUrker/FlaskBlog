from utils.get_profile_picture import get_profile_picture


def return_user_profile_picture():
    """
    Returns a dictionary with the user's profile picture.

    Returns:
        dict: A dictionary containing the user's profile picture.
    """

    return dict(get_profile_picture=get_profile_picture)
