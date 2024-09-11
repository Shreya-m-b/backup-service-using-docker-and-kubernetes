import os
import subprocess
import time
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

import os

def list_files_in_folder(service, folder_id):
    """List all files in the specified folder."""
    response = service.files().list(
        q=f"'{folder_id}' in parents",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = response.get('files', [])
    return {file['name']: file['id'] for file in files}

def upload_to_google_drive(file_path, service, folder_id, existing_files):
    """Upload or update file in Google Drive."""
    file_name = os.path.basename(file_path)
    if file_name.startswith('.goutputstream'):
        #print(f"Skipping file: {file_name}")
        return  # Skip uploading this file
    try:
        # Check if the file already exists in Google Drive
        file_id = existing_files.get(file_name)
        media = MediaFileUpload(file_path)
        if file_id:  # File already exists, update it
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            print(f"Updated file: {file_name}")
        else:  # File doesn't exist, create it
            file_metadata = {
                "name": file_name,
                "parents": [folder_id]
            }
            upload_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            print(f"Uploaded file: {file_name}")
    except HttpError as e:
        print("Error: " + str(e))

def main():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    response = service.files().list(
        q="name='BackupFolder10' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()
    if not response['files']:
        file_metadata = {
            "name": "BackupFolder10",
            "mimeType": "application/vnd.google-apps.folder"
        }    
        file = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = file.get('id')
    else:
        folder_id = response['files'][0]['id']

    # List all existing files in the Google Drive folder
    existing_files = list_files_in_folder(service, folder_id)

    # Backup initial contents of the folder
    for root, dirs, files in os.walk('backupfiles'):
        for file in files:
            upload_to_google_drive(os.path.join(root, file), service, folder_id, existing_files)

 

if __name__ == "__main__":
    main()