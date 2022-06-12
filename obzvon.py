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
    # TODO поменять так, чтобы добавление условного форматирования не зависело от 


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

    #небольшой костыль для определения буквы столбца с датой
    dateLetter = chr(65+columnlist.index('Дата'))

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
        #Условное форматирование для даты
        "addConditionalFormatRule": {
            "rule": {
            "ranges": [
                {
                "sheetId": sheetId,
                "startRowIndex": 1,
                "endRowIndex": maxrowcount,
                "startColumnIndex": 0,
                "endColumnIndex": len(columnlist),
                }
            ],
            "booleanRule": {
                "condition": {
                "type": "CUSTOM_FORMULA",
                "values": [
                    {
                    "userEnteredValue": f'=AND(DATEDIF(${dateLetter}2;TODAY();"D")>2;NOT(ISBLANK(${dateLetter}2)))'
                    }
                ]
                },
                "format": {
                "backgroundColor": {
                    "red": 0.93,
                    "green": 0.73,
                    "blue": 0.71,
                    "alpha": 0.8
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
        logging.info("OBZVON_INIT: format SUCCESS")
    except:
        logging.exception("OBZVON_INIT: format FAIL")
    

def create_obzvon_df(df:pd.DataFrame)-> pd.DataFrame:
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

def transfercomments(dfnew:pd.DataFrame,dfold:pd.DataFrame)->pd.DataFrame:
    """
    Переносит Комментарии соответствующим ID из dfold в dfnew\n
    Возврщает отсортированный по дате датафрейм\n
    Наиболее новые заявления сверху
    """
    for i in dfnew['ID']:
        #если и в старом и в новом есть значения
        if (dfold["ID"].isin([i]).any()):
            comment = dfold.loc[dfold['ID']==i,'Комментарии'].to_string(index=False)
            dfnew.loc[dfnew['ID']==i,'Комментарии'] = comment
    dfnew=dfnew.fillna("")
    dfnew = dfnew.sort_values('Дата')
    return dfnew

	    
# def get_delete_list(df_old,df_new):
#     """
#     Возвращает массив интов Номер строки:ID, записей, которые нужно удалить\n
#     Args: \n
#     old dataframe\n
#     new dataframe\n
#     Returns:\n
#     list of rows to delete\n
#     """
#     dellist = []
#     #Если в новом датафрейме нет значения, то записываем в датафрейм значений, которые нужно удалить.
#     df_old['sheet_row'] = range(1, len(df_old) + 1)
#     df_old.set_index('sheet_row', inplace=True)
#     for x in df_old["ID"]:
#         if ~df_new["ID"].isin([x]).any():
#             dellist.append(df_old[df_old['ID'] == x].index.tolist())
#     dellist = [x for xs in dellist for x in xs]
#     return dellist


# def create_bu_del_body(dellist,sheetId:int):
#     # TODO Добавить проверку на пустоту
#     # ! В скрипте уже учитывается сдвиг на первую строку с названиями
#     request_list = []
#     for i in range(0,len(dellist)):
#         req = {
#                 'deleteDimension':{
#                     'range':{
#                     'sheetId':sheetId,
#                     'dimension': 'ROWS',
#                     'startIndex':f'{dellist[i]-i}',
#                     'endIndex':f'{dellist[i]+1-i}'
#                     }

#                 }
        
#             }
#         request_list.append(req)

#     request_body = {'requests':request_list}
#     return request_body

def obzvon(file_path:str,spreadsheetId:str):
    """
    Выгружает полный csv файл в существующую гугл таблицу\n 
    Args:\n
    file_path (str)-полный путь к файлу с именем файла и расширением\n 
    Пример: /data/file.csv\n
    spreadsheetId (str) - id таблицы\n
    Returns:\n
    int: 0 [success] or -1\n
    """
    #проверим, что файл существует
    try:
        df = pd.read_csv(file_path)
        logging.info(f"OBZVON: successfully opened {file_path}")
    except:
        logging.exception(f"OBZVON: Error occured while opening the file {file_path}")
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
        logging.exception(f'OBZVON: Sheet not found: {sheetname}')
        return -1
    else:
        #! СЧИТЫВАНИЕ И УДАЛЕНИЕ ДОЛЖНЫ БЫТЬ ПОД ОДНИМ TRY 
        #! СЧИТЫВАНИЕ И УДАЛЕНИЕ ДОЛЖНЫ БЫТЬ ПОД ОДНИМ TRY 
        #! СЧИТЫВАНИЕ И УДАЛЕНИЕ ДОЛЖНЫ БЫТЬ ПОД ОДНИМ TRY 
        try:
            #получаем новую табличку из датафрейма
            dfnew = create_obzvon_df(df)

            # TODO оформить в одну функцию
            # TODO логгирование

            #Выбираем все, что после первой строки
            ranges = [f'Обзвон!A2:{chr(64+len(columnlist))}']
            #Запрашиваем данные из таблички
            responseBGet = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId, ranges=ranges).execute()
            #Выбираем кусок с данными, засовываем в датафрейм
            dfold = pd.DataFrame(responseBGet.get('valueRanges')[0].get('values'), columns = columnlist)
            #Преобразовываем нужные нам столбцы
            #Т.К. при вытаскивании из json'a у нас данные превратились в object, нужно их преобразовать.
            dfold['ID']=dfold['ID'].astype('int64')
            dfold['Комментарии']=dfold['Комментарии'].astype('string')
            data = transfercomments(dfnew,dfold)

            data.to_csv(f'{settings.datapath}/base_obzvon{time.strftime("%Y%m%d-%H%M%S")}.csv', sep=',', encoding='utf-8')
            data = data.to_numpy().tolist()

            #запрос для записи новой таблицы
            data_request= {
                            "valueInputOption": "RAW",
                            "data": [
                                {
                                "range": f"{sheetname}!A2",
                                "majorDimension": "ROWS",
                                "values": data
                                },
                            ]
                        }
            
            #запрос на очистку страницы
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

            bu_response_clean = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=clean_request).execute()
            bu_response_write = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = data_request).execute()

        except:
            logging.exception('OBZVON: FAILED')
            print('OBZVON: FAILED')
    logging.info('OBZVON: executed successfully')
    print('OBZVON: executed successfully')
    return 0