# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 13:49:11 2020
@author: RohithBhandaru
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes
