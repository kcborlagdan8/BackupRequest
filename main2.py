from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import re
from Case import *
from sftp import SFTP
import lookup
import sys


#Input main.py Cases.xlsx 1
file = sys.argv[1] #Cases.xlsx
type = sys.argv[2] #1

######################
#   Types of Cases   #
# 1 - Backup Request #
# 2 - Data Consent   #
# 3 - Support Pod
# 4 - Database Refresh (Preview NOT included)
# 9 - All SRs        #
# 0 - All Incidents  #
######################

#Types of Case
dbr = "database backup request"
def caseType(x):
    cType = {
        "1": ["database backup request"],
        "2": ["support server (not support pod)", "local restore"],
        "3": ["support pod"],
        "4": ["database refresh"]
    }
    #All SRs "9"
    cType["9"] = [cType["1"][0], cType["4"][0]]

    #All incidents "0"
    cType["0"] = [cType["2"][0], cType["2"][1], cType["3"][0]]

    return cType.get(x, "XXXXXX")
 
search = caseType(type) if type in ["1", "2", "3", "4", "9", "0"] else exit("Choose from 0-9 only.")

wb = load_workbook(file)
ws = wb.active
count = 0 #number of tickets with case type
brcount = 0
dbrcount = 0
#dccount = 0
spcount = 0

brline = ""
dbrline = ""
#dcline = ""
spline = ""

s = ", ".join(search).capitalize()
print(f"Search for: {s}")

#LOOP THROUGH EXCEL FILE
#print(type, search)
for row in range(1, 300): #row
    for col in range(1, 7): #column
        char = get_column_letter(col)
        val = ws[char + str(row)].value
        if(col == 6 and val != None):
            if(col == 6 and val is not None and "Refresh Preview" not in val and any(y in str(val).lower() for y in search)):
                count += 1
                #create dict from excel
                request = {
                    "clientID": ws["D" + str(row)].value,
                    "client": ws["E" + str(row)].value,
                    "rnt": ws["B" + str(row)].value,
                    "email": ws["G" + str(row)].value,
                    "dlz": ws["H" + str(row)].value,
                    "product": ws["C" + str(row)].value,
                    "subject": ws["F" + str(row)].value
                }
                if(type in ["1", "2", "9"]# and val.lower().find(search[0]) != -1
                ): #Backup Request
                    
                    br = BackupRequest(request)

                    if(val.lower().find(search[0]) != -1 and type == "1"):
                        dbtype = br.getDBType()
                        br.getDB(dbtype)
                    
                    else: #data consent
                        br.getDB("P")
                    br.generateSFTP()
                    cred = ",".join(br.credentials)
                    brline +=f"""{br.dbserver},{br.db},{br.clientID},N,Y,\"{br.client}\",{br.rnt},{cred}
"""
                    brcount += 1
                
                if(type == "4" or type == "9" and val.lower().find(search[1]) != -1): #DB Refresh
                    dbr = DatabaseRefresh(request)
                    dbr.getDBs()
                    
                    if(dbr.dbserver == "XXXXXX"): #if fqdn was not found
                        dbr.sourceDB = dbr.dbserver 
                        dbr.destDB = dbr.dbserver 

                    dbrline +=f"""{dbr.dbserver},{dbr.clientID},{dbr.instance},{dbr.sourceDB},{dbr.destDB},{dbr.rnt}
"""
                    dbrcount += 1
               # if(cType == "9"):
               #     line = """
               #     """
print(f"\nBackup and Data Consent: {brcount}")               
print(brline)
print(f"Database Refresh: {dbrcount}")               
print(dbrline)
#print("Data Consent:")               
#print(dcline)
print("Support Pod:")               
print(spline)

print(f"\nNumber of cases to be processed: {str(count)}")