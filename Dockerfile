# Use an official Python image as a base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install timezone data and set timezone
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Kolkata

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code of your application
COPY src/telegram /app/src

# Set the command to run when the container starts
# CMD ["python", "src/send-msg.py"]
CMD ["python", "src/scheduler.py"]

# Use it like:
# docker build -t stock-report .
# and then
# docker run --env-file .env stock-report   # use -d to run in detached mode