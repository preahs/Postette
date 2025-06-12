from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    username = input("Enter username: ")
    password = input("Enter password: ")
    if User.query.filter_by(username=username).first():
        print("User already exists.")
    else:
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created.")
