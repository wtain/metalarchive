# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements if you have them
COPY requirements.txt .

# Install dependencies (if you have requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY backend.py .
COPY daily_digest.py .
COPY log.ini .

COPY stats_session.session.enc .

COPY csv_saver/ ./csv_saver/
COPY database_saver/ ./database_saver/
COPY storage_client/ ./storage_client/
COPY aitools/ ./aitools/
COPY api/ ./api/
COPY db/ ./db/
COPY metrics/ ./metrics/
COPY environment/ ./environment/
COPY synchronizer/ ./synchronizer/
COPY telegram/ ./telegram/

# Run script once when container starts
# CMD ["python", "channel_stats.py"]
EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "-k", "uvicorn.workers.UvicornWorker", "backend:app", "--log-config", "log.ini"]
