from svodka import *
from obzvon import *
from grant_access import *
import settings

# #на какой лист писать?
listname = "Лист2"

#svodka(settings.datafilepath,settings.SHEET_ID,listname)
obzvon(settings.datafilepath,settings.SHEET_ID,listname)
# email = "fsr.bot.priemka@gmail.com"
# grant_access(spreadsheetId,email)