from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from . import db, mail
from .forms import SetupForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_mail import Message
from datetime import datetime, timedelta
import secrets

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/setup', methods=['GET', 'POST'])
def setup():
    # Check if any user exists
    if User.query.first():
        flash("Setup is already completed. Please log in.", "info")
        return redirect(url_for('auth.login'))

    form = SetupForm()
    if form.validate_on_submit():
        try:
            verification_token = secrets.token_urlsafe(32)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                newsletter_title=form.newsletter_title.data,
                verification_token=verification_token
            )
            user.is_admin = True
            db.session.add(user)
            db.session.commit()

            # Send verification email
            verification_url = url_for('auth.verify_email', token=verification_token, _external=True)
            msg = Message(
                subject="Verify Your Email - Postette",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            msg.html = render_template('verify_user_email.html', verification_url=verification_url)
            mail.send(msg)

            flash("User created successfully. Please check your email to verify your account.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            current_app.logger.exception("Full traceback:")
            flash(f"An error occurred while creating the user: {str(e)}", "danger")
            return render_template('setup.html', form=form)

    return render_template('setup.html', form=form)

@auth.route('/auth/verify/<token>')
def verify_email(token):
    current_app.logger.info(f"Verifying email with token: {token}")
    user = User.query.filter_by(verification_token=token).first()
    current_app.logger.info(f"User found: {user}")
    
    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Email already verified.', 'info')
        return redirect(url_for('auth.login'))
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    flash('Email verified successfully. You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            # Send reset email
            reset_url = url_for('auth.reset_password', token=user.reset_token, _external=True)
            msg = Message(
                subject="Reset Your Password - Postette",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            msg.html = render_template('reset_password_email.html', reset_url=reset_url)
            mail.send(msg)

        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', form=form)

