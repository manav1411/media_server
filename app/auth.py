from flask import request, abort

def identify_user():
    if request.path.startswith("/media") or request.path.startswith("/static"):
        return
    user_email = request.headers.get("Cf-Access-Authenticated-User-Email")
    if not user_email:
        abort(403)
    request.user_email = user_email
