SECRET_KEY = 'yoursecretkey'
SQLALCHEMY_DATABASE_URI = 'sqlite:///newsletter.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'  # Use environment variables or `.env`
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 16MB
