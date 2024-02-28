# Use a Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from the host into the container
COPY . .

# Set up the virtual environment
RUN python3 -m venv venv

# Activate the virtual environment
RUN /bin/bash -c "source venv/bin/activate"

# Expose any necessary ports
# EXPOSE 5000

# Define the command to run your application
CMD [ "python", "yolov5/detect.py" ]
