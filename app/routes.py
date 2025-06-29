from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, abort
from werkzeug.utils import secure_filename
from .models import Post, Subscriber
from . import db, mail
from .forms import PostForm, SubscribeForm
from flask_mail import Message
from werkzeug.datastructures import FileStorage
from email.utils import make_msgid
from .utils import format_datetime
import os
from flask_login import login_required, current_user

MAX_TOTAL_IMAGE_SIZE_MB = 15
MAX_TOTAL_IMAGE_SIZE_BYTES = MAX_TOTAL_IMAGE_SIZE_MB * 1024 * 1024
MAX_TOTAL_VIDEO_SIZE_MB = 15
MAX_TOTAL_VIDEO_SIZE_BYTES = MAX_TOTAL_VIDEO_SIZE_MB * 1024 * 1024

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    posts = Post.query.filter_by(archived=False).order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@main.route('/archive')
@login_required
def archive():
    posts = Post.query.filter_by(archived=True).order_by(Post.timestamp.desc()).all()
    return render_template('archive.html', posts=posts)

@main.route('/archive-sent-posts', methods=['POST'])
@login_required
def archive_sent_posts():
    sent_posts = Post.query.filter_by(sent=True, archived=False).all()
    if not sent_posts:
        flash('No sent posts to archive.', 'info')
        return redirect(url_for('main.index'))
        
    for post in sent_posts:
        post.archived = True
    db.session.commit()
    flash('All sent posts have been archived.', 'success')
    return redirect(url_for('main.index'))

@main.route('/delete-all-archived', methods=['POST'])
@login_required
def delete_all_archived():
    archived_posts = Post.query.filter_by(archived=True).all()
    if not archived_posts:
        flash('No archived posts to delete.', 'info')
        return redirect(url_for('main.archive'))
        
    upload_folder = current_app.config['UPLOAD_FOLDER']

    for post in archived_posts:
        if post.image_filenames:
            for filename in post.image_filenames.split(','):
                filepath = os.path.join(upload_folder, filename.strip())
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        if post.video_filenames:
            for filename in post.video_filenames.split(','):
                filepath = os.path.join(upload_folder, filename.strip())
                if os.path.exists(filepath):
                    os.remove(filepath)

        db.session.delete(post)

    db.session.commit()
    flash('All archived posts and their media have been deleted.', 'success')
    return redirect(url_for('main.archive'))

