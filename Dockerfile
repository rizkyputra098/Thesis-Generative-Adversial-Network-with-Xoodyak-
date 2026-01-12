# Gunakan Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy semua kode
COPY . /app

# Install system deps untuk Pillow/opencv
RUN apt-get update && \
    apt-get install -y build-essential libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Install pip dependencies
RUN pip install --upgrade pip
RUN pip install torch==2.1.0 streamlit numpy pillow opencv-python-headless

# Expose port Streamlit
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
