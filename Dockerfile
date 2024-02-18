# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy only the requirements file, to cache the pip install step
COPY ./app/requirements.txt .

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt --src /usr/local/src

# Install Gunicorn
RUN pip install gunicorn

# Copy the rest of the application's code
COPY ./app .

# Expose the port Gunicorn will listen on
EXPOSE 5000

# Now specify the command to run Gunicorn
# Note: Adjust the number of workers (-w) based on your environment
# Also, replace `app:app` with `your_flask_file_name:flask_app_variable_name` if different
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "app:app"]
