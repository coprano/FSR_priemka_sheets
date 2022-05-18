#basename - name of the .csv file w database

basename = 'base.csv'

#datapath - path to .csv file folder
#datapath - path to .csv file 
#
#don't forget about slashes in Linux and backslashes in Windows
#don't forget about smartquotes


datapath = "C:\\FSR_data\\"
datafilepath = f'{datapath}\{basename}'

#!!!!
#token from Google account
#you can use your regular account or create a service account
#you need to put token.json in the same folder as all the files
#!!!!

#scopes
#you don't need to change it
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#SHEET_ID
SHEET_ID = ''