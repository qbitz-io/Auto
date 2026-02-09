# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app/backend

# Copy backend code selectively
COPY ./backend/agents ./agents
COPY ./backend/tools ./tools
COPY ./backend/core ./core
COPY ./backend/main.py ./
COPY ./backend/api.py ./
COPY ./requirements.txt ./

# Create memory directory for persistent state
RUN mkdir -p /app/backend/memory

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (default 8080)
EXPOSE 8080

# Set environment variables
ENV API_HOST=0.0.0.0
ENV PORT=8080

# Run the FastAPI server
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8080"]
