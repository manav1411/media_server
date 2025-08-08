# SimplyServed - a Media Streaming Server
A fully custom-built, privacy-first self-hosted media streaming platform with multi-user support, torrent automation, and personalised playback

## Overview
SimplyServed is a self-hosted, privacy-first media streaming platform built entirely from scratch using Flask, NGINX, and torrent automation tools. It lets multiple authorised users remotely search, request, and stream movies seamlessly — with automatic torrent downloading, metadata fetching, subtitle support, and personalised playback progress tracking. Unlike off-the-shelf solutions like Plex or Jellyfin, SimplyServed is a full custom-built system that I designed end-to-end - demonstrating full-stack knowledge in backend architecture, media streaming, API integration, secure user access, software architecture, and networking.


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


## Architecture Component Diagram
<img width="3840" height="2509" alt="architecture" src="https://github.com/user-attachments/assets/5e9613a4-44af-45d1-8043-6ab657648b97" />


## Architecture Sequence Diagram
<img width="7680" height="3124" alt="sequence" src="https://github.com/user-attachments/assets/9d113577-1d7d-4ec1-b13d-d465e757ee4e" />


## Tech Stack

| Layer              | Tech          | Purpose                              |
|--------------------|---------------------------|------------------------------------|
| Hardware           | Raspberry Pi 400 + SSD    | Self-hosted media server              |
| Backend Framework  | Python Flask              | Web server and API                    |
| Web Server         | NGINX                     | Reverse proxy and static/media hosting |
| Torrent Indexer    | Jackett                   | Torrent search aggregation            |
| Torrent Client     | qBittorrent-nox           | Headless torrent downloading and management          |
| Media Storage      | External SSD (Mounted)    | Storage for /media_library files      |
| Domain & DNS       | Cloudflare                | DNS management, secure tunneling      |
| Authentication     | Cloudflare Access + Google OAuth | Secure, email-based user login |
| External APIs      | TMDb (movie poster/metadata), OpenSubtitles (subtitle files), Jackett (torrent indexer aggregation) | Movie metadata/poster, subtitles, movie files |
| Media Processing   | ffmpeg                    | Subtitle conversion (SRT → VTT)     |
| Frontend           | HTML/CSS/JS               | Responsive UI and video player      |
| Communication      | APIs                      | Backend interaction with services   |


## Folder Structure:
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
├── user_progress.json
└── utils.py
/media_library
  └── Movie_Name/
       ├── movie.mp4
       ├── subtitles.vtt
       ├── metadata.json
       └── poster.jpg
run.py
README.md
```
Media files are organized in /media_library, each movie in its own folder named after the movie, containing `movie.mp4`, `subtitles.vtt`, `metadata.json`, and `poster.jpg`.

## Features
- Movie Search and Request -> Users can search for movies using the TMDb API from the homepage.
- Automated Torrent Download -> The most seeded torrent matching the search is automatically downloaded via Jackett + qBittorrent.
- Download Progress Tracking -> The UI shows real-time progress of torrent downloads per requested movie.
- Playback Progress Persistence -> Tracks where each user left off in a movie; resumes playback accordingly.
- Subtitles Support -> Automatically downloads and converts subtitles to .vtt for in-browser display.
- Multi-user Support -> Multiple users authenticated through Cloudflare Access share the media library but have separate playback states.
- Mobile-Friendly Interface -> Responsive design with custom video controls optimized for touch.
- Secure Access -> Restricts access to authorized users via Cloudflare Access.


## Future Improvements
- Add TV show and episodic content support with season/episode management.
- Implement HLS adaptive streaming for smoother remote playback on slower networks.
- Extra metadata such as trailers, cast info, reviews, etc.
- support for other file formats other than mp4, such as mkv.
- Improve subtitles accuracy by allowing user-selectable subtitle options and ability to offset timing.


## Key Files & Components
- server.py: Flask backend handling requests and user sessions
- nginx.conf: Reverse proxy configuration, byte-range support
- jackett.service: Background torrent indexer
- qbittorrent-nox.service: Background torrent client
- /media_library/: Organized media folder
- metadata.json: Stores movie metadata retrieved from TMDb
- .env: Environment variables including API keys


## Contribution & Customization
This project is designed as a personal learning and self-hosted system. Contributions and forks are welcome with the following notes:
- Modify server.py to add new features or integrate other indexers.
- Improve UI/UX and add additional metadata support.
- Add TV shows, series support, or library search features.


## Setup and Running
I do not expect many people to actually run this, it is moreso a demonstration of my skills. Nevertheless, if you are so inclined, the steps are below.

### Prerequisites:
- Linux server (e.g. Raspberry Pi) with Python 3.x
- Flask app and dependencies (see Python files)
- NGINX configured as reverse proxy
- Jackett, qBittorrent-nox with APIs set up
- OpenSubtitles, TMdb API keys
- Cloudflared tunnel configured with your domain
- (Optional) Docker for containerized deployment

### Starting Services
```
sudo systemctl restart server           # Flask server on port 8000
sudo systemctl restart cloudflared      # Cloudflare tunnel
sudo systemctl restart nginx            # NGINX reverse proxy on port 5000
sudo systemctl restart jackett          # Torrent indexer on port 9117
sudo systemctl restart qbittorrent-nox  # Torrent client on port 8080
```
`SSH`-ing into your server is reccomended.

### Usage
- Visit https://home.yourdomain.com
- Log in via Cloudflare Access
- Search or request movies from the homepage
- Click a movie poster to stream with subtitles and resume playback support
- Track download and playback progress in real time
