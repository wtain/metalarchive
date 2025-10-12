# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements if you have them
COPY requirements.txt .

# Install dependencies (if you have requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY channel_stats.py .
# Not really secure... - should be encrypted
COPY stats_session.session.enc .
COPY csv_saver/ ./csv_saver/
COPY database_saver/ ./database_saver/
COPY storage_client/ ./storage_client/

# Run script once when container starts
CMD ["python", "channel_stats.py"]
