#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:18:20 2020

@author: rohithbhandaru
"""


import os

from flask_migrate import Migrate
from appDir import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

app.logger.info('Artha app started')