@main.route('/restore/<int:post_id>', methods=['POST'])
@login_required
def restore_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.archived = False
    post.sent = False
    db.session.commit()
    flash('Post has been restored.', 'success')
    return redirect(url_for('main.archive'))

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        print("DEBUG: Form validation passed, processing submission")
        # Check total size of all media before saving
        total_size = 0
        MAX_TOTAL_SIZE = 15 * 1024 * 1024  # 15MB in bytes

        # Calculate total size of images
        if form.images.data:
            for image in form.images.data:
                if image:
                    image.seek(0, os.SEEK_END)
                    total_size += image.tell()
                    image.seek(0)

        # Calculate total size of videos
        if form.videos.data:
            for video in form.videos.data:
                if video:
                    video.seek(0, os.SEEK_END)
                    total_size += video.tell()
                    video.seek(0)

        if total_size > MAX_TOTAL_SIZE:
            flash(f'Total size of all media (images and videos) must be less than 15MB. Current size: {total_size / (1024 * 1024):.2f}MB', 'danger')
            return render_template('create_post.html', title='Create Post', form=form)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )

        # Handle image uploads
        if form.images.data:
            image_filenames = []
            for image in form.images.data:
                if image:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_filenames.append(filename)
            post.image_filenames = ','.join(image_filenames)

        # Handle video uploads
        if form.videos.data:
            video_filenames = []
            for video in form.videos.data:
                if video:
                    filename = secure_filename(video.filename)
                    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    video.save(video_path)
                    video_filenames.append(filename)
            post.video_filenames = ','.join(video_filenames)

        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.index'))
    else:
        print("DEBUG: Form validation failed")
        print(f"DEBUG: Form errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return render_template('create_post.html', title='Create Post', form=form)

@main.route('/newsletter-preview')
@login_required
def newsletter_preview():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    subscribers = Subscriber.query.filter_by(is_verified=True).order_by(Subscriber.created_at.desc()).all()
    return render_template('newsletter_preview.html', posts=posts, subscribers=subscribers)

@main.route('/send-newsletter', methods=['POST'])
@login_required
def send_newsletter():
    posts = Post.query.filter_by(sent=False).order_by(Post.timestamp.asc()).all()
    if not posts:
        flash("No new posts to send.", "warning")
        return redirect(url_for('main.index'))

    subscribers = Subscriber.query.filter_by(is_verified=True).all()
    if not subscribers:
        flash("No verified subscribers found. Cannot send newsletter.", "danger")
        return redirect(url_for('main.index'))

    html_body = "<p>This is an automated newsletter. You can reply to this email and the sender will see it. Please do not Reply All, or else everyone will see your response!</p>"
    attachments = []

    # Calculate total size of attachments for all posts in the newsletter
    current_newsletter_total_size = 0
    for post in posts:
        if post.image_filenames:
            for filename in post.image_filenames.split(','):
                filename = filename.strip()
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(image_path):
                    current_newsletter_total_size += os.path.getsize(image_path)
        
        if post.video_filenames:
            for filename in post.video_filenames.split(','):
                filename = filename.strip()
                video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(video_path):
                    current_newsletter_total_size += os.path.getsize(video_path)

    print(f"DEBUG: Pre-send check - Current newsletter total size: {current_newsletter_total_size / (1024 * 1024):.2f} MB")
    print(f"DEBUG: Pre-send check - MAX_TOTAL_IMAGE_SIZE_MB: {MAX_TOTAL_IMAGE_SIZE_MB} MB")
    if current_newsletter_total_size > MAX_TOTAL_IMAGE_SIZE_BYTES:
        flash(f'Total media size for this newsletter ({current_newsletter_total_size / (1024 * 1024):.2f} MB) exceeds the limit of {MAX_TOTAL_IMAGE_SIZE_MB}MB. Please reduce the number or size of media across your unsent posts.', 'danger')
        return redirect(url_for('main.newsletter_preview'))

    for i, post in enumerate(posts):
        if i > 0:  # Add divider before all posts except the first one
            html_body += '<hr style="border: none; border-top: 2px solid #eee; margin: 2em 0;">'
            
        html_body += f"<h2>{post.title}</h2>"
        html_body += f"<p style='color: #666; font-size: 0.9em;'>Posted on {format_datetime(post.timestamp)}</p>"
        html_body += f"<div style='margin-bottom: 1.5em;'>{post.content.replace(chr(10), '<br>')}</div>"

        if post.image_filenames:
            for filename in post.image_filenames.split(','):
                filename = filename.strip()
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                if os.path.exists(image_path):
                    cid = make_msgid(domain="postette.local")
                    html_body += f'<img src="cid:{cid[1:-1]}" style="max-width: 100%;"><br>'
                    attachments.append((cid[1:-1], image_path))

        if post.video_filenames:
            for filename in post.video_filenames.split(','):
                filename = filename.strip()
                video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                if os.path.exists(video_path):
                    cid = make_msgid(domain="postette.local")
                    html_body += f'<video src="cid:{cid[1:-1]}" style="max-width: 100%;" controls></video><br>'
                    attachments.append((cid[1:-1], video_path))

    html_body += "<p><small>Sent via Postette</small></p>"

    # Send email to all verified subscribers
    with mail.connect() as connection:
        for subscriber in subscribers:
            unsubscribe_url = url_for('main.unsubscribe', token=subscriber.unsubscribe_token, _external=True)
            subscriber_html = html_body + f'<p style="font-size: 0.8em; color: #666; margin-top: 2em; border-top: 1px solid #eee; padding-top: 1em;">To unsubscribe, <a href="{unsubscribe_url}">click here</a>.</p>'

            msg = Message(
                subject=current_user.newsletter_title,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[subscriber.email],
                html=subscriber_html
            )

            for cid, path in attachments:
                with open(path, 'rb') as media:
                    content_type = "image/jpeg" if path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')) else "video/mp4"
                    msg.attach(
                        filename=os.path.basename(path),
                        content_type=content_type,
                        data=media.read(),
                        headers=[('Content-ID', f'<{cid}>'), ('Content-Disposition', 'inline')]
                    )

            mail.send(msg)

    for post in posts:
        post.sent = True
    db.session.commit()

    flash("Newsletter sent successfully!", "success")
    return redirect(url_for('main.index'))

@main.route('/unsubscribe/<token>', methods=['GET', 'POST'])
def unsubscribe(token):
    subscriber = Subscriber.query.filter_by(unsubscribe_token=token).first()
    
    if not subscriber:
        return render_template('unsubscribe.html', error="Invalid or expired unsubscribe link.")
    
    if request.method == 'POST':
        db.session.delete(subscriber)
        db.session.commit()
        return render_template('unsubscribe.html', success=True)
    
    return render_template('unsubscribe.html')

@main.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Remove associated media files for the post
    if post.image_filenames:
        for filename in post.image_filenames.split(','):
            if filename.strip():
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
                if os.path.exists(image_path):
                    os.remove(image_path)
    if post.video_filenames:
        for filename in post.video_filenames.split(','):
            if filename.strip():
                video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
                if os.path.exists(video_path):
                    os.remove(video_path)

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for('main.index'))

