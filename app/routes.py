from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import Post
from . import db, mail
from .forms import PostForm
from flask_mail import Message
from werkzeug.datastructures import FileStorage
import os
from .models import Post, Subscriber
from .forms import PostForm, SubscribeForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@main.route('/create', methods=['GET', 'POST'])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        image_filenames = []

        # Safely iterate only if form.images.data is a list
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
def newsletter_preview():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    return render_template('newsletter_preview.html', posts=posts)

@main.route('/send-newsletter', methods=['POST'])
def send_newsletter():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    if not posts:
        flash("No new posts to send.", "warning")
        return redirect(url_for('main.index'))

    # You can replace this with DB-driven recipients later
    recipients = [s.email for s in Subscriber.query.all()]
    if not recipients:
        flash("No subscribers found. Cannot send newsletter.", "danger")
        return redirect(url_for('main.index'))

    images_html = ""
    for post in posts:
        images_html += f"<h2>{post.title}</h2><p>{post.content.replace(chr(10), '<br>')}</p>"
        for filename in post.image_filenames.split(','):
            if filename.strip():
                images_html += f'<p><img src="{request.url_root}static/uploads/{filename.strip()}" style="max-width: 100%;"></p>'

    msg = Message(
        subject="Preah's Newsletter",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients,
        html=f"""
            {images_html}
            <p><small>Sent via Verba</small></p>
        """
    )

    mail.send(msg)

    for post in posts:
        post.sent = True
    db.session.commit()

    flash("Newsletter sent successfully!", "success")
    return redirect(url_for('main.index'))

@main.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Delete image files
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

@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
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
