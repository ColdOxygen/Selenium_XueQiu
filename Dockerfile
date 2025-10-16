# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    unzip \
    jq \
    --no-install-recommends

# Add Google's official GPG key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg

# Set up the repository for Google Chrome Stable
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome Stable
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

# --- START: IMPROVED CHROMEDRIVER INSTALL ---
# Use the new JSON endpoints from Google to get the latest stable chromedriver
RUN LATEST_STABLE_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url') && \
    wget -O /tmp/chromedriver.zip $LATEST_STABLE_URL && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64
# --- END: IMPROVED CHROMEDRIVER INSTALL ---

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Command to run on container start
CMD ["python", "Xueqiu-user-status.py"]
