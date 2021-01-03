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
from tabula import read_pdf
from flask import current_app
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

def updateDailyTxnData(cUser):
    local_tz = pytz.timezone(cUser.timezone)
    txnDat = pd.read_excel('appDir/user-content/' + current_app.config["DAILY_TXN_FILE_NAME"], None)
    temp = pd.DataFrame()
    
    for ii in txnDat.keys():
        temp = temp.append(txnDat[ii].iloc[7:-3, 2:], ignore_index = True)
    
    temp.columns = ['Date', 'Category Type', 'Category Name', 'Note', 'Amount']
    txnDat = temp.copy()
    del temp
    
    mclient["artha"]["transaction_data"].drop()
    buffer = []
    for ii in range(txnDat.shape[0]):
        tempObj = {
            "email": cUser.email,
            "date": local_tz.localize(dt.datetime.strptime(txnDat.iloc[ii, 0], '%d %b %Y')).astimezone(UTC),
            "category_type": txnDat.iloc[ii, 1],
            "category_name": txnDat.iloc[ii, 2],
            "description": txnDat.iloc[ii, 3],
            "amount": txnDat.iloc[ii, 4]
        }
        buffer.append(tempObj)

    mclient["artha"]["transaction_data"].insert_many(buffer)

def joinRowStr(df):
    tabStr = ''
    for ii in range(df.shape[1]):
        try:
            np.isnan(df.iloc[0, ii])
        except:
            tabStr += df.iloc[0, ii]
        else:
            continue
    
    return tabStr

def getNum(amt):
    if amt == '':
        return 0
    elif amt[0] == '(':
        return -1*float(amt[1:-1].replace(',', ''))
    else:
        return float(amt.replace(',', ''))

def checkNaN(num):
    if np.isnan(num):
        return 0
    else:
        return num

