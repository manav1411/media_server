from flask import Blueprint, request, render_template, current_app
import os
from ..utils import load_progress

bp = Blueprint("main", __name__)
progress = {}

@bp.before_app_first_request
def load_user_progress():
    global progress
    progress = load_progress(current_app.config['PROGRESS_PATH'])

@bp.route("/")
def landing_page():
    media_path = current_app.config['MEDIA_PATH']
    movies = []

    for name in os.listdir(media_path):
        movie_dir = os.path.join(media_path, name)
        if os.path.isdir(movie_dir):
            poster = f"/media/{name}/poster.jpg"
            seconds = progress.get(request.user_email, {}).get(name, 0)
            movies.append({"name": name, "poster": poster, "progress_seconds": seconds})

    return render_template("index.html", user_email=request.user_email, movies=movies)

@bp.route("/movie/<movie_name>")
def movie_page(movie_name):
    movie_file = f"/media/{movie_name}/movie.mp4"
    subtitles_file = f"/media/{movie_name}/subtitles.vtt"
    return render_template("movie.html", movie_name=movie_name, movie_file=movie_file, subtitles_file=subtitles_file)
