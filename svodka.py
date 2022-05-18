#for csv:
import csv
import logging
import os.path
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')

#for sheets:
import settings
import httplib2 
#import apiclient
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials	

def svodka(file_path,spreadsheetId,listname):
    """
    Создает новую гугл таблицу и выгружает в неё файл
    Выгружает полный csv файл в НОВУЮ гугл таблицу
    """
    if(os.path.exists(file_path)):
        CREDENTIALS_FILE = settings.token_service
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
        service = discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    line_count += 1
            logging.info(f'SVODKA: processed {line_count} lines.')
        logging.info(f"SVODKA: finished processing {file_path}")
        # Получаем список листов, их Id и название
        spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheetId).execute()
        sheetList = spreadsheet.get('sheets')
        # for sheet in sheetList:
        #     print(sheet['properties']['sheetId'], sheet['properties']['title'])
        for sheet in sheetList:
           if sheet['properties']['title'] == listname:
               print(sheet['properties']['sheetId'], sheet['properties']['title'])
    else:
        logging.exception(f"SVODKA: couldn't open file:{file_path}")
        return -1