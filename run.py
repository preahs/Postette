from dotenv import load_dotenv
import os

load_dotenv()

from app import create_app
from app.extensions import db

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized.")

if __name__ == '__main__':
    app.run(debug=True)
