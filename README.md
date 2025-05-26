# 3-2-1 Sync

A Python-based backup solution that implements the 3-2-1 backup strategy:
- 3 copies of your data
- 2 local copies on different devices/drives
- 1 offsite copy (using Google Drive)

## Features

- Complete 3-2-1 sync (syncs between offsite, primary, and backup locations)
- Offsite to primary sync only
- Primary to backup sync only (offline mode)
- Automatic file synchronization
- Google Drive integration for offsite storage

## Prerequisites

- Python 3.6 or higher
- Google Cloud Platform account
- Google Drive API enabled
- OAuth 2.0 Client ID

## Setup

1. Clone this repository:
```bash
git clone https://github.com/muhammad-sharique/3-2-1-sync.git
cd 3-2-1-sync
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up Google Drive API:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the client configuration file
   - Rename it to `client_secrets.json` and place it in the project root

4. Configure the application:
   - Copy `client_secrets.json.sample` to `client_secrets.json`
   - Replace the placeholder values with your actual Google API credentials

## Usage

Run the script using:
```bash
python main.py
```

The script will prompt you to:
1. Choose a sync mode:
   - Complete 3-2-1 Sync (recommended)
   - Offsite to Primary Sync
   - Primary to Backup Sync
2. Authenticate with Google Drive (first run only)
3. Enter folder IDs for:
   - Offsite folder (Google Drive folder ID)
   - Primary folder (local path)
   - Backup folder (local path)

### Folder IDs

- **Google Drive Folder ID**: Can be found in the URL when viewing the folder in Google Drive
  Example: `https://drive.google.com/drive/folders/1234567890abcdef` -> ID is `1234567890abcdef`
- **Local folders**: Full path to your backup locations
  Example: `D:\Backup` or `E:\Backup`

## Security

- Never commit your `client_secrets.json` with real credentials to version control
- The app will store OAuth tokens in `credentials.json` locally
- Both files are listed in `.gitignore`
