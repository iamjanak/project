
# =========================================================
# SwasthaCare HMS - Dockerfile
# =========================================================

# 1. Use Python as the base image
FROM python:3.12-slim

# 2. Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Make Python output appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# 4. Set the working directory inside the container
WORKDIR /app

# 5. Copy dependency file first
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the application source code
COPY . .

# 8. Expose Flask's application port
EXPOSE 5000

# 9. Start the Flask application
CMD ["python", "run.py"]

