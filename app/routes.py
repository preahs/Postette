from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import Post, Subscriber
from . import db, mail
from .forms import PostForm, SubscribeForm
from flask_mail import Message
from werkzeug.datastructures import FileStorage
from email.utils import make_msgid
import os
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        image_filenames = []

        if form.images.data:
            for image in form.images.data:
                if isinstance(image, FileStorage) and image.filename:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_filenames.append(filename)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image_filenames=",".join(image_filenames) if image_filenames else ""
        )

        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for('main.index'))

    return render_template('create_post.html', form=form)

@main.route('/newsletter-preview')
@login_required
def newsletter_preview():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    return render_template('newsletter_preview.html', posts=posts)

@main.route('/send-newsletter', methods=['POST'])
@login_required
def send_newsletter():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    if not posts:
        flash("No new posts to send.", "warning")
        return redirect(url_for('main.index'))

    recipients = [s.email for s in Subscriber.query.all()]
    if not recipients:
        flash("No subscribers found. Cannot send newsletter.", "danger")
        return redirect(url_for('main.index'))

    html_body = "<h3>This is an automated newsletter. You can reply to this email and the sender will see it. Please do not Reply All, or else everyone will see your response!</h3>"
    attachments = []

    for post in posts:
        html_body += f"<h2>{post.title}</h2>"
        html_body += f"<p>{post.content.replace(chr(10), '<br>')}</p>"

        if post.image_filenames:
            for filename in post.image_filenames.split(','):
                filename = filename.strip()
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                if os.path.exists(image_path):
                    cid = make_msgid(domain="postette.local")
                    html_body += f'<img src="cid:{cid[1:-1]}" style="max-width: 100%;"><br>'
                    attachments.append((cid[1:-1], image_path))

    html_body += "<p><small>Sent via Postette</small></p>"

    msg = Message(
        subject="Preah's Newsletter",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients,
        html=html_body
    )

    for cid, path in attachments:
        with open(path, 'rb') as img:
            msg.attach(
                filename=os.path.basename(path),
                content_type="image/jpeg",
                data=img.read(),
                headers={
                    'Content-ID': f'<{cid}>',
                    'Content-Disposition': 'inline'
                }
            )

    mail.send(msg)

    for post in posts:
        post.sent = True
    db.session.commit()

    flash("Newsletter sent successfully!", "success")
    return redirect(url_for('main.index'))

@main.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.image_filenames:
        for filename in post.image_filenames.split(','):
            if filename.strip():
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
                if os.path.exists(image_path):
                    os.remove(image_path)

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for('main.index'))

@main.route('/generate-invite', methods=['POST'])
@login_required
def generate_invite():
    token = current_app.token_serializer.dumps('invite')
    invite_link = url_for('main.subscribe_with_token', token=token, _external=True)
    flash(f"Invite link generated: {invite_link}")
    return redirect(url_for('main.index'))

@main.route('/subscribe/<token>', methods=['GET', 'POST'])
def subscribe_with_token(token):
    form = SubscribeForm()

    try:
        data = current_app.token_serializer.loads(token, max_age=86400)
        if data != 'invite':
            raise ValueError("Invalid token payload")
    except Exception:
        flash("This invite link is invalid or has expired.", "danger")
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        email = form.email.data
        existing = Subscriber.query.filter_by(email=email).first()
        if existing:
            flash("You're already subscribed!", "info")
        else:
            new_subscriber = Subscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash("Subscribed successfully!", "success")
        return redirect(url_for('main.index'))

    return render_template('subscribe.html', form=form)

@main.route('/delete-sent-posts', methods=['POST'])
@login_required
def delete_sent_posts():
    sent_posts = Post.query.filter_by(sent=True).all()
    upload_folder = current_app.config['UPLOAD_FOLDER']

    for post in sent_posts:
        if post.image_filenames:
            for filename in post.image_filenames.split(','):
                filepath = os.path.join(upload_folder, filename.strip())
                if os.path.exists(filepath):
                    os.remove(filepath)

        db.session.delete(post)

    db.session.commit()
    flash('All sent posts and their images have been deleted.', 'success')
    return redirect(url_for('main.index'))
