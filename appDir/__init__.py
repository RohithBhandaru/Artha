#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:37:11 2020

@author: rohithbhandaru
"""


from appDir import models
import os
import logging
from flask import Flask
from flask_mail import Mail
from pymongo import MongoClient
from flask_moment import Moment
from flask_compress import Compress
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment
from logging.handlers import RotatingFileHandler

from . import assets as assetsModule
from config import config

db = SQLAlchemy()
moment = Moment()
assets = Environment()
compress = Compress()
mail = Mail()
login = LoginManager()
login.login_view = "auth.login"
mclient = MongoClient(config["default"].MONGO_URI)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login.init_app(app)
    moment.init_app(app)
    assets.init_app(app)
    compress.init_app(app)
    mail.init_app(app)

    # with app.app_context():
    #     assets.load_path = [
    #         os.path.join(os.path.dirname(__file__), "static/js"),
    #         os.path.join(os.path.dirname(__file__), "static/styles"),
    #     ]
    #     assetsModule.compile_assets(assets)

    # Registering blue prints
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    # Initiating logging module
    if not app.config["DEBUG"]:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/arthaApp_v1.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s -:- %(levelname)s -:- %(message)s -:- [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)

    return app
