FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Expose port
EXPOSE 8080

# Run the application with gunicorn (single worker to maintain cache consistency)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--log-level", "info", "app:app"]
