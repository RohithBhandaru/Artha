#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 15:41:57 2020

@author: rohithbhandaru
"""


import os

# import jwt
import datetime as dt
from functools import wraps
from flask_login import UserMixin, logout_user
from flask import url_for, redirect, flash, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime)
    status = db.Column(db.String(32), index=True, default="Active")
    # Types of status: Active, Deleted
    confirmed = db.Column(db.Boolean, index=True, default=False)
    confirmed_on = db.Column(db.DateTime)
    user_type = db.Column(db.String(128), index=True)
    # Types of users: Customer, Admin

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return False

        if data.get("confirm") != self.id:
            return False

        self.confirmed = True
        self.confirmed_on = dt.datetime.utcnow()
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id}).decode("utf-8")

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return False

        user = User.query.get(data.get("reset"))
        if user is None:
            return False

        user.set_password(new_password)
        db.session.add(user)
        return True

    def initiate_admin_user(self):
        self.username = os.environ.get("ADMIN_USERNAME")
        self.email = os.environ.get("ADMIN_EMAIL")
        self.user_type = "Admin"
        self.registered_on = dt.datetime.utcnow()
        self.confirmed = True
        self.confirmed_on = dt.datetime.utcnow()
        self.status = "Active"
        self.set_password(os.environ.get("ADMIN_PASSWORD"))
        db.session.commit()

        return True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.user_type == "Admin"

    def access_allowed(self, access_type):
        return self.user_type == access_type

    def __repr__(self):
        return "<User {}>".format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class MFPortfolio(db.Model):
    __tablename__ = 'mf_portfolio'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True)
    fund_name = db.Column(db.String(480), index=True)
    folio_num = db.Column(db.String(480), index=True)
    as_on_date = db.Column(db.DateTime, default=dt.datetime.utcnow())
    cub = db.Column(db.Float(128))
    nav = db.Column(db.Float(128))
    total_investment = db.Column(db.Float(128))
    investing_since = db.Column(db.DateTime, default=dt.datetime.utcnow())
    
    def __repr__(self):
        return '<Fund {}>'.format(self.fund_name)


def requires_access_level(user, access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not user.access_allowed(access_level):
                logout_user()
                flash("You do not have access to that page. Sorry!")
                return redirect(url_for("login"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator