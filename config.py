#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:41:22 2020

@author: rohithbhandaru
"""


import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard-to-guess-string"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get("MONGO_URI")
    
    MF_STATEMENT_PWD = 'Asia@1996'
    DAILY_TXN_FILE_NAME = 'Daily - Txns Statement.xls'
    MF_TXN_FILE_NAME = 'MF - Txns Statement.pdf'
    EQ_TXN_FILE_NAME = 'Equity - Txns Statement.csv'
    
    TXNS_PER_PAGE = 10
    
    MAX_CONTENT_LENGTH = 1024*1024*5
    UPLOAD_PATH = os.path.join(basedir, r"DB Population\Object Storage")
    UPLOAD_EXTENSIONS = [".pdf"]
    
    #If ASSETS_DEBUG == True, Flask-Assets won't bundle our static files while
    #we're running Flask in debug mode
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = True
    
    COMPRESS_MIMETYPES = ["text/html", "text/css", "text/xml", "application/json", "application/javascript"]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    MAIL_DEBUG = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = [os.environ.get("ADMIN_EMAIL")]
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "data-dev.db")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or "sqlite://"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "data.db")
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

config = {"development": DevelopmentConfig, "testing": TestingConfig, "production": ProductionConfig, "default": DevelopmentConfig}

















