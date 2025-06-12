from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .forms import SetupForm
import logging

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
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
            user = User(
                username=form.username.data,
                password_hash=generate_password_hash(form.password.data),
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()
            flash("User created successfully. Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            current_app.logger.exception("Full traceback:")
            flash(f"An error occurred while creating the user: {str(e)}", "danger")
            return render_template('setup.html', form=form)

    return render_template('setup.html', form=form)

