#for csv:
import logging
import time

import pandas as pd

logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')

import httplib2
import numpy
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

#for sheets:
import settings

sheetname = 'Вместо ЕГЭ'

def SprConnect():
    """
    Подключение к аккаунту Google
    """
    # TODO add exception catcher
    # TODO уйти от settings файла?
    credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.token_service, settings.SCOPES)
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http = httpAuth, cache_discovery=False)
    return service

def get_new_men(df:pd.DataFrame)->pd.DataFrame:
    print(df)
    df = df[df['Вместо ЕГЭ'] == True]
    df = df[df['Новое согласие?'] == False]
    df['ФИО'] = df['ФИО']
    df=df['ФИО'].astype('string')
    df=df.fillna("")
    print(df)
    return df


def vmestoege(file_path:str,spreadsheetId:str):
    """
    Дописывает под последнюю строку с данными фамилию человека
    """
    #проверим, что файл существует
    try:
        df = pd.read_csv(file_path)
        logging.info(f"VMESTOEGE: successfully opened {file_path}")
    except:
        logging.exception(f"VMESTOEGE: Error occured while opening the file {file_path}")
        raise SystemExit(-1)
    
    #Подключаемся к таблице
    service = SprConnect()

    #Получаем список листов, все их параметры
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheetId).execute()
    sheetList = spreadsheet.get('sheets')
    
    #SheetId - айди нужного нам листа
    sheetId = -1
    for sheet in sheetList:
        if sheet['properties']['title'] == sheetname:
            sheetId = sheet['properties']['sheetId']
    
    if sheetId == -1:
        logging.exception(f'VMESTOEGE: Sheet not found: {sheetname}')
        return -1
    else:
        df = get_new_men(df)
    df = df.to_numpy().tolist()
    #двумерный массив нужен для гугл таблицы
    df = [[x] for x in df]
    print(df)


    resource = {
    "majorDimension": "ROWS",
    "values": df
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range='A2:Z', valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=resource)
    response = request.execute()

    return 0