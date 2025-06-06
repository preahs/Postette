from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from jinja2 import pass_eval_context
from markupsafe import Markup, escape
import re

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    app.register_blueprint(main)

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

    return app
