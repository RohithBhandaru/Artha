#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 17:32:12 2020

@author: rohithbhandaru
"""


import os
import re
import pytz
import json
import numpy as np
import pandas as pd
import datetime as dt
# from tabula import read_pdf
from pymongo import MongoClient
from sqlalchemy import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from appDir import create_app, db, mclient
from appDir.models import User, MFPortfolio

app = create_app(os.getenv("FLASK_CONFIG") or "default")
app.app_context().push()
mclient = MongoClient("mongodb://localhost:27017")

UTC = pytz.utc

def toJson(df):
    df = df.to_dict(orient = 'records')
    df = json.dumps(df)
    df = {'graph_data': df}
    
    return df

def monthlyTxnDatPl(local_month_year, email):
    return [
        {"$match": {"date": {"$gte": local_month_year, "$lt": local_month_year + relativedelta(months=+1)}, "email": email}},
        {"$project": {"_id": "$_id", "type": "$category_type", "name": "$category_name", "amount": "$amount"}},
        {"$group": {"_id": {"Type": "$type", "Name": "$name"}, "Amount": {"$sum": "$amount"}, "Number": {"$sum": 1}}},
        {"$sort": {"_id.type": 1, "Amount": 1}}
        ]

def monthlyTxnDatSummaryPl(local_month_year, email):
    return [
        {"$match": {"date": {"$gte": local_month_year, "$lt": local_month_year + relativedelta(months=+1)}, "email": email}},
        {"$project": {"_id": "$_id", "type": "$category_type", "amount": "$amount"}},
        {"$group": {"_id": {"Type": "$type"}, "Amount": {"$sum": "$amount"}}},
        {"$sort": {"_id.type": 1, "totAmount": 1}}
        ]

def convertToDf(data, columns):
    dfData = pd.DataFrame(columns = columns)
    
    for ii in range(len(data)):
        for jj in columns:
            if jj == "Type" or jj == "Name":
                dfData.loc[ii, jj] = data[ii]['_id'][jj]
            else:
                dfData.loc[ii, jj] = data[ii][jj]
    
    month_num = {"income": dfData.loc[dfData['Type'] == 'Income', "Amount"].sum(axis = 0),
                 "expense": dfData.loc[dfData['Type'] == 'Expense', "Amount"].sum(axis = 0)}
    
    return dfData, month_num

def getMonthlyTxnData(local_month_year, cUser):
    data1 = list(mclient["artha"]["transaction_data"].aggregate(monthlyTxnDatPl(local_month_year, cUser.email)))    
    data2 = list(mclient["artha"]["transaction_data"].aggregate(monthlyTxnDatSummaryPl(local_month_year + relativedelta(months=-1), cUser.email)))
    
    columns1 = ['Type', 'Name', 'Amount', 'Number']
    columns2 = ['Type', 'Amount']
    
    dfData1, current_month_num = convertToDf(data1, columns1)
    dfData2, last_month_num = convertToDf(data2, columns2)
    
    current_month_num["income-mom-percent"] = ((current_month_num["income"]/last_month_num["income"]) - 1)*100
    current_month_num["expense-mom-percent"] = ((current_month_num["expense"]/last_month_num["expense"]) - 1)*100
    
    dfData_e = toJson(dfData1[dfData1['Type'] == 'Expense'])
    dfData_i = toJson(dfData1[dfData1['Type'] == 'Income'])
    
    return dfData_e, dfData_i, current_month_num

current_user = User.query.filter(User.email == "rohith@temp.com").all()[0]
local_tz = pytz.timezone("Asia/Kolkata")
local_month_year = local_tz.localize(dt.datetime(2020, 12, 1))

a = list(mclient["artha"]["transaction_data"].aggregate([{"$match": {"date": {"$gte": local_month_year, "$lt": local_month_year + relativedelta(months=+1)}}}]))

txn_E, txn_I, monthly_num = getMonthlyTxnData(local_month_year, current_user)

