def updateMFTxnData(cUser):
    local_tz = pytz.timezone(cUser.timezone)
    pdfName = r'appDir/user-content/' + current_app.config["MF_TXN_FILE_NAME"]
    df = read_pdf(pdfName, columns = [70.5,333,375,433,492], stream=True, guess = False, pages = 'all', password = current_app.config["MF_STATEMENT_PWD"])
    
    #####
    txnsDf = pd.DataFrame()
    for ii in range(len(df)):
        temp = df[ii]
        txnsDf = txnsDf.append(temp)
    
    txnsDf = txnsDf.reset_index(drop = True).applymap(str)
    txnsDf.columns = list(np.arange(txnsDf.shape[1]))
    txnsDf.drop(txnsDf[txnsDf.iloc[:, 0].str.contains('CAMSCASW')].index, inplace = True)
    txnsDf = txnsDf.reset_index(drop = True)
    
    regex = r'Folio No:.*?'
    div = txnsDf.iloc[:, 0].str.contains(regex)
    div = div.replace(np.nan, False)
    temp = txnsDf[div]
    
    folioIdx = list(temp.index)
    folioData = {}
    jj = 0
    
    for ii in range(len(folioIdx)):
        if ii != len(folioIdx) - 1:
            folioData[jj] = txnsDf.iloc[folioIdx[ii]:folioIdx[ii+1], :]
        else:
            folioData[jj] = txnsDf.iloc[folioIdx[ii]:, :]
        
        jj += 1
    
    #####
    fundDetails = pd.DataFrame(columns = ['Folio Num', 'Fund Name', 'As on Date', 
                                      'Closing Unit Balance', 'NAV', 'Total Investment',
                                      'Total Value', 'Investing Since'])
    objects = []
    
    for ii in folioData.keys():
        temp = folioData[ii]
        
        folioNumReg = r'Folio No:.*?'
        t1 = temp[temp.iloc[:, 0].str.contains(folioNumReg).replace(np.nan, False)]
        folioNum = t1.iloc[0, 0] + t1.iloc[0, 1]
        folioNumReg = r'Folio No: ([0-9/ ]+)'
        folioNum = re.match(folioNumReg, folioNum).group(1).replace(' ', '')
        
        folioIdx = list(t1.index)[0]
        fundName = (temp.loc[folioIdx + 1, 0] + temp.loc[folioIdx + 1, 1] + 
                    temp.loc[folioIdx + 1, 2] + temp.loc[folioIdx + 1, 3] + 
                    temp.loc[folioIdx + 1, 4]).replace('nan', '')
        fundNameReg = r'(?P<fName>[0-9a-zA-Z\- /\'\&]*).*?\(Advisor:.*?'
        fundStr = re.search(fundNameReg, fundName)
        fundName = fundStr.group('fName')
        
        asOnReg = r'Closing Unit B'
        t2 = temp[temp.iloc[:, 0].str.contains(asOnReg).replace(np.nan, False)]
        t2 = joinRowStr(t2).replace('nan', ' ')
        asOnReg = r'Closing Unit Balance: (?P<CUB>(\d*?,)*\d*\.\d{2,4}) NAV on (?P<asOnDate>\d\d-\w\w\w-\d\d\d\d): INR (?P<NAV>(\d*?,)*\d*\.\d{2,4})( )*?Valuation on.*?: INR (?P<val>(\d*?,)*\d*\.\d{2,4})'
        balStr = re.search(asOnReg, t2)
        closeUnitBal = balStr.group('CUB')
        asOnDate = dt.datetime.strptime(balStr.group('asOnDate'), "%d-%b-%Y").strftime("%d %b'%y")
        nav = balStr.group('NAV')
        totVal = balStr.group('val')
        
        txnReg = r'\d\d-\w\w\w-\d\d\d\d'
        t3 = temp[temp.iloc[:, 0].str.contains(txnReg)]
        t3.columns = ['Date', 'Txn Type', 'Amount (INR)', 'Units', 'NAV (INR)', 'Unit Balance']
        t3.loc[:, 'Amount (INR)'] = t3.loc[:, 'Amount (INR)'].apply(lambda x: getNum(x))
        t3.loc[:, 'Units'] = t3.loc[:, 'Units'].apply(lambda x: getNum(x))
        t3.loc[:, 'NAV (INR)'] = t3.loc[:, 'NAV (INR)'].apply(lambda x: getNum(x))
        t3.loc[:, 'Unit Balance'] = t3.loc[:, 'Unit Balance'].apply(lambda x: getNum(x))
        t3.loc[:, 'Date'] = t3.loc[:, 'Date'].apply(lambda x: local_tz.localize(dt.datetime.strptime(x, '%d-%b-%Y')))
        folioData[ii] = t3.reset_index(drop = True).replace('nan', '').copy()
        
        totInvestment = t3['Amount (INR)'].sum()
        investingSince = t3['Date'].iloc[0]
        fundDetails.loc[ii] = [folioNum, fundName, asOnDate, closeUnitBal, nav, totInvestment, totVal, investingSince]
        tempObj = {
            "email": cUser.email,
            "fund_name": fundName,
            "folio_number": folioNum,
            "as_on_date": asOnDate,
            "unit_balance": float(closeUnitBal.replace(",", "")),
            "nav": float(nav.replace(",", "")),
            "investing_since": investingSince
            }
        
        buffer = []
        for ii in range(t3.shape[0]):
            buffer.append({
                "date": t3.iloc[ii, 0],
                "description": t3.iloc[ii, 1],
                "amount": checkNaN(t3.iloc[ii, 2]),
                "units": checkNaN(t3.iloc[ii, 3]),
                "nav": checkNaN(t3.iloc[ii, 4]),
                "cumulative_units": checkNaN(t3.iloc[ii, 5])
                })
        
        tempObj["events"] = buffer
        objects.append(tempObj)
        mclient["artha"]["mf_data"].insert(tempObj)



























