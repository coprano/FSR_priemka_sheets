from svodka import *
from obzvon import *
from grant_access import *
import settings

# #на какой лист писать?
listname = "Лист2"
#TODO remove listname from svodka
#svodka(settings.datafilepath,settings.SHEET_ID,listname)
for i in range(0,100):
    obzvon(settings.datafilepath,settings.SHEET_ID)
    obzvon_init(settings.SHEET_ID)
# email = "fsr.bot.priemka@gmail.com"
# grant_access(spreadsheetId,email)