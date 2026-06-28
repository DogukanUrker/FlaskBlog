from math import ceil

from flask import Blueprint, render_template, request

from models import Post, User
from utils.log import Log

search_blueprint = Blueprint("search", __name__)


@search_blueprint.route("/search/<query>", methods=["GET", "POST"])
def search(query):
    query = query.replace("%20", " ")
    query_no_white_space = query.replace("+", "")
    query = query.replace("+", " ")

    page = request.args.get("page", 1, type=int)
    per_page = 9

    Log.info(f"Searching for query: {query}")

    query_users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    query_users_no_space = User.query.filter(
        User.username.ilike(f"%{query_no_white_space}%")
    ).all()
    all_users = list(set(query_users + query_users_no_space))

    query_tags = (
        Post.query.filter(Post.tags.ilike(f"%{query}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )
    query_tags_no_space = (
        Post.query.filter(Post.tags.ilike(f"%{query_no_white_space}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )

    query_titles = (
        Post.query.filter(Post.title.ilike(f"%{query}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )
    query_titles_no_space = (
        Post.query.filter(Post.title.ilike(f"%{query_no_white_space}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )

    query_authors = (
        Post.query.filter(Post.author.ilike(f"%{query}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )
    query_authors_no_space = (
        Post.query.filter(Post.author.ilike(f"%{query_no_white_space}%"))
        .order_by(Post.time_stamp.desc())
        .all()
    )

    all_posts_set = set()
    posts_ordered = []

    for post in (
        query_tags
        + query_tags_no_space
        + query_titles
        + query_titles_no_space
        + query_authors
        + query_authors_no_space
    ):
        if post.id not in all_posts_set:
            all_posts_set.add(post.id)
            posts_ordered.append(post)

    empty = not posts_ordered and not all_users

    total_posts = len(posts_ordered)
    total_pages = max(ceil(total_posts / per_page), 1)
    offset = (page - 1) * per_page
    paginated_posts = posts_ordered[offset : offset + per_page]

    posts = [
        [
            (
                p.id,
                p.title,
                p.tags,
                p.content,
                p.banner,
                p.author,
                p.views,
                p.time_stamp,
                p.last_edit_time_stamp,
                p.category,
                p.url_id,
                p.abstract,
            ),
        ]
        for p in paginated_posts
    ]

    users = []
    if all_users:
        users_tuples = [
            (
                u.user_id,
                u.username,
                u.email,
                u.profile_picture,
                u.role,
                u.points,
                u.time_stamp,
                u.is_verified,
            )
            for u in all_users
        ]
        users.append(users_tuples)

    Log.info(
        f"Rendering search.html: params: query={query} | users={len(all_users)} | posts={len(posts)} | empty={empty}"
    )

    return render_template(
        "search.html",
        posts=posts,
        users=users,
        query=query,
        empty=empty,
        page=page,
        total_pages=total_pages,
    )
