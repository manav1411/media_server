from flask import Flask, request, abort, render_template_string, send_from_directory, jsonify
import os
import json

HOST, PORT = "0.0.0.0", 8000
app = Flask(__name__)
media_path = "../media_library"
progress_path = "./user_progress.json"

# Load or initialize user progress data
if os.path.exists(progress_path):
    with open(progress_path, "r") as f:
        user_progress = json.load(f)
else:
    user_progress = {}

# Authentication
@app.before_request
def identify_user():
    if request.path.startswith("/media") or request.path.startswith("/static"):
        return
    user_email = request.headers.get("Cf-Access-Authenticated-User-Email")
    if not user_email:
        abort(403)
    request.user_email = user_email

# Landing page
@app.route("/")
def landing_page():
    movies = []
    for name in os.listdir(media_path):
        movie_dir = os.path.join(media_path, name)
        if os.path.isdir(movie_dir):
            poster_path = f"/media/{name}/poster.jpg"
            progress = user_progress.get(request.user_email, {}).get(name, 0)
            movies.append({"name": name, "poster": poster_path, "progress_seconds": progress})
    
    return render_template_string("""
<html>
<head>
    <style>
        /* Global styles */
        body {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
        }

        h1 {
            text-align: center;
            color: #FFFFFF;
            margin-bottom: 30px;
        }

        /* Grid of movies */
        .movies {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }

        .movie {
            background-color: #1E1E1E;
            border-radius: 10px;
            overflow: hidden;
            width: 180px;
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.4);
        }

        .movie:hover {
            transform: scale(1.03);
            box-shadow: 0 0 12px rgba(255, 255, 255, 0.1);
        }

        .movie img {
            width: 100%;
            height: auto;
            border-bottom: 1px solid #333;
        }

        .movie-title {
            padding: 10px;
            font-size: 16px;
            color: #E0E0E0;
        }

        /* Progress bar */
        .progress-container {
            width: 100%;
            height: 6px;
            background-color: #2C2C2C;
        }

        .progress-bar {
            height: 100%;
            background-color: #55AEF5;
            width: 0%;
            transition: width 0.3s ease;
        }

        /* Responsive design */
        @media (max-width: 600px) {
            .movie {
                width: 45%;
            }
        }
    </style>
</head>
<body>
    <h1>Welcome, {{ user_email }}</h1>
    <div class="movies">
        {% for movie in movies %}
            <div class="movie">
                <a href="/movie/{{ movie.name }}">
                    <img src="{{ movie.poster }}" alt="Poster for {{ movie.name }}">
                </a>
                <div class="progress-container" data-movie="{{ movie.name }}" data-seconds="{{ movie.progress_seconds }}">
                    <div class="progress-bar"></div>
                </div>
                <div class="movie-title">{{ movie.name }}</div>
            </div>
        {% endfor %}
    </div>

    <video id="dummy" style="display:none"></video>
    <script>
        const dummy = document.getElementById("dummy");
        const containers = document.querySelectorAll(".progress-container");

        containers.forEach(container => {
            const movie = container.dataset.movie;
            const seconds = parseFloat(container.dataset.seconds);
            const bar = container.querySelector(".progress-bar");

            const src = `/media/${movie}/movie.mp4`;
            dummy.src = src;

            dummy.addEventListener("loadedmetadata", () => {
                const duration = dummy.duration;
                if (duration > 0 && seconds > 0) {
                    const percent = Math.min((seconds / duration) * 100, 100);
                    bar.style.width = percent + "%";
                }
            }, { once: true });

            dummy.load();
        });
    </script>
</body>
</html>


""", user_email=request.user_email, movies=movies)

# Serve static media files
@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_from_directory(media_path, filename)

# Movie playback page
@app.route("/movie/<movie_name>")
def movie_page(movie_name):
    movie_file = f"/media/{movie_name}/movie.mp4"
    subtitles_file = f"/media/{movie_name}/subtitles.vtt"
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ movie_name }}</title>
<style>
  /* Full screen page + reset */
  html, body {
    margin: 0; padding: 0; height: 100%; background: #121212; color: #eee; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
  }
  body {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }

  /* Back button top right */
  #backBtn {
    position: fixed;
    top: 15px; left: 20px;
    background: #222;
    border: none;
    color: #eee;
    padding: 10px 15px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 4px;
    transition: background 0.3s ease;
    z-index: 1000;
  }
  #backBtn:hover {
    background: #555;
  }

  /* Video fills screen (leave room for controls) */
  video#player {
    max-height: 80vh;
    width: 100vw;
    background: black;
    outline: none;
  }

  /* Controls container */
  #controls {
    width: 100vw;
    max-width: 100vw;
    background: #222;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-sizing: border-box;
  }

  /* Buttons style */
  button.control-btn {
    background: #444;
    border: none;
    color: #eee;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }
  button.control-btn:hover {
    background: #666;
  }

  /* Progress bar container */
  #progress-container {
    flex-grow: 1;
    height: 8px;
    background: #555;
    border-radius: 4px;
    cursor: pointer;
    position: relative;
  }

  /* Progress bar fill */
  #progress {
    height: 100%;
    background: #55AEF5; /* Spotify green for nice contrast */
    width: 0%;
    border-radius: 4px;
  }
