# Dockerfile
# Use a slim Python base image for smaller size
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't store cache files to reduce image size
# -r: Install from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your FastAPI app will listen on (default for Uvicorn)
EXPOSE 8000

# Command to run your FastAPI application using Uvicorn
# main:app refers to the 'app' object in 'main.py'
# --host 0.0.0.0: Makes the app accessible from outside the container
# --port $PORT: Railway injects the port your app should listen on as an env var
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]