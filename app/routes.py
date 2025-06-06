from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import Post, Group
from . import db
import os
from datetime import datetime
from flask import current_app

main = Blueprint('main', __name__)

# Home page: list all posts
@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

# Create a new post
@main.route('/create', methods=['GET', 'POST'])
def create_post():
    groups = Group.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        group_ids = request.form.getlist('groups')

        post = Post(title=title, content=content, timestamp=datetime.utcnow())
        
        for group_id in group_ids:
            group = Group.query.get(group_id)
            if group:
                post.groups.append(group)

        # Handle file uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            upload_dir = os.path.join(current_app.instance_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)

        db.session.add(post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_post.html', groups=groups)
