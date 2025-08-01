FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for psycopg2 etc.)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy requirements
COPY environment.yml /app/environment.yml

# Install dependencies using pip (simpler than conda inside Docker)
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy psycopg2-binary streamlit requests

# Copy app code
COPY . /app

# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
