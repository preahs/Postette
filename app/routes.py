from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import Post, Group
from . import db, mail
from .forms import PostForm
from flask_mail import Message
import os
from werkzeug.datastructures import FileStorage

main = Blueprint('main', __name__)

@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@main.route('/create', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    form.groups.choices = [(g.id, g.name) for g in Group.query.all()]

    if form.validate_on_submit():
        image_filenames = []

        for image in form.images.data:
            # Ensure we're only processing file uploads
            if isinstance(image, FileStorage) and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_filenames.append(filename)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image_filenames=",".join(image_filenames)
        )
        post.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()

        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for('main.index'))

    return render_template('create_post.html', form=form)

@main.route('/send/<int:post_id>')
def send_newsletter(post_id):
    post = Post.query.get_or_404(post_id)
    recipients = []
    for group in post.groups:
        recipients += [email.strip() for email in group.emails.split(',') if email.strip()]
    recipients = list(set(recipients))

    if not recipients:
        flash("No recipients found for this post.", "warning")
        return redirect(url_for('main.index'))

    msg = Message(subject=f"Newsletter: {post.title}",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=recipients)

    images_html = ""
    if post.image_filenames:
        for filename in post.image_filenames.split(','):
            images_html += f'<p><img src="{request.url_root}static/uploads/{filename.strip()}" style="max-width: 100%;"></p>'

    msg.html = f"""
        <h2>{post.title}</h2>
        <p>{post.content.replace('\n', '<br>')}</p>
        {images_html}
        <p><small>Sent via Verba</small></p>
    """

    mail.send(msg)
    flash("Newsletter sent!", "success")
    return redirect(url_for('main.index'))