</style>
</head>
<body>

<button id="backBtn" onclick="window.location.href='/'">&#8592; Back</button>

<video id="player" tabindex="0" preload="metadata">
  <source src="{{ movie_file }}" type="video/mp4" />
  <track id="subTrack" label="English" kind="subtitles" srclang="en" src="{{ subtitles_file }}" default>
  Your browser does not support the video tag.
</video>

<div id="controls">
  <button class="control-btn" onclick="togglePlay()" id="playPauseBtn">▶️ Play</button>
  <button class="control-btn" onclick="seek(-10)">⏪ 10s</button>
  <button class="control-btn" onclick="seek(10)">⏩ 10s</button>
  <button class="control-btn" onclick="toggleSubtitles()" id="subBtn">Subtitles ON</button>
  <button class="control-btn" onclick="toggleFullscreen()">⛶ Fullscreen</button>

  <div id="progress-container" aria-label="Video progress bar" role="slider" tabindex="0">
    <div id="progress"></div>
  </div>
</div>

<script>
  const video = document.getElementById("player");
  const playPauseBtn = document.getElementById("playPauseBtn");
  const subBtn = document.getElementById("subBtn");
  const progressContainer = document.getElementById("progress-container");
  const progressBar = document.getElementById("progress");
  const progressUrl = "/progress";
  const movieName = "{{ movie_name }}";

  // Load last watched time
  fetch(`${progressUrl}?movie=${movieName}`)
    .then(res => res.json())
    .then(data => {
      if (data.time) video.currentTime = data.time;
    });

  // Update progress bar visually as video plays
  video.addEventListener("timeupdate", () => {
    const percent = (video.currentTime / video.duration) * 100 || 0;
    progressBar.style.width = percent + "%";
    updatePlayPauseButton();
  });

  // Play/pause button text update
  function updatePlayPauseButton() {
    playPauseBtn.textContent = video.paused ? "▶️ Play" : "⏸ Pause";
  }

  // Toggle play/pause
  function togglePlay() {
    if (video.paused) video.play();
    else video.pause();
  }

  // Seek relative seconds
  function seek(seconds) {
    video.currentTime = Math.min(Math.max(0, video.currentTime + seconds), video.duration || 0);
  }

  // Toggle subtitles on/off
  function toggleSubtitles() {
    const track = document.getElementById("subTrack");
    if (track.mode === "showing") {
      track.mode = "disabled";
      subBtn.textContent = "Subtitles OFF";
    } else {
      track.mode = "showing";
      subBtn.textContent = "Subtitles ON";
    }
  }

  // Toggle fullscreen for video element
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      video.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  // Clicking progress bar to jump
  progressContainer.addEventListener("click", (e) => {
    const rect = progressContainer.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const clickPercent = clickX / width;
    video.currentTime = clickPercent * video.duration;
  });

  // Keyboard support for progress bar
  progressContainer.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      seek(-5);
      e.preventDefault();
    } else if (e.key === "ArrowRight") {
      seek(5);
      e.preventDefault();
    }
  });

  // Save progress every 5 seconds
  setInterval(() => {
    fetch(progressUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ movie: movieName, time: video.currentTime })
    });
  }, 5000);

  // Save progress when tab closes
  window.addEventListener("beforeunload", () => {
    navigator.sendBeacon(progressUrl, JSON.stringify({ movie: movieName, time: video.currentTime }));
  });

  // Initialize subtitles button state
  document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("subTrack");
    subBtn.textContent = track.mode === "showing" ? "Subtitles ON" : "Subtitles OFF";
    updatePlayPauseButton();
  });
</script>

</body>
</html>
""", movie_name=movie_name, movie_file=movie_file, subtitles_file=subtitles_file, user_email=request.user_email)

# Endpoint to get or set progress
@app.route("/progress", methods=["GET", "POST"])
def movie_progress():
    user = request.headers.get("Cf-Access-Authenticated-User-Email")
    if not user:
        abort(403)

    if request.method == "GET":
        movie = request.args.get("movie")
        time = user_progress.get(user, {}).get(movie, 0)
        return jsonify({"time": time})

    data = request.get_json()
    movie = data["movie"]
    time = float(data["time"])

    if user not in user_progress:
        user_progress[user] = {}
    user_progress[user][movie] = time

    with open(progress_path, "w") as f:
        json.dump(user_progress, f)

    return jsonify({"status": "ok"})



if __name__ == "__main__":
    app.run(host=HOST, port=PORT)