#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 15:35:50 2020

@author: rohithbhandaru
"""


from threading import Thread
from flask import current_app
from flask_mail import Message

from . import mail


def send_async_email(appContext, msg):
    with appContext.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
