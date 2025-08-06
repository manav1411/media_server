from flask import request, abort

def identify_user():
    if request.path.startswith("/media") or request.path.startswith("/static"):
        return
    user_email = request.headers.get("Cf-Access-Authenticated-User-Email")
    user_name = request.headers.get("Cf-Access-Authenticated-User-Name")
    if not user_email:
        abort(403)
    request.user_email = user_email
    request.user_name = user_name or user_email.split('@')[0]  # fallback is username=email name
