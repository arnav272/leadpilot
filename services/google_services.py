import os
import json
from datetime import datetime
from pathlib import Path


def _get_credentials():
    from google.oauth2 import service_account
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_path = Path('credentials.json')
    if not creds_path.exists():
        raise FileNotFoundError('credentials.json not found')
    return service_account.Credentials.from_service_account_file(
        str(creds_path), scopes=SCOPES
    )


async def log_to_sheets(lead, status: str = 'Success'):
    try:
        from googleapiclient.discovery import build
        creds = _get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        if not sheet_id:
            print('SHEETS: No GOOGLE_SHEET_ID in .env — skipping')
            return

        # Ensure header row exists
        existing = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range='Sheet1!A1:G1'
        ).execute()

        if not existing.get('values'):
            headers = [['Timestamp', 'Name', 'Email', 'Company', 'Website', 'Industry', 'Report Status']]
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Sheet1!A1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()

        # Append lead row
        row = [[
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            lead.name,
            lead.email,
            lead.company,
            lead.website,
            lead.industry,
            status
        ]]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='Sheet1!A:G',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': row}
        ).execute()
        print(f'SHEETS: Logged {lead.company} — {status}')

    except Exception as e:
        print(f'SHEETS ERROR (non-critical): {e}')


async def archive_to_drive(pdf_path: Path):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        creds = _get_credentials()
        service = build('drive', 'v3', credentials=creds)
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not folder_id:
            print('DRIVE: No GOOGLE_DRIVE_FOLDER_ID in .env — skipping')
            return

        file_metadata = {
            'name': pdf_path.name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(str(pdf_path), mimetype='application/pdf')
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        print(f"DRIVE: Archived {uploaded.get('name')} (id: {uploaded.get('id')})")

    except Exception as e:
        print(f'DRIVE ERROR (non-critical): {e}')