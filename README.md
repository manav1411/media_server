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
1. mae download bar green, not blue.
2. clicking on any part of the card (not just poster), like name, should open movie.
3. remove little white divider between poster and rest of card.
4. movie request bar is at bottom, but there should be no scroll bar (its scrolling a little it)
5. make sure movie doesn't show up in ready to watch, maybe check and only list those who have subtitle.vtt
6. when person wants to reload, why is "Are you sure you want to send a form again?" showing up? fix.