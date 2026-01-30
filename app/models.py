from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from database import db
from utils.time import current_time_stamp


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.Text)
    role = db.Column(db.Text, default="user")
    points = db.Column(db.Integer, default=0)
    time_stamp = db.Column(db.Integer, default=current_time_stamp)
    is_verified = db.Column(db.Text, default="False")

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    banner = db.Column(db.LargeBinary, nullable=False)
    author = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    time_stamp = db.Column(db.Integer, default=current_time_stamp)
    last_edit_time_stamp = db.Column(db.Integer)
    category = db.Column(db.Text, nullable=False)
    url_id = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.Text, nullable=False, default="")

    comments = db.relationship(
        "Comment",
        backref="post",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def hot_score(self):
        age_hours = (current_time_stamp() - self.time_stamp) / 3600
        gravity = 1.8
        return (self.views or 0) / ((age_hours + 2) ** gravity)

    @hot_score.expression
    def hot_score(cls):
        age_hours = (func.strftime("%s", "now") - cls.time_stamp) / 3600.0
        gravity = 1.8
        return func.coalesce(cls.views, 0) / func.pow(age_hours + 2, gravity)

    def __repr__(self):
        return f"<Post {self.title}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"))
    comment = db.Column(db.Text)
    username = db.Column(db.Text)
    time_stamp = db.Column(db.Integer, default=current_time_stamp)

    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id}>"


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"))
    time_stamp = db.Column(db.Integer, default=current_time_stamp)

    # 确保每个用户对每篇文章只能收藏一次
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

    def __repr__(self):
        return f"<Bookmark user_id={self.user_id} post_id={self.post_id}>"
