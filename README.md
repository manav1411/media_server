background services:
flask server->          sudo systemctl restart server.service
cloudflared tunnel->    sudo systemctl restart cloudflared
nginx server->          sudo systemctl restart nginx
jackett->               sudo systemctl restart jackett -> visit at http://192.168.0.134:9117
qbitorrent->            sudo systemctl restart jackett -> visit at http://192.168.0.134:8080



folder structure inside media_library:
each folder is a movie name, 
inside each folder movie.mp4 is the movie, subtitles.vtt is the subtitles, poster.jpg is the poster.

if running into error of movies stuck in requested section, add 'session["searched_movies"] = []' to top of / flask route and run once.



things to fix:
1. clicking on any part of the card (not just poster), like name, should open movie.
2. when person wants to reload, why is "Are you sure you want to send a form again?" showing up? fix.
3. make it mobile-friendly
3. delay in watched movie bar
4. search for Dune Part Two doesn't work for some reason...
5. if torrent gives mkv, convert to mp4
5. (not implementing) tv show support
6. (not implementing) searching for movies in library (will be a small library)
4. (not implementing) advanced filtering like genre, etc, description, etc. from timdb - need metadata file for each movie. also trailers, cast, etc like netflix.