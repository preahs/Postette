# Postette

A self-hostable newsletter service for sending personalized updates to friends and family. Postette provides a simple, elegant interface for managing your newsletter subscriptions and sending beautiful, formatted emails to your loved ones.

> [!WARNING]
This project is currently in active development and should be considered unstable. Features may change, bugs may exist, and the application is not yet stable. Use at your own risk.

## Features

- Beautiful, responsive web interface
- Email subscription management
- Newsletter archive
- User authentication
- Email verification
- Invite system for subscribers

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A mail server or SMTP service (e.g., Gmail, SendGrid, etc.)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/preahs/Postette.git
   cd Postette
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   MAIL_SERVER=your-smtp-server
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email
   MAIL_PASSWORD=your-password
   DATABASE_URL=sqlite:///instance/app.db
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Create an admin user:
   ```bash
   python create_user.py
   ```

7. Run the application:
   ```bash
   flask run
   ```

The application will be available at `http://localhost:5000`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)