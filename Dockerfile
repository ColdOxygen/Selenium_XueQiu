# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including gnupg (which provides gpg), curl, and tools for Chrome
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    unzip \
    --no-install-recommends

# Add Google's official GPG key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg

# Set up the repository
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update apt and install Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

# Install Chromedriver
# Find the latest stable version
RUN CHROME_VERSION=$(google-chrome --version | cut -f 3 -d ' ' | cut -d '.' -f 1-3) && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | jq -r ".versions[] | select(.version == \"$CHROME_VERSION\") | .downloads.chromedriver[0].url") && \
    wget -O /tmp/chromedriver.zip $CHROMEDRIVER_VERSION && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Command to run on container start
CMD ["python", "Xueqiu-user-status.py"]