@main.route('/generate-invite', methods=['POST'])
@login_required
def generate_invite():
    token = current_app.token_serializer.dumps('invite')
    invite_link = url_for('main.subscribe_with_token', token=token, _external=True)
    flash(invite_link, 'invite_link')
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
            if existing.is_verified:
                return render_template('subscribe.html', success=True, message="You're already subscribed!")
            else:
                # Resend verification email
                verification_url = url_for('main.verify_email', token=existing.verification_token, _external=True)
                msg = Message(
                    subject="Verify Your Email - Postette Newsletter",
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )
                msg.html = render_template('verify_email.html', verification_url=verification_url)
                mail.send(msg)
                return render_template('subscribe.html', success=True)
        else:
            new_subscriber = Subscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()

            # Send verification email
            verification_url = url_for('main.verify_email', token=new_subscriber.verification_token, _external=True)
            msg = Message(
                subject="Verify Your Email - Postette Newsletter",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            msg.html = render_template('verify_email.html', verification_url=verification_url)
            mail.send(msg)

            return render_template('subscribe.html', success=True)

    return render_template('subscribe.html', form=form)

@main.route('/verify/<token>')
def verify_email(token):
    subscriber = Subscriber.query.filter_by(verification_token=token).first()
    
    if not subscriber:
        return render_template('verify.html', success=False, 
                             error="Invalid or expired verification link.")
    
    if subscriber.is_verified:
        return render_template('verify.html', success=True)
    
    subscriber.is_verified = True
    subscriber.verification_token = None  # Clear the token after verification
    db.session.commit()
    
    return render_template('verify.html', success=True)

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

@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if post.sent:
        flash('Cannot edit a post that has already been sent.', 'danger')
        return redirect(url_for('main.index'))
        
    form = PostForm()

    # Prepare existing media data for client-side JavaScript
    existing_images_data = []
    existing_videos_data = []
    
    if post.image_filenames:
        for filename in post.image_filenames.split(','):
            if filename.strip():
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
                if os.path.exists(image_path):
                    existing_images_data.append({
                        'filename': filename.strip(),
                        'size': os.path.getsize(image_path)
                    })
    
    if post.video_filenames:
        for filename in post.video_filenames.split(','):
            if filename.strip():
                video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
                if os.path.exists(video_path):
                    existing_videos_data.append({
                        'filename': filename.strip(),
                        'size': os.path.getsize(video_path)
                    })

    if form.validate_on_submit():
        # Check total size of all media before saving
        total_size = 0
        MAX_TOTAL_SIZE = 15 * 1024 * 1024  # 15MB in bytes

        # Calculate size of existing media that will be kept
        remaining_existing_image_filenames = request.form.getlist('existing_images')
        remaining_existing_video_filenames = request.form.getlist('existing_videos')

        for filename in remaining_existing_image_filenames:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
            if os.path.exists(image_path):
                total_size += os.path.getsize(image_path)

        for filename in remaining_existing_video_filenames:
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.strip())
            if os.path.exists(video_path):
                total_size += os.path.getsize(video_path)

        # Calculate size of new media
        if form.images.data:
            for image in form.images.data:
                if image:
                    image.seek(0, os.SEEK_END)
                    total_size += image.tell()
                    image.seek(0)

        if form.videos.data:
            for video in form.videos.data:
                if video:
                    video.seek(0, os.SEEK_END)
                    total_size += video.tell()
                    video.seek(0)

        if total_size > MAX_TOTAL_SIZE:
            flash(f'Total size of all media (images and videos) must be less than 15MB. Current size: {total_size / (1024 * 1024):.2f}MB', 'danger')
            return render_template('edit_post.html', title='Edit Post', form=form, post=post, 
                                 existing_images_data=existing_images_data, 
                                 existing_videos_data=existing_videos_data)

        post.title = form.title.data
        post.content = form.content.data

        # Handle new image uploads
        if form.images.data:
            image_filenames = []
            for image in form.images.data:
                if image:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_filenames.append(filename)
            post.image_filenames = ','.join(remaining_existing_image_filenames + image_filenames)
        else:
            post.image_filenames = ','.join(remaining_existing_image_filenames)

        # Handle new video uploads
        if form.videos.data:
            video_filenames = []
            for video in form.videos.data:
                if video:
                    filename = secure_filename(video.filename)
                    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    video.save(video_path)
                    video_filenames.append(filename)
            post.video_filenames = ','.join(remaining_existing_video_filenames + video_filenames)
        else:
            post.video_filenames = ','.join(remaining_existing_video_filenames)

        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('edit_post.html', title='Edit Post', form=form, post=post,
                         existing_images_data=existing_images_data,
                         existing_videos_data=existing_videos_data)

@main.route('/remove-image/<int:post_id>/<filename>', methods=['POST'])
@login_required
def remove_image(post_id, filename):
    post = Post.query.get_or_404(post_id)
    
    # Remove image file
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Update post's image_filenames
    if post.image_filenames:
        image_list = post.image_filenames.split(',')
        if filename in image_list:
            image_list.remove(filename)
            post.image_filenames = ','.join(image_list)
            db.session.commit()
    
    return jsonify(success=True) # Return JSON response for AJAX

@main.route('/remove-video/<int:post_id>/<filename>', methods=['POST'])
@login_required
def remove_video(post_id, filename):
    post = Post.query.get_or_404(post_id)
    
    # Remove video file
    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(video_path):
        os.remove(video_path)
    
    # Update post's video_filenames
    if post.video_filenames:
        video_list = post.video_filenames.split(',')
        if filename in video_list:
            video_list.remove(filename)
            post.video_filenames = ','.join(video_list)
            db.session.commit()
    
    return jsonify(success=True) # Return JSON response for AJAX

@main.route('/update-newsletter-title', methods=['POST'])
@login_required
def update_newsletter_title():
    new_title = request.form.get('newsletter_title')
    if new_title:
        current_user.newsletter_title = new_title
        db.session.commit()
        flash('Newsletter title updated successfully.', 'success')
    return redirect(url_for('main.newsletter_preview'))

@main.route('/remove-subscriber/<int:subscriber_id>', methods=['POST'])
@login_required
def remove_subscriber(subscriber_id):
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash('Subscriber has been removed.', 'success')
    return redirect(url_for('main.newsletter_preview'))
