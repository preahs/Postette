from flask import current_app, render_template
from flask_mail import Message
from .extensions import mail

def send_verification_email(user):
    msg = Message(
        'Verify your email address',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    verification_url = f"{current_app.config['BASE_URL']}/verify-email/{user.verification_token}"
    msg.body = render_template('email/verify_email.txt', user=user, verification_url=verification_url)
    msg.html = render_template('email/verify_email.html', user=user, verification_url=verification_url)
    mail.send(msg)

def send_password_reset_email(user):
    msg = Message(
        'Reset your password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    reset_url = f"{current_app.config['BASE_URL']}/reset-password/{user.reset_token}"
    msg.body = render_template('email/reset_password.txt', user=user, reset_url=reset_url)
    msg.html = render_template('email/reset_password.html', user=user, reset_url=reset_url)
    mail.send(msg)
