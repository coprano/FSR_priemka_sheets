from svodka import svodka
from obzvon import obzvon,obzvon_init
from grant_access import grant_access
from vmestoege import vmestoege
from sheetsdwnld import sheetsdwnld
import settings

#svodka(settings.datafilepath,settings.SHEET_ID)
#obzvon(settings.datafilepath,settings.SHEET_ID)
vmestoege(settings.datafilepath,settings.SHEET_ID)
#obzvon_init(settings.SHEET_ID)
#sheetsdwnld(settings.SHEET_ID)
# email = "fsr.bot.priemka@gmail.com"
# grant_access(spreadsheetId,email)