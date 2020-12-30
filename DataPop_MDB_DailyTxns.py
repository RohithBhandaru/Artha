#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 16:24:35 2020

@author: rohithbhandaru
"""


import pytz
import pandas as pd
import datetime as dt
from pymongo import MongoClient

txnDat = pd.read_excel('appDir/user-content/Daily Txns.xlsx', None)
temp = pd.DataFrame()

for ii in txnDat.keys():
    temp = temp.append(txnDat[ii].iloc[7:-3, 2:], ignore_index = True)

temp.columns = ['Date', 'Category Type', 'Category Name', 'Note', 'Amount']
txnDat = temp.copy()
del temp

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.utc

client = MongoClient('mongodb://localhost:27017')
db = client["artha"]
collection = db["transaction_data"]

#Upto 30 Dec 2020 have been updated
buffer = []
for ii in range(txnDat.shape[0]):
    tempObj = {
        "email": 'rohith@temp.com',
        "date": IST.localize(dt.datetime.strptime(txnDat.iloc[ii, 0], '%d %b %Y')).astimezone(UTC),
        "category_type": txnDat.iloc[ii, 1],
        "category_name": txnDat.iloc[ii, 2],
        "description": txnDat.iloc[ii, 3],
        "amount": txnDat.iloc[ii, 4]
    }
    buffer.append(tempObj)

collection.insert_many(buffer)
buffer = []

