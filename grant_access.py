import settings
import httplib2 
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials	

import logging
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')

def grant_access(spreadsheetID,email):
    """
    Выдает доступ на запись к указанной spreadsheetID таблице для имейла email
    """
    try:
        CREDENTIALS_FILE = settings.token_service
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе

        driveService = discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
        access = driveService.permissions().create(
            fileId = spreadsheetID,
            body = {'type': 'user', 'role': 'writer', 'emailAddress': email},  # Открываем доступ на редактирование
            fields = 'id'
        ).execute()
        logging.info(f"successfully granted access to {email}")
        return 0
    except:
        logging.exception(f"access_grant failed: {email}")
        return -1