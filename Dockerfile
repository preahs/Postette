# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Create folders for persistent data (if not exist)
RUN mkdir -p /app/instance /app/app/static/uploads

# Set environment variables for Flask
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Start with Gunicorn using the Flask app factory
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "'app:create_app()'"] 