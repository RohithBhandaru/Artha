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
from . import helper as helper
from .. import db
from .forms import MonthSelectForm, CategorySelectForm, DataUploadForm, ModalNewTxnForm, ModalUpdateTxnForm
from ..models import User, requires_access_level

UTC = pytz.utc

@main.route('/', methods = ['GET', 'POST'])
@main.route('/summary', methods = ['GET', 'POST'])
@login_required
def summary():
    form1 = MonthSelectForm()
    
    local_tz = pytz.timezone(current_user.timezone)
    local_month_year = local_tz.localize(dt.datetime(2020, 12, 1))
    data_for = local_month_year.strftime("%b'%y")
    
    txn_E, txn_I, monthly_num = helper.getMonthlyTxnData(local_month_year, current_user)
    
    return render_template('main/summary.html', title='Home', snavid = "snav-1", form1 = form1, txn_E = txn_E, monthly_num = monthly_num, data_for = data_for)

@main.route('/monthlyTrends', methods = ['GET', 'POST'])
@login_required
def monthlyTrends():
    if request.method == "POST":
        data = request.json['selectMonth']
        monYr = dt.datetime.strptime(data, '%Y-%m-%d')
        monYr = dt.datetime(monYr.year, monYr.month, 1)
        
        local_tz = pytz.timezone(current_user.timezone)
        local_month_year = local_tz.localize(monYr)
        data_for = local_month_year.strftime("%b'%y")
        
        txn_E, txn_I, monthly_num = helper.getMonthlyTxnData(local_month_year, current_user)
        data = {"txn_E": txn_E, "monthly_num": monthly_num, "data_for": data_for}
        return data













