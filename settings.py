#basename - name of the .csv file w database

basename = "base.csv"

#datapath - path to .csv file folder
#datapath - path to .csv file 
#
#don't forget about smartquotes]
#you better check if the file is accessible


datapath = "C:/FSR_data/"
datafilepath = f'{datapath}{basename}'

#!!!!
#token from Google account
#you can use your regular account or create a service account
#you need to put token.json in the same folder as all the files
#see firststart.py and README for more info
#!!!!
token = "token.json"
#token_service - token for service mail
token_service = "fsr-bot-priemka-sheets-d2f9c8b4a169.json"

#scopes
#you don't need to change it
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

#SHEET_ID
SHEET_ID = "1BqGdb75jl33yFq1E75tnJ36d0IsXhSyMw9ZtcUUixhU"