# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app .

# Install any needed packages specified in requirements.txt
# RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
        && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt --src /usr/local/src
# RUN pip install gunicorn

# Expose the port that the application will run on
EXPOSE 5000

# Run the command to start the application
# CMD [ "python", "app.py" ]
CMD gunicorn -w 4 --bind 0.0.0.0:5000 wsgi:app

# docker run -d -p 80:5000 hello_app_prod 
