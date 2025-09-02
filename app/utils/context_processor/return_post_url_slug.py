from utils.generate_url_id_from_post import get_slug_from_post_title


def return_post_url_slug():
    def url_slug(title):
        return get_slug_from_post_title(title)

    return dict(url_slug=url_slug)
