FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application files
COPY . .

# Set the entry point for the application
CMD ["python", "app.py"]
