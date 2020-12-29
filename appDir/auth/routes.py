# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 13:49:59 2020
@author: RohithBhandaru
"""

import datetime as dt
from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required

from . import auth
from .forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    ChangePasswordForm,
)
from .. import db
from ..email import send_email
from ..models import User

##################################
##################################
##################################
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.summary'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.summary')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Log In', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


##################################
##################################
##################################
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.summary'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            email=form.email.data,
            registered_on=dt.datetime.utcnow(),
            confirmed=False,
            status="Active",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # token = user.generate_confirmation_token()
        # send_email(
        #     "[Artha] Confirm Your Account",
        #     sender=current_app.config["ADMINS"][0],
        #     recipients=[user.email],
        #     text_body=render_template(
        #         "auth/email/confirmAccount.txt", user=user, token=token
        #     ),
        #     html_body=render_template(
        #         "auth/email/confirmAccount.html", user=user, token=token
        #     ),
        # )

        flash(
            "A confirmation email has been sent to you by email. This email is valid only for 1 hour.",
            category="success",
        )
        
        current_app.logger.info("New user registered - {0}".format(form.email.data))
        
        return redirect(url_for('auth.login'))
    
    return render_template("auth/register.html", title="Register", form=form)


@auth.route("/confirm-account/<token>", methods=["GET", "POST"])
@login_required
def confirmAccount(token):
    if current_user.confirmed:
        return redirect(url_for("main.summary"))

    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!", category="success")
    else:
        flash("The confirmation link is invalid or has expired.", category="danger")

    return redirect(url_for("auth.login"))


@auth.route("/confirm-account")
@login_required
def resendConfirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        "[Artha] Confirm Your Account",
        sender=current_app.config["ADMINS"][0],
        recipients=[current_user.email],
        text_body=render_template(
            "auth/email/confirmAccount.txt", user=current_user, token=token
        ),
        html_body=render_template(
            "auth/email/confirmAccount.html", user=current_user, token=token
        ),
    )
    flash("A new confirmation email has been sent to you by email.", category="success")
    return render_template("auth/unconfirmedAccount.html", user=current_user)



##################################
##################################
##################################
@auth.route("/reset-password", methods=["GET", "POST"])
def resetPasswordRequest():
    if current_user.is_authenticated:
        return redirect(url_for("main.summary"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            token = user.generate_reset_token()
            send_email(
                "[Artha] Reset Your Password",
                sender=current_app.config["ADMINS"][0],
                recipients=[user.email],
                text_body=render_template(
                    "auth/email/resetPassword.txt", user=user, token=token
                ),
                html_body=render_template(
                    "auth/email/resetPassword.html", user=user, token=token
                ),
            )

            flash(
                "An email with instructions to reset your password has been sent to you.",
                category="success",
            )
        else:
            flash("No user with the given email exists.", category="danger")

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/resetPasswordRequest.html", title="Reset Password", form=form
    )


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.summary"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password has been updated.", category="success")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.summary"))

    return render_template("auth/resetPassword.html", title="Reset Password", form=form)


##################################
##################################
##################################
@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash("Password successfully changed", category="success")
            current_app.logger.info(
                "{0} - Password changed".format("[User - " + current_user.email + "]")
            )
        else:
            flash("Invalid password.", category="danger")

    return redirect(url_for("main.profile"))
