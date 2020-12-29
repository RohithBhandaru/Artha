#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 17:35:28 2020

@author: rohithbhandaru
"""


import os
import pytz
import datetime as dt
import dateutil.relativedelta as rdel
from flask import render_template, flash, request, jsonify, current_app
from flask_login import current_user, login_required

from . import main
from .. import db
from ..models import User, requires_access_level
from .forms import MonthSelectForm, CategorySelectForm, DataUploadForm, ModalNewTxnForm, ModalUpdateTxnForm

UTC = pytz.utc

@main.route('/', methods = ['GET', 'POST'])
@main.route('/summary', methods = ['GET', 'POST'])
@login_required
def summary():
    return render_template('summary.html', title='Home')