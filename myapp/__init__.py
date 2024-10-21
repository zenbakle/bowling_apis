import os
from flask import Flask
from .routes import game, games



def create_app():
    app = Flask(__name__)

    gamess = games

    app.register_blueprint(game)

    return app, gamess
