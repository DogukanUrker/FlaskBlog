from utils.get_post_url_id_from_post import get_post_url_id_from_post


def return_post_url_id():
    def url_id(title, content):
        return get_post_url_id_from_post(title, content)

    return dict(url_id=url_id)
