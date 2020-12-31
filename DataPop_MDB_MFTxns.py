#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 13:08:48 2020

@author: rohithbhandaru
"""


import re
import pytz
import numpy as np
import pandas as pd
import datetime as dt
from pymongo import MongoClient
from tabula import read_pdf


IST = pytz.timezone("Asia/Kolkata")
client = MongoClient('mongodb://localhost:27017')
db = client["artha"]
collection = db["mf_data"]

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

pdfName = r'appDir/user-content/MF Txns.pdf'
df = read_pdf(pdfName, columns = [70.5,333,375,433,492], stream=True, guess = False, pages = 'all', password = 'Asia@1996')

#%%
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

#%%
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
    t3.loc[:, 'Date'] = t3.loc[:, 'Date'].apply(lambda x: IST.localize(dt.datetime.strptime(x, '%d-%b-%Y')))
    folioData[ii] = t3.reset_index(drop = True).replace('nan', '').copy()
    
    totInvestment = t3['Amount (INR)'].sum()
    investingSince = t3['Date'].iloc[0]
    fundDetails.loc[ii] = [folioNum, fundName, asOnDate, closeUnitBal, nav, totInvestment, totVal, investingSince]
    tempObj = {
        "email": "rohith@temp.com",
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
    collection.insert(tempObj)
    
    
# ActiveFunds = fundDetails[fundDetails['Total Value'] != '0.00']
# ActiveFunds.loc[:, 'Closing Unit Balance'] = ActiveFunds.loc[:, 'Closing Unit Balance'].apply(lambda x: getNum(x))
# ActiveFunds.loc[:, 'NAV'] = ActiveFunds.loc[:, 'NAV'].apply(lambda x: getNum(x))
# ActiveFunds.loc[:, 'Total Value'] = ActiveFunds.loc[:, 'Total Value'].apply(lambda x: getNum(x))
# ActiveFunds = ActiveFunds.groupby(['Fund Name']).agg({'As on Date': max, 'Closing Unit Balance': 'sum', 'NAV': max, 'Total Investment': 'sum', 'Total Value': 'sum', 'Investing Since': min}).reset_index()
# ActiveFunds['P&L'] = ActiveFunds['Total Value'] - ActiveFunds['Total Investment']
# ActiveFunds['P&L %'] = ActiveFunds['P&L']*100/ActiveFunds['Total Investment']
# ActiveFunds = ActiveFunds.sort_values(by = ['P&L %'], ascending = False).reset_index(drop = True)


#%%
# mdb_cl = pymongo.MongoClient(Config.MONGO_URI)
# mdb_cl[Config.MONGO_DB]['mf_data'].drop()
# for ii in folioData.keys():
#     temp = folioData[ii]
#     for jj in range(temp.shape[0]):
#         tempObj = MFTxnData(**{
#             "email": 'bhandarurohith@gmail.com',
#             "folio_num": fundDetails.loc[ii, 'Folio Num'],
#             "fund_name": fundDetails.loc[ii, 'Fund Name'],
#             "date": dt.datetime.strptime(temp.loc[jj, 'Date'], '%d-%b-%Y'),
#             "txn_type": temp.loc[jj, 'Txn Type'],
#             "amount": temp.loc[jj, 'Amount (INR)'],
#             "units": temp.loc[jj, 'Units'],
#             "nav": temp.loc[jj, 'NAV (INR)'],
#             "unit_balance": temp.loc[jj, 'Unit Balance']
#             })
#         MFTxnData.objects.insert(tempObj)

# me.disconnect_all()

#%%
# num_rows = db.session.query(MFPortfolio).delete()
# for ii in range(ActiveFunds.shape[0]):
#     fund = MFPortfolio(email = 'bhandarurohith@gmail.com',
#                         fund_name = ActiveFunds.loc[ii, 'Fund Name'],
#                         folio_num = ActiveFunds.loc[ii, 'Folio Num'],
#                         as_on_date = dt.datetime.strptime(ActiveFunds.loc[ii, 'As on Date'], '%d-%b-%Y'),
#                         cub = ActiveFunds.loc[ii, 'Closing Unit Balance'],
#                         nav = ActiveFunds.loc[ii, 'NAV'],
#                         total_investment = ActiveFunds.loc[ii, 'Total Investment'])
#     db.session.add(fund)
        # db.session.query().filter(MFPortfolio.folio_num == ActiveFunds.loc[ii, 'Folio Num']).update({
        #     'as_on_date': dt.datetime.strptime(ActiveFunds.loc[ii, 'As on Date'], '%d-%b-%Y'),
        #     'cub': ActiveFunds.loc[ii, 'Closing Unit Balance'],
        #     'nav': ActiveFunds.loc[ii, 'NAV'],
        #     'total_investment': ActiveFunds.loc[ii, 'Total Investment']
        #     })
    # except:
    #     fund = MFPortfolio(email = 'bhandarurohith@gmail.com',
    #                         fund_name = ActiveFunds.loc[ii, 'Fund Name'],
    #                         folio_num = ActiveFunds.loc[ii, 'Folio Num'],
    #                         as_on_date = dt.datetime.strptime(ActiveFunds.loc[ii, 'As on Date'], '%d-%b-%Y'),
    #                         cub = ActiveFunds.loc[ii, 'Closing Unit Balance'],
    #                         nav = ActiveFunds.loc[ii, 'NAV'],
    #                         total_investment = ActiveFunds.loc[ii, 'Total Investment'])
    #     db.session.add(fund)

# db.session.commit()
#%%

# def getMFDataPl(cUser):
#     return [
#         {"$match": {"email": 'bhandarurohith@gmail.com', "amount":{"$ne": np.nan}}},
#         {"$project": {"_id": "$_id", "amount": "$amount", "date": "$date"}},
#         {"$sort": {"date": 1}}
#         ]

# dat = list(MFTxnData.objects().aggregate(getMFDataPl(1)))
# dfDat = pd.DataFrame(columns = ['Amount', 'Date'])

# for ii in range(len(dat)):
#     dfDat.loc[ii] = [dat[ii]['amount'], dat[ii]['date']]
    

# allTxns = pd.DataFrame()
# for ii in folioData.keys():
#     allTxns = allTxns.append(folioData[ii].iloc[:, [0,2]])

# allTxns = allTxns.dropna()
# a = dfDat.groupby('Date').sum()
# a.index = pd.to_datetime(a.index)
# a = a.sort_values(by = ['Date'])
# # a['Cum Sum'] = a.cumsum()

# value = pd.DataFrame()
# for ii in folioData.keys():
#     temp = folioData[ii].iloc[:, [0, 3, 4]]











































