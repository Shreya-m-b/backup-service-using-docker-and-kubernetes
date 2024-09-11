# # Use the official Python image as a base image
# FROM python:3.9

# RUN pip install --no-cache-dir google-auth google-auth-oauthlib google-api-python-client

# # Set the working directory in the container
# WORKDIR /app

# # Copy the Python script and credentials file into the container
# COPY backup_script.py .
# COPY credentials.json .
# COPY token.json .

# # Install necessary dependencies
# #RUN pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# # Run the script when the container starts
# CMD ["python", "backup_script.py"]

# Use the official Python image as a base image
FROM python:3.9

RUN pip install --no-cache-dir google-auth google-auth-oauthlib google-api-python-client

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and credentials file into the container
COPY backup_script.py .
COPY credentials.json .
COPY token.json .

# Copy the backupfiles folder into the container
COPY backupfiles /app/backupfiles

# Run the script to perform the backup when the container starts
CMD ["python", "backup_script.py", "/app/backupfiles"]