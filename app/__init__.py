from flask import Flask
import os
import json

media_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media_library'))
progress_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'user_progress.json'))

def create_app():
    app = Flask(__name__)
    default_secret = os.urandom(32)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", default_secret)
    app.config['MEDIA_PATH'] = media_path
    app.config['PROGRESS_PATH'] = progress_path

    from .auth import identify_user
    app.before_request(identify_user)

    from .routes import main, media, progress
    app.register_blueprint(main.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(progress.bp)

    return app
