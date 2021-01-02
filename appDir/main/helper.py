#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 16:52:11 2020

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
from sqlalchemy import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from .. import db, mclient
from ..models import MFPortfolio

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

def getCategoriesList(catType, cUser):
    categoryPl = [
        {"$match": {"$and": [{"email": cUser.email}, {"category_type": catType}]}},
        {"$project": {"category_name": "$category_name"}}
        ]
    
    categories = list(mclient["artha"]["transaction_data"].aggregate(categoryPl))
    categories = list(set([ii["category_name"] for ii in categories]))
    categories.sort()
    
    return categories

def getCatHistoryPl(category, cUser):
    return [
       {"$match": {"category_name": category, "email": cUser.email}},
        {"$project": {"_id": "$_id", "date": "$date", "amount": "$amount"}},
        {"$group": {"_id": {"month": {"$month": {"date": "$date", "timezone": cUser.timezone}}, "year": {"$year": {"date": "$date", "timezone": cUser.timezone}}}, "totAmount": {"$sum": "$amount"}, "numTxn": {"$sum": 1}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
       ]

def getCategoryHistoryData(category, cUser):
    dat = list(mclient["artha"]["transaction_data"].aggregate(getCatHistoryPl(category, cUser)))
    
    sDate = dt.date(dat[0]['_id']['year'], dat[0]['_id']['month'], 1).strftime('%Y-%m-%d')
    eDate = dt.date(dat[-1]['_id']['year'], dat[-1]['_id']['month'], 1).strftime('%Y-%m-%d')
    monthrange = pd.date_range(sDate, eDate, freq='MS').tolist()
    
    dfDat = pd.DataFrame(0, columns = ['Amount', 'Number'], index = monthrange)
    
    for ii in range(len(dat)):
        dfDat.loc[dt.datetime(dat[ii]['_id']['year'], dat[ii]['_id']['month'], 1)] = [dat[ii]['totAmount'], dat[ii]['numTxn']]
    
    dfDat['Month'] = dfDat.index.to_series().apply(lambda x: x.month)
    dfDat['Year'] = dfDat.index.to_series().apply(lambda x: x.year)
    dfDat = dfDat[['Month', 'Year', 'Amount', 'Number']]
    dfDat = toJson(dfDat)
    
    return dfDat

def getMFPortfolioPl(cUser):
    return [
        {"$match": {"$and": [{"email": cUser.email}, {"unit_balance": {"$ne": 0}}, {"events.amount": {"$ne": np.nan}}]}},
            {"$project": {"as_on_date": "$as_on_date",
                    "folio_number": "$folio_number",
                    "fund_name": "$fund_name",
                    "investing_since": "$investing_since",
                    "nav": "$nav",
                    "total_invested": {"$sum": "$events.amount"},
                    "unit_balance": "$unit_balance"}}
            ]

def getMFPortfolio(cUser, local_tz):
    funds = list(mclient["artha"]["mf_data"].aggregate(getMFPortfolioPl(cUser)))
    funds = pd.DataFrame([(f["fund_name"], f["folio_number"], f["as_on_date"], f["unit_balance"], f["nav"], f["total_invested"], UTC.localize(f["investing_since"]).astimezone(local_tz)) for f in funds], columns = ['Fund Name', 'Folio Num', 'As On Date', 'CUB', 'NAV', 'Total Investment', 'Investing Since'])
    funds.loc[:, 'Fund Name'] = funds.loc[:, 'Fund Name'].apply(lambda x: x.split('-')[1])
    funds['Total Value'] = funds['CUB']*funds['NAV']
    funds = funds.groupby(['Fund Name']).agg({'Folio Num': list, 'As On Date': max, 'CUB': 'sum', 'NAV': max, 'Total Investment': 'sum', 'Total Value': 'sum', 'Investing Since': min}).reset_index()
    funds['P&L'] = funds['Total Value'] - funds['Total Investment']
    funds['P&L %'] = funds['P&L']*100/funds['Total Investment']
    funds = funds.sort_values(by = ['P&L %'], ascending = False).reset_index(drop = True)
    
    return funds

def getFullMFDataPl(cUser):
    return [
        {"$match": {"email": cUser.email}},
        {"$unwind": "$events"},
        {"$project": {"_id": "$_id", "amount": "$events.amount", "date": "$events.date"}},
        {"$sort": {"date": 1}}
        ]

def getFullMFData(cUser):
    data = list(mclient["artha"]["mf_data"].aggregate(getFullMFDataPl(cUser)))
    dfDat = pd.DataFrame(columns = ['Amount', 'Date'])

    for ii in range(len(data)):
        dfDat.loc[ii] = [data[ii]['amount'], data[ii]['date']]
    
    dfDat = dfDat.groupby('Date').sum()
    dfDat.index = pd.to_datetime(dfDat.index)
    dfDat = dfDat.sort_values(by = ['Date'])
    dfDat = dfDat.cumsum().resample('1D').ffill().reset_index()
    dfDat = dfDat.dropna()
    dfDat['Date'] = dfDat['Date'].apply(lambda x: x.strftime("%d-%b-%Y"))
    dfDat = toJson(dfDat)
    
    return dfDat

def getPaginatePl(cUser, skip, limit):
    return [
      {"$match": {"email": cUser.email}},
      {"$project": {"_id": "$_id", "date": "$date", "type": "$category_type", "name": "$category_name", "description": "$description", "amount": "$amount"}},
      {"$sort": {"date": -1}},
      {"$skip": skip},
      {"$limit": limit}
      ]



























