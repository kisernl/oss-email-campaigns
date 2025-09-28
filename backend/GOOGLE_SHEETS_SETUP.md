# Google Sheets API Setup Guide

This guide will help you set up Google Sheets API access for the Email Campaign App.

## Prerequisites

- Google Cloud Platform account
- Google Sheets with email addresses you want to use for campaigns

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

## Step 2: Enable Google Sheets API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details:
   - Name: `email-campaign-service`
   - Description: `Service account for email campaign app`
4. Click "Create and Continue"
5. Skip optional steps and click "Done"

## Step 4: Generate Service Account Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Choose "JSON" format
6. Download the key file

## Step 5: Set Up Credentials

1. Rename the downloaded file to `credentials.json`
2. Place it in the `backend/` directory
3. **IMPORTANT**: Never commit this file to git (it's already in .gitignore)

Alternatively, you can set the credentials as an environment variable:
```bash
export GOOGLE_CREDENTIALS_JSON='{"type": "service_account", ...}'
```

## Step 6: Prepare Your Google Sheet

1. Create or open your Google Sheet with email addresses
2. Make sure it has clear headers like:
   - `Email` or `Email Address` - for email addresses
   - `Name` or `Full Name` - for recipient names (optional)
3. Share the sheet with your service account email:
   - Click "Share" button in Google Sheets
   - Add the service account email (found in credentials.json as `client_email`)
   - Give "Editor" permission (needed to mark emails as sent)

## Expected Sheet Format

Your Google Sheet should look like this:

| Name | Email Address | Company | Phone |
|------|---------------|---------|-------|
| John Doe | john@example.com | Acme Corp | 123-456-7890 |
| Jane Smith | jane@example.com | Tech Inc | 098-765-4321 |

## Testing the Setup

You can test your setup by running:

```bash
cd backend
source venv/bin/activate
python -c "
from app.services.google_sheets import GoogleSheetsService
service = GoogleSheetsService()
# Replace with your actual sheet ID
sheet_id = 'your_google_sheet_id_here'
print('Testing access:', service.test_sheet_access(sheet_id))
"
```

## Getting Your Sheet ID

Your Google Sheet ID is in the URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit#gid=0
                                      ↑
                                 This is your Sheet ID
```

## Troubleshooting

### Permission Denied (403)
- Make sure you shared the sheet with the service account email
- Check that the service account has "Editor" permissions

### Sheet Not Found (404)
- Verify the sheet ID is correct
- Make sure the sheet exists and is accessible

### Authentication Errors
- Check that `credentials.json` is in the correct location
- Verify the JSON format is valid
- Make sure the Google Sheets API is enabled in your project

### Invalid Email Addresses
- Check your sheet has a column with header containing "email"
- Verify email addresses are in valid format
- Remove any empty rows or invalid data

## Security Notes

- Keep your `credentials.json` file secure and never share it
- The service account email should only have access to sheets you need
- Consider using environment variables for production deployment
- Regularly rotate your service account keys