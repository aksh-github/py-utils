# Use an official Python image as a base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install timezone data and set timezone
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Kolkata

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code of your application
COPY src/scheduler-telegram /app/src

# Set the command to run when the container starts
# CMD ["python", "src/send-msg.py"]
CMD ["python", "-u", "src/scheduler.py"]

# Use it like:
# docker build -t py-scheduler .

# stop
# docker stop py-scheduler

# remove
# docker rm py-scheduler

# and then
# docker run -d --name py-scheduler --restart=unless-stopped --env-file .env py-scheduler   # use -d to run in detached mode

# To check logs:
# docker logs -f py-scheduler