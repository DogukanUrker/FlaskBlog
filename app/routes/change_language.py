from flask import Blueprint, redirect, request, session

change_language_blueprint = Blueprint("change_language", __name__)


@change_language_blueprint.route("/change-language", methods=["GET", "POST"])
def change_language():
    """
    This function is the route for the change language page.
    It is used to change the user's language.

    Args:
        request.form (dict): the form data from the request

    Returns:
        redirect: a redirect to the previous page
    """

    if request.method == "POST":
        language = request.form["language"]
        session["language"] = language
        return redirect(request.form["redirect"])

    return redirect("/")
