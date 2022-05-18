from svodka import *
from grant_access import *
import settings

#на какой лист писать?
listname = "Лист1"

svodka(settings.datafilepath,settings.SHEET_ID,listname)

# email = "fsr.bot.priemka@gmail.com"
# grant_access(spreadsheetId,email)