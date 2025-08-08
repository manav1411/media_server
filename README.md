# Home Media Streaming Server

## Overview
This project is a self-hosted, multi-user media streaming platform built from scratch using Python Flask, NGINX, Jackett, and cloudflare tunneling. It allows authorized users to:
- Search movies via TMDb API
- Automatically fetch the most seeded torrent for a requested movie
- Download and organize media (video, poster, subtitles) automatically
- Stream videos remotely through a web interface with progress tracking and subtitles
- Resume playback where users left off
- Manage download requests with cancellation functionality
- Access securely through Cloudflare Access with email-based authentication

The platform is designed to be lightweight, privacy-respecting, and fully controlled by the user without reliance on commercial streaming solutions.


## Desktop Demo

https://github.com/user-attachments/assets/300dace1-8348-46d3-9c9b-a4cc17651930


<details>
<summary>More demos</summary>
### Desktop Screenshots
<img width="1440" height="900" alt="mac screenshot 1" src="https://github.com/user-attachments/assets/a4ad54f0-8d10-4d6a-a4fd-eb3c7b7ebbb1" />

<img width="1440" height="900" alt="mac screenshot 2" src="https://github.com/user-attachments/assets/9fe0beaf-abb3-4343-be42-4f612116b68d" />

### Mobile Demo

https://github.com/user-attachments/assets/9a0b5a3c-fd86-4828-afd7-acf520f5a459

### Mobile Screenshots
<img width="402" height="874" alt="iphone screenshot 1" src="https://github.com/user-attachments/assets/d39f172b-56df-4588-be37-a22e810ed201" />

<img width="402" height="874" alt="iphone screenshot 2" src="https://github.com/user-attachments/assets/ab776e3c-7f46-43cf-b10f-0934e512a227" />

</details>


## Architecture Overview
Components:
- Flask Backend Server
  - Serves the web frontend
  - Handles user authentication via Cloudflare Access headers
  - Manages search requests to TMDb and Jackett
  - Tracks download progress and playback position per user
  - Provides REST endpoints for frontend interactions
- NGINX Server
  - Serves video files with HTTP byte-range support for streaming
  - Acts as a reverse proxy for Flask server
  - Manages static file delivery (posters, subtitles)
- Jackett
  - Acts as a torrent indexer aggregator
  - Integrated via API to search for torrents matching requested movies
  - Provides torrent URLs to Flask for download initiation
  - Torrent Client (qBittorrent-nox)
  - Downloads torrents triggered by Flask backend
  - Saves completed media files to organized folder structure under /media_library
- Cloudflare Tunnel + Access
  - Provides secure external access to the server without exposing IP
  - Ensures only authorized users with specified emails can access the service

Folder Structure:
```
/app
├── auth.py
├── __init__.py
├── /routes
│   ├── main.py
│   ├── media.py
│   ├── progress.py
├── /static
│   ├── global.css
│   └── movie.css
├── /templates
│   ├── index.html
│   └── movie.html
├── user_progress
├── user_progress.json
└── utils.py
/media_library
  └── Movie_Name/
       ├── movie.mp4
       ├── subtitles.vtt
       └── poster.jpg
run.py
README.md
```
- Each movie has its own folder named after the movie.
- The main video file is movie.mp4 (currently supports mp4 format only).
- Subtitles are stored in WebVTT format as subtitles.vtt.
- The poster image is saved as poster.jpg.

## Features
- Movie Search and Request -> Users can search for movies using the TMDb API from the homepage.
- Automated Torrent Download -> The most seeded torrent matching the search is automatically downloaded via Jackett + qBittorrent.
- Download Progress Tracking -> The UI shows real-time progress of torrent downloads per requested movie.
- Playback Progress Persistence -> Tracks where each user left off in a movie; resumes playback accordingly.
- Subtitles Support -> Automatically downloads and converts subtitles to .vtt for in-browser display.
- Multi-user Support -> Multiple users authenticated through Cloudflare Access share the media library but have separate playback states.
- Mobile-Friendly Interface -> Responsive design with custom video controls optimized for touch.
- Secure Access -> Restricts access to authorized users via Cloudflare Access.

## Limitations & Future Improvements
- Only supports .mp4 video format; does not currently handle .mkv or other container formats.
- Subtitles can be inaccurate; plan to implement user-selectable subtitle options and timing offset adjustment.
- Does not support TV shows or episodic content yet.
- Does not currently support searching existing media library (assumes small library).
- Missing additional metadata features such as trailers, cast info, or reviews.

## Setup and Running
### Prerequisites:
- Raspberry Pi or Linux server with Python 3.x
- Docker (optional, if you want containerized services)
- Installed and configured:
- Flask app (see server.py)
- NGINX
- Jackett
- qBittorrent-nox
- Cloudflared tunnel

### Starting Services
```
sudo systemctl restart server           # Flask server on port 8000
sudo systemctl restart cloudflared      # Cloudflare tunnel
sudo systemctl restart nginx            # NGINX reverse proxy on port 5000
sudo systemctl restart jackett          # Torrent indexer on port 9117
sudo systemctl restart qbittorrent-nox  # Torrent client on port 8080
```
pi is running on local IP http://192.168.0.134

### Access
- Open your browser to: https://home.mydomain.com
- Login is handled by Cloudflare Access.
- Search and request movies from the homepage.

## Architecture Diagram
(TODO: diagram here, the flow between user → Cloudflare Access → Cloudflare Tunnel → NGINX → Flask → Jackett/qBittorrent n Media Files). Include cloudflare using google's API to authenticate

## Key Files & Components
- server.py: Flask backend handling requests and user sessions
- nginx.conf: Reverse proxy configuration, byte-range support
- jackett.service: Background torrent indexer
- qbittorrent-nox.service: Background torrent client
- /media_library/: Organized media folder
- metadata.json: Stores movie metadata retrieved from TMDb
- .env: Environment variables including API keys

## How It Works (Workflow)
1. User visits homepage and searches for a movie.
2. Flask calls TMDb API to get movie details and poster.
3. Flask calls Jackett API to search for torrents of that movie on configured indexers.
4. The most seeded torrent is chosen and download starts via qBittorrent.
5. Download progress is tracked and sent to the frontend in real-time.
6. When download completes, files are organized in /media_library with poster and subtitles.
7. Movie is removed from the “requests” section automatically.
8. User clicks movie poster to start streaming with resume and subtitle controls.
9. Playback progress is saved per user and restored on subsequent visits.

## Contribution & Customization
This project is designed as a personal learning and self-hosted system. Contributions and forks are welcome with the following notes:
- Modify server.py to add new features or integrate other indexers.
- Improve UI/UX and add additional metadata support.
- Add TV shows, series support, or library search features.
