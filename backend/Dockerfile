FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# The host 0.0.0.0 is important for Docker! It means "listen on all interfaces".