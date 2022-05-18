from svodka import *
from grant_access import *
import settings

svodka(settings.datafilepath)
spreadsheetId = "1BqGdb75jl33yFq1E75tnJ36d0IsXhSyMw9ZtcUUixhU"
email = "fsr.bot.priemka@gmail.com"
grant_access(spreadsheetId,email)