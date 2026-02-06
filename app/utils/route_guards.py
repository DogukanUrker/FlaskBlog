from functools import wraps

from flask import redirect, request, session

from models import User
from utils.log import Log


def admin_required(route_name: str):
    """Ensure the current session belongs to an admin user."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            username = session.get("username")

            if not username:
                Log.error(
                    f"{request.remote_addr} tried to reach {route_name} without being logged in"
                )
                return redirect("/")

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
