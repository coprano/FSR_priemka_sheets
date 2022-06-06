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

def create_full_csv(df):
    df_new = df[['ID','ФИО','Номер телефона','Зона','Статус ошибок']] 
    df_new = df_new.reindex(columns= ['ID','ФИО','Зона','Номер телефона','Комментарии','Статус ошибок'])
    #df_new.index = df.index.set_names('foo', level=1)
    df_new.reindex(df_new['ID'])
    #df_new.drop('Indexes')
    return df_new 

def filter_finished(df):
    df = df.drop(df[df['Статус ошибок'] == "Загружено в АИС / Проверки пройдены"].index)
    df.reset_index().reindex(df['ID'])
    return df

def df_to_list(df):
    return df.to_numpy().tolist()

def obzvon(file_path,spreadsheetId,sheetname):
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
        logging.info(f"OBZVON: successfully opened {file_path}")
        print(f"OBZVON: successfully opened {file_path}")
    except:
        logging.exception(f"OBZVON: Error occured while opening the file {file_path}")
        print(f"OBZVON: Error occured while opening the file {file_path}")
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
            print('OBZVON:', sheet['properties']['sheetId'], sheet['properties']['title'])
            sheetId = sheet['properties']['sheetId']
    print(sheetId)
    
    if sheetId == -1:
        logging.exception(f'OBZVON: Sheet not found: {sheetname}')
        print(f'OBZVON: Sheet not found: {sheetname}')
        return -1
    else:
        data = filter_finished(create_full_csv(df))
        data = data.fillna("")
        data.to_csv('C:/FSR_data/base_obzvon.csv', sep=',', encoding='utf-8')
        data = df_to_list(data)
        print(data) 



        
        try:
            # Очищаем лист
            rangeAll = '{0}!A1:Z'.format( sheetname )
            body = {}
            resultClear = service.spreadsheets( ).values( ).clear( spreadsheetId=spreadsheetId, range=rangeAll,
                                                                body=body ).execute( )
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
            logging.exception("OBZVON: Error while performing batchUpdate to googlesheets.")
            print("OBZVON: Error while performing batchUpdate to googlesheets.")
            return -1
    logging.info('OBZVON: executed successfully')
    print('OBZVON: executed successfully')
    return 0