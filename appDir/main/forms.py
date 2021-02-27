#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 16:27:06 2020

@author: rohithbhandaru
"""


from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.fields.html5 import DateField
from wtforms import SubmitField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired


class MonthSelectForm(FlaskForm):
    selectMonth = DateField('Select Month', format='%Y-%m-%d')
    submit = SubmitField('Submit')


class CategorySelectForm(FlaskForm):
    selectCat = SelectField('Category')
    submit = SubmitField('Submit')


class DataUploadForm(FlaskForm):
    dailyFile = FileField('Daily Transactions Data')
    mfFile = FileField('Mutual Fund Transactions Data')
    eqFile = FileField('Equity Transactions Data')
    submit = SubmitField('Submit')


class ModalNewTxnForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount = DecimalField(places=2, validators=[DataRequired()])
    txn_type = SelectField('Type', choices=['Expense', 'Income'])
    category = SelectField('Category')
    description = TextAreaField('Comments')
    submit = SubmitField('Submit')


class ModalUpdateTxnForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount = DecimalField(places=2, validators=[DataRequired()])
    txn_type = SelectField('Type', choices=['Expense', 'Income'])
    category = SelectField('Category')
    description = TextAreaField('Comments')
    update = SubmitField('Update')
    delete = SubmitField('Delete')
