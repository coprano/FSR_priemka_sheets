#for csv:
import pandas as pd

import logging
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')


#for sheets:
import settings
import httplib2 
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials	

#auxulary:
import datetime
sheetname = 'Сводка'
maxrowcount = 10000

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

def svodka_data_creator(df:pd.DataFrame):
    """
    Args:\n
    df pandas.DataFrame\n
    В котором есть столбец "Направление" и "Статус согласия" и "Cтатус Согласия"\n 
    Returns:\n
    data (list of lists)\n
    data[0] - блок направление\n
    data[1] - инфа об олимпиадниках\n
    data[2] - инфа о заявлениях
    """
    data = []
    try:
        data_cnt = pd.DataFrame(df["Направление"].value_counts()).fillna("").reset_index().to_numpy().tolist()
        svodka_stripper(data_cnt)
        data.append(data_cnt)
    except:
        data.append([['err',"0"]])
        logging.exception('SVODKA: No column named "Направление" in df.')
        print('SVODKA: No column named "Направление" in df.')

    try:
        data_olymp = pd.DataFrame(df["Олимпиадник?"].value_counts())
        data_olymp = data_olymp.rename(index={'Нет': 'Без олимпиад'})
        
        data_olymp = data_olymp.fillna("").reset_index().to_numpy().tolist()
        data.append(data_olymp)
    except:
        data.append([['err',"0"]])
        logging.exception('SVODKA: No column named "Олимпиадник?" in df.')
        print('SVODKA: No column named "Олимпиадник?" in df.')
    
    try:
        data_sogl = pd.DataFrame(df["Статус согласия"].value_counts())
        data_sogl = data_sogl.rename(index={'Нет': 'Нет согласия или отзыва'})
        data_sogl = data_sogl.append(pd.DataFrame({'Статус согласия': [df.shape[0]]},index = ['Всего заявлений']).astype('int64'))
        data_sogl = data_sogl.reindex(['Всего заявлений', 'Согл. на зач.: Принято АИС', 'Согл. на зач.: Отзыв принят АИС', 'Согл. на зач.: Отзыв загружен'])
        data_sogl = data_sogl.fillna("").reset_index().to_numpy().tolist()
        data.append(data_sogl)
    except:
        data.append([['err',"0"]])
        logging.exception('SVODKA: No column named "Статус согласия" in df.')
        print('SVODKA: No column named "Статус согласия" in df.')

    return(data)



def svodka(file_path,spreadsheetId):
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
        data = svodka_data_creator(df)
        print()
        print(data[2])
        name = "Направление"
        listnapr = df[name].unique()
        bu_val_body = {
                "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {
                    "range": f"{sheetname}!B2",
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": data[0]
                    },
                    {
                    "range": f"{sheetname}!E2",
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": data[1]
                    },
                    {
                    "range": f"{sheetname}!H2",
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": data[2]
                    },
                    {
                    "range": f"{sheetname}!H10",
                    "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
                    "values": [['Обновлено',datetime.datetime.now().strftime('%d.%m.%Y %H:%M') ]]
                    }
                ]
            }
        #запрос на очистку страницы
        #! Т.К. ПИШЕМ НА ВТОРУЮ СТРОКУ, НЕ НУЖНО СТАВИТЬ startIndex МЕНЬШЕ ДВОЙКИ. ИНАЧЕ БУДЕТ ПРОИСХОДИТЬ ОШИБКА
        clean_request = {"requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheetId,
                        "dimension": "ROWS",
                        "startIndex": 2,
                        "endIndex": maxrowcount
                    }
                }
            },
        ]}
        try:
            bu_response_clean = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=clean_request).execute()
        except:
            print()
        try:
            results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = bu_val_body).execute()
        except:
            logging.exception("SVODKA: Error while performing batchUpdate to googlesheets.")
            print("SVODKA: Error while performing batchUpdate to googlesheets.")
            return -1
    logging.info('SVODKA: executed successfully')
    print('SVODKA: executed successfully')
    return 0