from ..utils import load_progress, search_and_download_subtitle, finalize_movie_folder, download_poster_and_metadata, normalize
from flask import Blueprint, request, render_template, current_app, session, jsonify, redirect, url_for
from urllib.parse import urlencode
from dotenv import load_dotenv
import subprocess
import requests
import shutil
import gzip
import html
import json
import os
import re

load_dotenv(dotenv_path="/home/manavpi/home_server/.env")
JACKETT_API_KEY = os.getenv("JACKETT_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

bp = Blueprint("main", __name__)
progress = {}
MAX_SEARCH_RESULTS = 5
in_progress_downloads = {}
post_processed = set()  # tracks processed movies
completed_downloads = set()

@bp.before_app_first_request
def load_user_progress():
    global progress
    progress = load_progress(current_app.config['PROGRESS_PATH'])

@bp.route("/", methods=["GET", "POST"])
def landing_page():
    global progress
    progress = load_progress(current_app.config['PROGRESS_PATH'])

    media_path = current_app.config['MEDIA_PATH']
    movies = []

    # hard reset session in case dev error
    ## session["searched_movies"] = []
    

    for name in os.listdir(media_path):
        movie_dir = os.path.join(media_path, name)
        if os.path.isdir(movie_dir):
            subtitles_file = os.path.join(movie_dir, "metadata.json")
            if not os.path.exists(subtitles_file):
                continue

            metadata_path = os.path.join(movie_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                continue

            try:
                with open(metadata_path, encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                current_app.logger.warning(f"Failed to read metadata for {name}: {e}")
                continue

            poster = f"/media/{name}/poster.jpg"
            encoded_name = html.escape(name, quote=True).replace("&#x27;", "&#39;")
            seconds = progress.get(request.user_email, {}).get(encoded_name, 0)

            movie_info = {
                "name": name,
                "poster": poster,
                "progress_seconds": seconds,
                "title": metadata.get("title", name),
                "year": metadata.get("release_date", "")[:4],
                "overview": metadata.get("overview", "No description available."),
                "genres": metadata.get("genres", []),
                "runtime": metadata.get("runtime"),
                "rating": metadata.get("rating"),
                "tmdb_id": metadata.get("tmdb_id")
            }

            movies.append(movie_info)

    # Initialize searched_movies if not present
    if "searched_movies" not in session:
        session["searched_movies"] = []

    session["searched_movies"] = [
        m for m in session["searched_movies"]
        if m["id"] not in completed_downloads
    ]
    session.modified = True

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            url = "https://api.themoviedb.org/3/search/movie"
            headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
            params = {"query": query, "include_adult": False, "language": "en-US", "page": 1}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            results = data.get("results", [])
            if results:

                query_normalized = normalize(query)

                close_matches = [r for r in results if normalize(r["title"]) == query_normalized]

                # If any close match exists, pick the one with highest popularity
                if close_matches:
                    most_popular = max(close_matches, key=lambda r: r.get("popularity", 0))
                else:
                    # Fallback: just take the most popular from all results
                    most_popular = max(results, key=lambda r: r.get("popularity", 0))

                if not any(m["id"] == most_popular["id"] for m in session["searched_movies"]):
                    if len(session["searched_movies"]) >= MAX_SEARCH_RESULTS:
                        session["searched_movies"].pop(0)
                    session["searched_movies"].append(most_popular)
                    session.modified = True

                    try:
                        start_download(most_popular["id"])
                    except Exception as e:
                        current_app.logger.error(f"Auto-download failed: {e}")
        return redirect(url_for("main.landing_page"))

    return render_template(
        "index.html",
        user_name=request.user_name,
        movies=movies,
        searched_movies=session["searched_movies"]
    )



@bp.route("/remove_movie/<int:movie_id>", methods=["POST"])
def remove_movie(movie_id):
    # Remove movie by TMDb ID from session list
    if "searched_movies" in session:
        session["searched_movies"] = [m for m in session["searched_movies"] if m["id"] != movie_id]
        session.modified = True
    return "", 204  # No Content response

@bp.route("/movie/<movie_name>")
def movie_page(movie_name):
    movie_file = f"/media/{movie_name}/movie.mp4"
    subtitles_file = f"/media/{movie_name}/subtitles.vtt"
    return render_template("movie.html", movie_name=movie_name, movie_file=movie_file, subtitles_file=subtitles_file)


# helper function to start downloads
def start_qbittorrent_download(torrent_url, save_path):
    qb_host = os.getenv("QBITTORRENT_HOST")
    qb_user = os.getenv("QBITTORRENT_USER")
    qb_pass = os.getenv("QBITTORRENT_PASS")

    s = requests.Session()
    # Login
    login = s.post(f"{qb_host}/api/v2/auth/login", data={"username": qb_user, "password": qb_pass})
    if login.status_code != 200 or login.text != "Ok.":
        return False

    # Add torrent
    add = s.post(f"{qb_host}/api/v2/torrents/add", data={
        "urls": torrent_url,
        "savepath": save_path,
        "category": "media"
    })
    return add.status_code == 200

@bp.route("/start_download/<int:tmdb_id>", methods=["POST"])
def start_download(tmdb_id):
    # First: get TMDb info
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", headers=headers)
    movie_data = response.json()
    movie_title = movie_data["title"]

    in_progress_downloads[tmdb_id] = {
        "title": movie_title,
        "original_title": movie_data["title"]
    }

    # 1. Search Jackett
    jackett_url = f"http://localhost:9117/api/v2.0/indexers/all/results"
    query = {
        "apikey": JACKETT_API_KEY,
        "Query": f"{movie_title} {movie_data.get('release_date', '')[:4]}" if movie_title.lower() != "casablanca" else movie_title
    }

    r = requests.get(jackett_url, params=query)
    if r.status_code != 200:
        return jsonify({"error": "Jackett search failed"}), 500

    results = r.json().get("Results", [])
    if not results:
        return jsonify({"error": "No torrents found"}), 404

    # 2. Choose best torrent (by seeders)
    filtered_results = [r for r in results if "1080p" in r["Title"].lower()]
    if not filtered_results:
        filtered_results = results  # fallback to all results
    
    # Sort by seeders
    filtered_results.sort(key=lambda x: x.get("Seeders", 0), reverse=True)
    best = filtered_results[0]

    # 3. Start download with qBittorrent
    save_path = os.path.join(current_app.config['MEDIA_PATH'], movie_title)
    os.makedirs(save_path, exist_ok=True)
    success = start_qbittorrent_download(best["MagnetUri"], save_path)

    if not success:
        return jsonify({"error": "Failed to add torrent"}), 500

    return jsonify({"status": "started", "title": movie_title})


@bp.route("/download_status/<movie_title>")
def download_status(movie_title):
    qb_host = os.getenv("QBITTORRENT_HOST")
    qb_user = os.getenv("QBITTORRENT_USER")
    qb_pass = os.getenv("QBITTORRENT_PASS")

    s = requests.Session()
    login = s.post(f"{qb_host}/api/v2/auth/login", data={"username": qb_user, "password": qb_pass})
    if login.status_code != 200 or login.text != "Ok.":
        return jsonify({"error": "qBittorrent login failed"}), 500

    torrents = s.get(f"{qb_host}/api/v2/torrents/info").json()

    for torrent in torrents:
        if normalize(movie_title) in normalize(torrent["name"]):

            # Find matching tmdb_id for this title
            tmdb_id = next((id for id, title in in_progress_downloads.items() if normalize(title["title"]) == normalize(movie_title)), None)

            if torrent["progress"] >= 1.0:
                if tmdb_id:
                    completed_downloads.add(tmdb_id)
                    in_progress_downloads.pop(tmdb_id, None)

                    # post-processing after download done
                    base_path = os.path.join(current_app.config['MEDIA_PATH'], movie_title)
                    finalize_movie_folder(base_path)
                    download_poster_and_metadata(tmdb_id, base_path)
                    search_and_download_subtitle(movie_title, base_path)

            return jsonify({
                "progress": torrent["progress"],
                "state": torrent["state"]
            })

    return jsonify({"error": "Torrent not found"}), 404


@bp.route("/download_state/<int:tmdb_id>")
def download_state(tmdb_id):
    if tmdb_id in completed_downloads:
        return jsonify({"state": "completed"})
    elif tmdb_id in in_progress_downloads:
        return jsonify({"state": "downloading"})
    return jsonify({"state": "idle"})


@bp.route("/cancel_download/<int:tmdb_id>", methods=["POST"])
def cancel_download(tmdb_id):
    title = in_progress_downloads.get(tmdb_id)["title"]
    if not title:
        return jsonify({"error": "not in progress"}), 404

    # Remove from qBittorrent
    qb_host = os.getenv("QBITTORRENT_HOST")
    qb_user = os.getenv("QBITTORRENT_USER")
    qb_pass = os.getenv("QBITTORRENT_PASS")

    s = requests.Session()
    login = s.post(f"{qb_host}/api/v2/auth/login", data={"username": qb_user, "password": qb_pass})
    if login.status_code != 200 or login.text != "Ok.":
        return jsonify({"error": "login failed"}), 500

    # Get torrent hashes
    info = s.get(f"{qb_host}/api/v2/torrents/info", params={"category": "media"})
    torrents = info.json()
    for torrent in torrents:
        if normalize(title) in normalize(torrent["name"]):
            hash_ = torrent["hash"]
            s.post(f"{qb_host}/api/v2/torrents/delete", data={"hashes": hash_, "deleteFiles": "true"})
            break

    # Remove folder
    media_path = os.path.join(current_app.config["MEDIA_PATH"], title)
    if os.path.exists(media_path):
        shutil.rmtree(media_path, ignore_errors=True)

    in_progress_downloads.pop(tmdb_id, None)

    # Remove from session
    session["searched_movies"] = [m for m in session.get("searched_movies", []) if m["id"] != tmdb_id]
    session.modified = True

    return jsonify({"status": "cancelled"})

 
# get media directory stats
@bp.route("/controls_info")
def controls_info():
    media_path = current_app.config['MEDIA_PATH']
    total_size = 0
    folders = []

    for folder in os.listdir(media_path):
        folder_path = os.path.join(media_path, folder)
        if os.path.isdir(folder_path):
            size = sum(os.path.getsize(os.path.join(dp, f))
                       for dp, dn, filenames in os.walk(folder_path)
                       for f in filenames)
            total_size += size
            folders.append({"name": folder, "size": round(size / (1024 * 1024), 2)})

    return jsonify({
        "total_size": round(total_size / (1024 * 1024), 2),  # in MB
        "directories": folders
    })

# clear session
@bp.route("/reset_search", methods=["POST"])
def reset_search():
    session["searched_movies"] = []
    session.modified = True
    return "", 204

# removes torrent and deletes movie folder
@bp.route("/delete_folder/<folder>", methods=["POST"])
def delete_folder(folder):
    media_path = current_app.config['MEDIA_PATH']
    folder_path = os.path.join(media_path, folder)

    # Remove matching torrent from qBittorrent
    qb_host = os.getenv("QBITTORRENT_HOST")
    qb_user = os.getenv("QBITTORRENT_USER")
    qb_pass = os.getenv("QBITTORRENT_PASS")

    try:
        s = requests.Session()
        login = s.post(f"{qb_host}/api/v2/auth/login", data={"username": qb_user, "password": qb_pass})
        if login.status_code == 200 and login.text == "Ok.":

            torrents = s.get(f"{qb_host}/api/v2/torrents/info", params={"category": "media"}).json()
            for torrent in torrents:
                if folder.lower() in torrent["name"].lower():
                    hash_ = torrent["hash"]
                    s.post(f"{qb_host}/api/v2/torrents/delete", data={"hashes": hash_, "deleteFiles": "true"})
                    break  # Stop after first match

    except Exception as e:
        current_app.logger.warning(f"Failed to remove torrent for {folder}: {e}")

    # Delete the folder
    if os.path.isdir(folder_path):
        shutil.rmtree(folder_path, ignore_errors=True)
        return "", 204

    return "Folder not found", 404
