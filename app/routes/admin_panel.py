from flask import Blueprint, render_template, session

from utils.log import Log
from utils.route_guards import admin_required

admin_panel_blueprint = Blueprint("admin_panel", __name__)


@admin_panel_blueprint.route("/admin")
@admin_required("admin panel")
def admin_panel():
    Log.info(f"Admin: {session['username']} reached to the admin panel")

    Log.info("Rendering admin_panel.html: params: None")

    return render_template("admin_panel.html")
