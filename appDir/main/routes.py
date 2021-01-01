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
from flask import render_template, flash, request, jsonify, current_app, redirect, url_for
from flask_login import current_user, login_required

from . import main
from . import helper as helper
from .. import db, mclient
from .forms import MonthSelectForm, CategorySelectForm, DataUploadForm, ModalNewTxnForm, ModalUpdateTxnForm
from ..models import User, requires_access_level

UTC = pytz.utc

@main.route('/', methods = ['GET', 'POST'])
@main.route('/summary', methods = ['GET', 'POST'])
@login_required
def summary():
    form1 = MonthSelectForm()
    form2 = CategorySelectForm()
    form3 = ModalNewTxnForm()
    
    local_tz = pytz.timezone(current_user.timezone)
    local_month_year = local_tz.localize(dt.datetime(2020, 12, 1))
    data_for = local_month_year.strftime("%b'%y")
    
    txn_E, txn_I, monthly_num = helper.getMonthlyTxnData(local_month_year, current_user)
    
    exp_cat = helper.getCategoriesList("Expense", current_user)
    inc_cat = helper.getCategoriesList("Income", current_user)
    form2.selectCat.choices = exp_cat + inc_cat
    form3.category.choices = exp_cat + inc_cat
    
    catD = helper.getCategoryHistoryData('Bills', current_user)
    
    mfp = helper.getMFPortfolio(current_user, local_tz)
    mf_full_data = helper.getFullMFData(current_user)
    
    return render_template('main/summary.html', title='Home', snavid = "snav-1", form1 = form1, txn_E = txn_E, monthly_num = monthly_num, data_for = data_for, form2 = form2, catD = catD, form3 = form3, mfp = mfp, mf_full_data = mf_full_data)

@main.route('/monthlyTrends', methods = ['GET', 'POST'])
@login_required
def monthlyTrends():
    if request.method == "POST":
        data = request.json['selectMonth']
        monYr = dt.datetime.strptime(data, '%Y-%m')
        monYr = dt.datetime(monYr.year, monYr.month, 1)
        
        local_tz = pytz.timezone(current_user.timezone)
        local_month_year = local_tz.localize(monYr)
        data_for = local_month_year.strftime("%b'%y")
        
        txn_E, txn_I, monthly_num = helper.getMonthlyTxnData(local_month_year, current_user)
        data = {"txn_E": txn_E, "monthly_num": monthly_num, "data_for": data_for}
        return data

@main.route('/categoryHistory', methods = ['GET', 'POST'])
@login_required
def categoryHistory():
    if request.method == "POST":
        category = request.json['selectCat']
        catD = helper.getCategoryHistoryData(category, current_user)
        return catD

@main.route('/addNewTxn', methods = ['GET', 'POST'])
@login_required
def addNewTxn():
    form = ModalNewTxnForm(request.form)
    exp_cat = helper.getCategoriesList("Expense", current_user)
    inc_cat = helper.getCategoriesList("Income", current_user)
    form.category.choices = exp_cat + inc_cat
    
    if request.method=="POST":
        date = form.date.data
        amount = form.amount.data
        txn_type = form.txn_type.data
        category = form.category.data
        description = form.description.data
        
        tempObj = {
            "email": current_user.email,
            "date": dt.datetime(date.year, date.month, date.day),
            "category_type": txn_type,
            "category_name": category,
            "description": description,
            "amount": amount
        }
        # mclient["artha"]["transaction_data"].insert(tempObj)
        
        print("{0} - {1} - {2} - {3} - {4}".format(date, amount, txn_type, category, description))
        flash('New transaction added', category='success')
    return redirect(url_for('main.summary'))













