from settings import Settings


def socialSharing():
    """
    Returns social sharing configuration for templates.

    Returns:
        dict: A dictionary with social sharing settings (enabled, URL, icon).
    """

    return dict(
        shareEnabled=Settings.SHARE_ENABLED,
        shareUrl=Settings.SHARE_URL,
        shareIcon=Settings.SHARE_ICON
    )
