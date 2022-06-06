#for csv:
import pandas as pd
import os.path

import logging
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')


#for sheets:
import settings
import httplib2 
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials	

def svodka_stripper(arr):
    """
    Вход:\n
    Двумерный массив. В 1 столбце строка\n 
    Выход:\n
    Тот же массив, в 1 столбце будут удалены все знаки ' [ ]\n
    """
    for i in range(0,len(arr)):
        arr[i][0] = arr[i][0].replace("'","")
        arr[i][0] = arr[i][0].replace("]","")
        arr[i][0] = arr[i][0].replace("[","")
    return arr

def svodka_creator(df):
    """
    Вход:\n
    pandas dataframe\n
    В КОТОРОМ ЕСТЬ СТОЛБЕЦ НАПРАВЛЕНИЕ
    Выход:\n
    Массив формата направление:колво человек\n
    """
    try:
        df = pd.DataFrame(df.Направление.value_counts()).reset_index().to_numpy().tolist()
        svodka_stripper(df)
    except AttributeError:
        logging.exception('SVODKA: No column named "napravlenie" in df.')
        print('SVODKA: No column named "napravlenie" in df.')
        return
    return df



def svodka(file_path,spreadsheetId,sheetname):
    """
    Вход:\n
    -полный путь к файлу с именем файла и расширением (абсолютный или относительный)\n 
    Пример: /data/file.csv\n
    -id таблицы\n
    -имя листа\n
    =====\n
    Выход:\n
    Выгружает полный csv файл в существующую гугл таблицу\n 
    """
    #проверим, что файл существует
    try:
        df = pd.read_csv(file_path)
        logging.info(f"SVODKA: successfully opened {file_path}")
        print(f"SVODKA: successfully opened {file_path}")
    except:
        logging.exception(f"SVODKA: Error occured while opening the file {file_path}")
        print(f"SVODKA: Error occured while opening the file {file_path}")
        raise SystemExit(-1)
    

    #Подключаемся к таблице
    credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.token_service, settings.SCOPES)
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

    #Получаем список листов, все их параметры
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheetId).execute()
    sheetList = spreadsheet.get('sheets')     
    
    #Пока это по сути проверка на то, что лист существует
    #
    #SheetId - айди нужного нам листа
    sheetId = -1
    for sheet in sheetList:
        if sheet['properties']['title'] == sheetname:
            print('SVODKA:', sheet['properties']['sheetId'], sheet['properties']['title'])
            sheetId = sheet['properties']['sheetId']

    
    if sheetId == -1:
        logging.exception(f'SVODKA: Sheet not found: {sheetname}')
        print(f'SVODKA: Sheet not found: {sheetname}')
        return -1
    else:
        data = svodka_creator(df)
        # name = "Направление"
        # listnapr = df[name].unique()
        # for i in range(1,len(listnapr)):
        #     print(listnapr)
        try:
            results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = {
                "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {
                    "range": f"{sheetname}!B2",
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": data
                    }
                ]
            }).execute()
        except:
            logging.exception("SVODKA: Error while performing batchUpdate to googlesheets.")
            print("SVODKA: Error while performing batchUpdate to googlesheets.")
            return -1
    logging.info('SVODKA: executed successfully')
    print('SVODKA: executed successfully')
    return 0