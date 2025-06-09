from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import Post, Group
from . import db
import os
from datetime import datetime
from flask import current_app
from .forms import PostForm

main = Blueprint('main', __name__)

# Home page: list all posts
@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

# Create a new post
@main.route('/create', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_filenames = []
        for image in form.images.data:
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filenames.append(filename)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image_filenames=",".join(image_filenames)
        )
        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for('main.index'))

    return render_template('create_post.html', form=form)
