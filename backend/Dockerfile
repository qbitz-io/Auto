# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ ./backend/

# Copy requirements file
COPY backend/requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (default 8080)
EXPOSE 8080

# Set environment variables
ENV API_HOST=0.0.0.0
ENV PORT=8080

# Run the FastAPI server
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8080"]
