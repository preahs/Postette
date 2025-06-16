from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .forms import SetupForm, LoginForm, RequestPasswordResetForm, ResetPasswordForm
from .email_utils import send_verification_email, send_password_reset_email
import logging
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_verified:
            flash('Please verify your email before logging in. Check your email for the verification link.', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        flash('Logged in successfully.', 'success')
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/setup', methods=['GET', 'POST'])
def setup():
    if User.query.first():
        flash("Setup is already completed. Please log in.", "info")
        return redirect(url_for('auth.login'))

    form = SetupForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                newsletter_title=form.newsletter_title.data
            )
            db.session.add(user)
            db.session.commit()
            
            send_verification_email(user)
            flash("Account created successfully. Please check your email to verify your account.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            current_app.logger.exception("Full traceback:")
            flash(f"An error occurred while creating the user: {str(e)}", "danger")
            return render_template('setup.html', form=form)

    return render_template('setup.html', form=form)

@auth.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user is None:
        flash('Invalid verification token.', 'danger')
        return redirect(url_for('auth.login'))
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    flash('Your email has been verified. You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            send_password_reset_email(user)
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('request_password_reset.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    if user is None or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired password reset token.', 'danger')
        return redirect(url_for('auth.request_password_reset'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

