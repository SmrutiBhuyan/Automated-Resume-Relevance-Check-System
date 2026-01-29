# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create upload directories
RUN mkdir -p uploads/resumes uploads/job_descriptions uploads/temp

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 5000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
redis-server --daemonize yes\n\
celery -A tasks worker --loglevel=info --detach\n\
python app.py &\n\
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0\n\
' > start.sh && chmod +x start.sh

# Default command
CMD ["./start.sh"]
