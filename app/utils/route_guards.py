from functools import wraps

from flask import redirect, request, session

from models import User
from utils.flash_message import flash_message
from utils.log import Log


def login_required(
    route_name: str,
    redirect_to="/",
    flash_page: str | None = None,
    flash_message_key: str = "login",
    flash_category: str = "error",
):
    """Ensure the current session has a logged in user."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if "username" in session:
                return view_func(*args, **kwargs)

            Log.error(
                f"{request.remote_addr} tried to reach {route_name} without being logged in"
            )

            if flash_page:
                flash_message(
                    page=flash_page,
                    message=flash_message_key,
                    category=flash_category,
                    language=session.get("language", "en"),
                )

            if callable(redirect_to):
                return redirect(redirect_to(*args, **kwargs))

            return redirect(redirect_to)

        return wrapped_view

    return decorator


def admin_required(route_name: str):
    """Ensure the current session belongs to an admin user."""

    def decorator(view_func):
        @login_required(route_name)
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            username = session["username"]

            user = User.query.filter_by(username=username).first()
            if not user:
                Log.error(
                    f'Session user "{username}" was not found while reaching {route_name}'
                )
                return redirect("/")

            if user.role != "admin":
                Log.error(
                    f"{request.remote_addr} tried to reach {route_name} without being admin"
                )
                return redirect("/")

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
