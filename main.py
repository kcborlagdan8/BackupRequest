from dns.rdatatype import NULL
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import re
from sftp import SFTP
import lookup
import sys

file = sys.argv[1]

search = "database backup request" if "backuprequest" in str(file).lower() else "support server (not support pod)"
wb = load_workbook(file)
ws = wb.active
count = 0 #number of tickets
dbtype = 'P'
dbserver = ''

def dbtypealias(dbtype):
    switcher = {
        "Preview": "D",
        "Production": "P",
        "Sandbox": "S"
    }
    return switcher.get(dbtype, "XXXXXX")

#loop through rows for backup requests
for row in range(1, 300): #row
    for col in range(1, 7): #column
        char = get_column_letter(col)
        val = ws[char + str(row)].value
        if(col == 6 and val is not None and search in str(val).lower()):
            count += 1
            
            #get values from excel
            clientID = ws["D" + str(row)].value
            client = ws["E" + str(row)].value
            case = ws["B" + str(row)].value
            product = ws["C" + str(row)].value

            #Generate sftp credentials
            try:
                session = SFTP().credGen(case)
                credentials = SFTP().getCred(session)
            except Exception:
                credentials = ""

            #Get instance name 
            domain = ws["G" + str(row)].value #get dlz value
            try:
                instance = re.search('(.+?)@(.+?).com', domain).group(2).title()
            except AttributeError:
                instance = ""
            #end get instance name

            #Get database type
            subject = ws["F" + str(row)].value #check if preview, sandbox, production
            if(search == "database backup request"):
                dbtype = subject.split("-")
                dbtype = dbtype[1].strip()
                dbtype = dbtypealias(dbtype)
            #end database type           

            
            #get DB Server if NOT PREVIEW
            if(dbtype != "D"): 
                try:   
                    fqdn = lookup.dnsresolver(f"{instance}.deltekfirst.com") 
                except:
                    print(f"\nFQDN not found for {instance}, {clientID}. Check if the client has different instance name.")
                    fqdn = ""

                if(product == "Vision"):
                    dbserver = lookup.getDBfromCNAME(fqdn)
                else:
                    try:
                        pod = re.search('vt(.+?).deltekfirst.com.', fqdn).group(1)
                        dbserver = f"USEAPDVT{pod}DB1"
                    except AttributeError:
                        pod = ""
            else:
                dbserver = "USEAPVVT0DB1"


            #get database name for VT
            databaseName = instance #default
            
            if(product == "Vantagepoint" or dbtype == "D"):
                databaseName = "C00000" \
                    + clientID \
                    + dbtype \
                    + "_1_" \
                    + ((instance.upper() + "00000000000")[:11]) #e.g.C000073333P_1_ontoit00000

            if(dbtype == "S" and product == "Vision"):
                databaseName += "_Sandbox"
    
            #print(databaseName)
            print(f"{dbserver},{databaseName},{clientID},N,Y,\"{client}\",{case},{credentials}")

            
print(f"\nNumber of Backup Requests: {str(count)}")