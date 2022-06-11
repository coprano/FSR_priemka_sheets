#for csv:
import logging
import os.path

import pandas as pd

logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(message)s')

import httplib2
import numpy
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

#for sheets:
import settings

#названия столбцов
columnlist = ['ID','ФИО','Зона','Номер телефона','Комментарии','Статус ошибок','Дата']
sheetname = 'Обзвон'
maxrowcount = 10000
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

def obzvon_init(spreadsheetId:str) -> None:
    """
    Инициализирует первичные настройки для листа обзвона.\n
    1. Фиксирует 1 строку, записывает названия столбцов.\n
    \n
    Args:\n
        spreadsheetId(str) - id гугл таблицы\n
    """
    # TODO return 0 ?
    # TODO add exception catcher
    # TODO условное форматирование по строкам, а не только по ячейкам


    service = SprConnect()

    #Получение списка листов
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheetId).execute()
    sheetList = spreadsheet.get('sheets') 

    #поиск id листа с нужным названием
    for sheet in sheetList:
        if sheet['properties']['title'] == sheetname:
            sheetId = sheet['properties']['sheetId']

    #данные
    init_data_request_body= {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                    "range": f"{sheetname}!A1",
                    "majorDimension": "ROWS",
                    "values": [columnlist]
                    },
                ]
            }
    try:
        bu_columlistfix_response = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = init_data_request_body).execute()
        logging.info("OBZVON_INIT: init data SUCCESS")
    except:
        logging.exception("OBZVON_INIT: init data FAIL")

    #форматирование
    init_request_body = {
        "requests": [
            #Фиксируем первую строку
            {
            "updateSheetProperties": 
                {
                    
                    "properties": {
                        "sheetId": sheetId,
                        "gridProperties": {"frozenRowCount" : 1}
                    },
                    "fields" : "gridProperties.frozenRowCount"
                },
        },
        #Скрываем первый столбец
        {
            'updateDimensionProperties': {
                    "range": {
                    "sheetId": sheetId,
                    "dimension": 'COLUMNS',
                    "startIndex": 0,
                    "endIndex": 1,
                    },
                    "properties": {
                    "hiddenByUser": True,
                    },
                    "fields": 'hiddenByUser',
                }
        },
        {
        "addNamedRange": {
            #Именованный диапазон для даты
            "namedRange": {
            "name": "Дата",
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 1,
                "endRowIndex": maxrowcount,
                "startColumnIndex": columnlist.index("Дата"),
                "endColumnIndex": columnlist.index("Дата")+1,
            },
            }
        }
        },
        {
        #Условное форматирование для даты
        "addConditionalFormatRule": {
            "rule": {
            "ranges": [
                {
                "sheetId": sheetId,
                "startRowIndex": 1,
                "endRowIndex": maxrowcount,
                "startColumnIndex": len(columnlist),
                "endColumnIndex": len(columnlist),
                }
            ],
            "booleanRule": {
                "condition": {
                "type": "DATE_BEFORE",
                "values": [
                    {
                    "relativeDate": "YESTERDAY"
                    }
                ]
                },
                "format": {
                "backgroundColor": {
                    "green": 0.2,
                    "red": 0.8,
                }
                }
            }
            },
            "index": 1
      }
    }
        ]
    }
    
    try:
        init_request_result = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheetId, body = init_request_body).execute()
        print("success")
        logging.info("OBZVON_INIT: format SUCCESS")
    except:
        logging.exception("OBZVON_INIT: format FAIL")
        print("fail")
    

def formatting(spreadsheetId):
    """
    Инициализирует первичные настройки для листа обзвона.\n
    1. Фиксирует 1 строку, записывает названия столбцов.\n
    \n
    Args:\n
        spreadsheetId(str) - id гугл таблицы\n
    """
    # TODO return 0 ?
    # TODO add exception catcher
    # TODO Сокрытие 1 столбца

    service = SprConnect()

    #Получение списка листов
    spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheetId).execute()
    sheetList = spreadsheet.get('sheets') 

    #поиск id листа с нужным названием
    for sheet in sheetList:
        if sheet['properties']['title'] == sheetname:
            sheetId = sheet['properties']['sheetId']

    #форматирование
    init_request_body = {
  "requests": [
    {
      "addConditionalFormatRule": {
        "rule": {
          "ranges": [
            {
              "sheetId": sheetId,
              "startRowIndex": 1,
              "endRowIndex": maxrowcount,
              "startColumnIndex": len(columnlist)-1,
              "endColumnIndex": len(columnlist),
            }
          ],
          "booleanRule": {
            "condition": {
              "type": "DATE_BEFORE",
              "values": [
                {
                  "relativeDate": "YESTERDAY"
                }
              ]
            },
            "format": {
              "backgroundColor": {
                "green": 0.2,
                "red": 0.8,
              }
            }
          }
        },
        "index": 1
      }
    }
  ]
}
    
    try:
        init_request_result = service.spreadsheets().batchUpdate(spreadsheetId = spreadsheetId, body = init_request_body).execute()
        print("success")
        logging.info("formatting: format SUCCESS")
    except:
        logging.exception("formatting: format FAIL")
        print("fail")    

def create_full_csv(df:pd.DataFrame)-> pd.DataFrame:
    """
    Создаем датафрейм для листа обзвона
    """

    #Выбираем в список столбцов все элементы кроме поля Комментарии
    dfnames = []
    for i in range(0, len(columnlist)):
        if columnlist[i] != "Комментарии":
             dfnames.append(columnlist[i])

    df_new = df[dfnames] 
    df_new = df_new.reindex(columns=columnlist)
    df_new = df_new.drop(df_new[df_new["Статус ошибок"] == "Загружено в АИС / Проверки пройдены"].index).fillna("")
    return df_new 

def obzvon(file_path:str,spreadsheetId:str):
    """
    Выгружает полный csv файл в существующую гугл таблицу\n 
    Args:\n
    file_path (str)-полный путь к файлу с именем файла и расширением\n 
    Пример: /data/file.csv\n
    spreadsheetId (str) - id таблицы\n
    sheetname (str) - название листа, на который писать\n
    Returns:\n
    int: 0 [success] or -1\n
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
    service = SprConnect()

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
        data = create_full_csv(df)
        #Сохраняем в csv последнее записанное состояние для листа обзвона
        data.to_csv(f'{settings.datapath}/base_obzvon.csv', sep=',', encoding='utf-8')

        #преобразовываем в list для передачи в табличку
        data = data.to_numpy().tolist()
        
        try:
            data_request= {
                        "valueInputOption": "USER_ENTERED",
                        "data": [
                            {
                            "range": f"{sheetname}!A2",
                            "majorDimension": "ROWS",
                            "values": data
                            },
                        ]
                    }

            bu_columlistfix_response = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = data_request).execute()
        except:
            logging.exception("OBZVON: Error while performing batchUpdate to googlesheets.")
            print("OBZVON: Error while performing batchUpdate to googlesheets.")
            return -1
    logging.info('OBZVON: executed successfully')
    print('OBZVON: executed successfully')
    return 0
