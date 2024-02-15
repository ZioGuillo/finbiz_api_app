# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy only the requirements file to the container
COPY ./app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
        && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 5000

# Run the command to start the application
CMD [ "python", "app.py" ]
# CMD gunicorn -w 4 --bind 0.0.0.0:5000 wsgi:app