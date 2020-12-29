#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 16:26:08 2020

@author: rohithbhandaru
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes