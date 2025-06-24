import os
import re
from flask import Flask, request, redirect, url_for
from jinja2 import pass_eval_context
from markupsafe import Markup, escape
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from .models import User
from .extensions import db, mail, migrate, login_manager
from .utils import format_datetime

# Load environment variables from .env
load_dotenv()

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load config from environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # fallback to 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'timeout': 30}  # Increase timeout for SQLite
    }
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    # Mail settings
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    app.login_manager = login_manager

    # Token serializer for invite-only links
    app.token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    # Register blueprints
    from .routes import main
    from .auth import auth as auth_blueprint
    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)

    # Add format_datetime to template context
    @app.context_processor
    def utility_processor():
        return dict(format_datetime=format_datetime)

    # Custom template filter
    @app.template_filter()
    @pass_eval_context
    def nl2br(eval_ctx, value):
        if value is None:
            return ''
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
        if eval_ctx.autoescape:
            result = Markup(result)
        return result
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Global login requirement
    @app.before_request
    def redirect_to_setup():
        from .models import User
        # Allow static files and auth.setup when no user exists
        allowed_no_user_routes = ['auth.setup', 'static']
        if not User.query.first() and request.endpoint not in allowed_no_user_routes:
            return redirect(url_for('auth.setup'))
    def require_login():
        from flask_login import current_user
        # List of allowed endpoints that do NOT require login
        allowed_routes = ['auth.login', 'auth.setup', 'static', 'main.subscribe_with_token']
        if (
            not current_user.is_authenticated and 
            request.endpoint not in allowed_routes
        ):
            return redirect(url_for('auth.login'))

    return app
