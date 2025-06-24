# Postette

A self-hostable newsletter service for sending personalized updates to friends and family. Postette provides a simple, accessible interface for managing your newsletter subscriptions and sending emails to anyone.

> [!WARNING]
This project is currently in active development and should be considered unstable. Features may change and bugs may exist. Use at your own risk.

## Features

- Beautiful, responsive web interface
- Email subscription management
- Newsletter archive
- User authentication and email verification
- Invite system for subscribers
- Media attachments (images and videos) in posts
- Admin setup and management
- Secure password reset and email verification flows

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A mail server or SMTP service (e.g., Gmail, SendGrid, etc.)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/preahs/Postette.git
   cd Postette
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
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
   SQLALCHEMY_DATABASE_URI=sqlite:///instance/newsletter.db
   ```

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

6. **Run the application:**
   ```bash
   flask run
   ```
   The application will be available at [http://localhost:5000](http://localhost:5000).

---

## Usage

- On first launch, you will be prompted to create an admin user.
- After setup, log in to access the dashboard, create posts, manage subscribers, and send newsletters.
- Subscribers can sign up via invite links and must verify their email before receiving newsletters.
- Posts can include images and videos (with size limits enforced).
- Sent and archived posts can be managed and deleted from the dashboard.

---

## Configuration

All configuration is handled via environment variables or the `instance/config.py` file.  
Key variables include:

- `SECRET_KEY`: Flask secret key for sessions and security.
- `SQLALCHEMY_DATABASE_URI`: Database connection string.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`: Email settings for sending newsletters and verification emails.
- `UPLOAD_FOLDER`: Path for storing uploaded media.

---

## Project Structure

```
Postette/
  app/
    __init__.py
    auth.py
    email_utils.py
    extensions.py
    forms.py
    models.py
    routes.py
    scheduler.py
    static/
      favicon.png
      js/
      styles.css
      uploads/
    templates/
      *.html
  create_user.py
  instance/
    config.py
    newsletter.db
  migrations/
  requirements.txt
  run.py
  README.md
```

---

## Development

- To reset the database, use the CLI command:
  ```bash
  flask init-db
  ```
- To create a user from the command line, run:
  ```bash
  python create_user.py
  ```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, open an issue first to discuss what you would like to change.

---

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/preahs/Postette).

---