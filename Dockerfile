# Base image (updated Debian version)
FROM python:3.10-slim-bullseye

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install git
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy and install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r /requirements.txt

# Copy project files
WORKDIR /VJ-FILTER-BOT
COPY . .

# Run the bot
CMD ["python", "bot.py"]
