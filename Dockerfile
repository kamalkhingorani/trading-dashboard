# Dockerfile for Kamal's Trading Dashboard on GCP

# Step 1: Base image
FROM python:3.10-slim

# Step 2: Working directory
WORKDIR /app

# Step 3: Copy local files to container
COPY . /app

# Step 4: Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Step 5: Expose port
EXPOSE 8501

# Step 6: Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
