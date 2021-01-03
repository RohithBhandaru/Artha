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
from bson import ObjectId
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
    
    local_tz = pytz.timezone(current_user.timezone)
    
    if request.method=="POST":
        date = form.date.data
        amount = form.amount.data
        txn_type = form.txn_type.data
        category = form.category.data
        description = form.description.data
        
        tempObj = {
            "email": current_user.email,
            "date": local_tz.localize(dt.datetime(date.year, date.month, date.day)).astimezone(UTC),
            "category_type": txn_type,
            "category_name": category,
            "description": description,
            "amount": int(amount)
        }
        mclient["artha"]["transaction_data"].insert(tempObj)
        
        print("{0} - {1} - {2} - {3} - {4}".format(date, amount, txn_type, category, description))
        flash('New transaction added', category='success')
    return redirect(url_for('main.summary'))

@main.route('/uploadData')
@login_required
def uploadData():
    form1 = DataUploadForm()
    form3 = ModalNewTxnForm()
    
    exp_cat = helper.getCategoriesList("Expense", current_user)
    inc_cat = helper.getCategoriesList("Income", current_user)
    form3.category.choices = exp_cat + inc_cat
    
    return render_template('main/upload.html', title = 'Upload Data', form1 = form1, form3 = form3, snavid = "snav-2")

@main.route('/getUploadData', methods = ['GET', 'POST'])
@login_required
def updateData():
    if request.method == 'POST':
        f1 = request.files['dailyFile']
        f2 = request.files['mfFile']
        f3 = request.files['eqFile']
        
        if f1.filename != '':
            f1.save(os.path.join('appDir/user-content', current_app.config["DAILY_TXN_FILE_NAME"]))
            helper.updateDailyTxnData(current_user)
            flash("Transactions data updated!", category="success")
        if f2.filename != '':
            f2.save(os.path.join('appDir/user-content', current_app.config["MF_TXN_FILE_NAME"]))
            helper.updateMFTxnData(current_user)
            flash("Mutual funds data updated!", category="success")
        if f3.filename != '':
            f3.save(os.path.join('appDir/user-content', current_app.config["EQ_TXN_FILE_NAME"]))
        
        return redirect(url_for('main.uploadData'))

@main.route('/profile')
@login_required
def profile():    
    form1 = ModalUpdateTxnForm()
    form3 = ModalNewTxnForm()
    
    exp_cat = helper.getCategoriesList("Expense", current_user)
    inc_cat = helper.getCategoriesList("Income", current_user)
    form1.category.choices = exp_cat + inc_cat
    form3.category.choices = exp_cat + inc_cat
    
    current_page = request.args.get('page', 1, type=int)
    limit = current_app.config["TXNS_PER_PAGE"]
    skip = (current_page - 1)*limit
    txns = list(mclient["artha"]["transaction_data"].aggregate(helper.getPaginatePl(current_user, skip, limit)))
    
    try:
        list(mclient["artha"]["transaction_data"].aggregate(helper.getPaginatePl(current_user, skip+1, limit)))
        next_url = url_for('main.profile', page = current_page+1)
    except:
        next_url = None
    
    if current_page == 1:
        prev_url = None
    else:
        prev_url = url_for('main.profile', page = current_page-1)
    
    
    return render_template('main/profile.html', title='Profile', snavid = "snav-3", form1 = form1, form3 = form3, txns = txns, next_url = next_url, prev_url = prev_url)

@main.route('/modifyDeleteTxn/<txn_id>', methods = ['GET', 'POST'])
@login_required
def modifyDeleteTxn(txn_id):
    form = ModalUpdateTxnForm(request.form)
    exp_cat = helper.getCategoriesList("Expense", current_user)
    inc_cat = helper.getCategoriesList("Income", current_user)
    form.category.choices = exp_cat + inc_cat
    
    local_tz = pytz.timezone(current_user.timezone)
    
    if request.method=="POST":
        date = form.date.data
        txn_type = form.txn_type.data
        amount = form.amount.data
        category = form.category.data
        description = form.description.data
                
        if 'update' in request.form:
            mclient["artha"]["transaction_data"].update_one({"_id": ObjectId(txn_id)}, 
                                                            {"$set": {"date": local_tz.localize(dt.datetime(date.year, date.month, date.day)).astimezone(UTC),
                                                            "category_type": txn_type,
                                                            "category_name": category,
                                                            "description": description,
                                                            "amount": int(amount)}})
        elif 'delete' in request.form:
            mclient["artha"]["transaction_data"].delete_one({"_id": ObjectId(txn_id)})
        
        print("{0} - {1} - {2} - {3} - {4}".format(date, amount, txn_type, category, description))
    
    return redirect(url_for('main.profile'))









































