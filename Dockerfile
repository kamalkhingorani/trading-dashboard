# Dockerfile for Kamal's Trading Dashboard on GCP

# Step 1: Use a stable image with build tools
FROM python:3.10

# Step 2: Set working directory
WORKDIR /app

# Step 3: Install system dependencies (essential for many Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy local files
COPY . /app

# Step 5: Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Step 6: Expose Streamlit port
EXPOSE 8501

# Step 7: Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
