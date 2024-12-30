# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Set the entrypoint to run the Flask app using Gunicorn (for production use)
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# If you want to run with Flask's built-in server (for development), use this instead:
# ENTRYPOINT ["python", "app.py"]
