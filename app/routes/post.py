import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from settings import Settings
from utils.addPoints import addPoints
from utils.calculateReadTime import calculateReadTime
from utils.delete import Delete
from utils.flashMessage import flashMessage
from utils.forms.CommentForm import CommentForm
from utils.generateUrlIdFromPost import getSlugFromPostTitle
from utils.getDataFromUserIP import getDataFromUserIP
from utils.log import Log
from utils.time import currentTimeStamp

postBlueprint = Blueprint("post", __name__)


@postBlueprint.route("/post/<urlID>", methods=["GET", "POST"])
@postBlueprint.route("/post/<slug>-<urlID>", methods=["GET", "POST"])
def post(urlID=None, slug=None):
    form = CommentForm(request.form)

    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    cursor.execute("select urlID, title from posts where urlID = ?", (urlID,))
    posts = cursor.fetchone()

    if str(urlID) in posts:
        postSlug = getSlugFromPostTitle(posts[1])

        if slug != postSlug:
            return redirect(url_for("post.post", urlID=urlID, slug=postSlug))

        Log.success(f'post: "{urlID}" loaded')

        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        cursor.execute(
            """select * from posts where urlID = ? """,
            [(urlID)],
        )
        post = cursor.fetchone()

        cursor.execute(
            """update posts set views = views+1 where id = ? """,
            [(post[0])],
        )
        connection.commit()

        # Record user history if user is logged in
        if 'userName' in session:
            try:
                Log.database(f"Connecting to '{Settings.DB_ANALYTICS_ROOT}' database for user history")
                history_conn = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
                history_conn.set_trace_callback(Log.database)
                history_cursor = history_conn.cursor()
                
                # Use upsert to update timestamp if record exists, otherwise insert
                history_cursor.execute(
                    """
                    INSERT OR REPLACE INTO userHistory (userName, postID, timeStamp)
                    VALUES (?, ?, ?)
                    """,
                    (session['userName'], post[0], currentTimeStamp())
                )
                history_conn.commit()
                history_conn.close()
            except Exception as e:
                Log.error(f"Error recording user history: {str(e)}")

        if request.method == "POST":
            if "postDeleteButton" in request.form:
                Delete.post(post[0])

                return redirect("/")

            if "commentDeleteButton" in request.form:
                Delete.comment(request.form["commentID"])

                return redirect(url_for("post.post", urlID=urlID)), 301

            from markupsafe import escape

            comment = escape(request.form["comment"])

            Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                "insert into comments(post,comment,user,timeStamp) \
                values(?, ?, ?, ?)",
                (
                    post[0],
                    comment,
                    session["userName"],
                    currentTimeStamp(),
                ),
            )
            connection.commit()

            Log.success(
                f'User: "{session["userName"]}" commented to post: "{urlID}"',
            )

            addPoints(5, session["userName"])

            flashMessage(
                page="post",
                message="success",
                category="success",
                language=session["language"],
            )

            return redirect(url_for("post.post", urlID=urlID)), 301

        Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        cursor.execute(
            """select * from comments where post = ? order by timeStamp desc""",
            [(post[0])],
        )
        comments = cursor.fetchall()

        if Settings.ANALYTICS:
            userIPData = getDataFromUserIP(str(request.headers.get("User-Agent")))
            idForRandomVisitor = None
            if "userName" in session:
                sessionUser = session["userName"]
            else:
                sessionUser = "unsignedUser"
            if userIPData["status"] == 0:
                Log.database(f"Connecting to '{Settings.DB_ANALYTICS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()

                cursor.execute(
                    """insert into postsAnalytics (postID, visitorUserName, country, os, continent, timeStamp) values (?,?,?,?,?,?) RETURNING id""",
                    (
                        post[0],
                        sessionUser,
                        userIPData["payload"]["country"],
                        userIPData["payload"]["os"],
                        userIPData["payload"]["continent"],
                        currentTimeStamp(),
                    ),
                )
                idForRandomVisitor = cursor.fetchone()[0]
                connection.commit()
                connection.close()
            else:
                Log.error(f"Aborting postsAnalytics, {userIPData['message']}")
        else:
            idForRandomVisitor = None

        return render_template(
            "post.html",
            id=post[0],
            title=post[1],
            tags=post[2],
            abstract=post[11],
            content=post[3],
            author=post[5],
            views=post[6],
            timeStamp=post[7],
            lastEditTimeStamp=post[8],
            urlID=post[10],
            form=form,
            comments=comments,
            appName=Settings.APP_NAME,
            blogPostUrl=request.root_url,
            readingTime=calculateReadTime(post[3]),
            idForRandomVisitor=idForRandomVisitor,
        )

    else:
        Log.error(f"{request.remote_addr} tried to reach unknown post")

        return render_template("notFound.html")
