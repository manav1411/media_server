from flask import Blueprint, send_from_directory, current_app

bp = Blueprint("media", __name__, url_prefix="/media")

@bp.route("/<path:filename>")
def serve_media(filename):
    return send_from_directory(current_app.config['MEDIA_PATH'], filename)
