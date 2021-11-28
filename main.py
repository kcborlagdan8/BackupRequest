from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import re
from sftp import SFTP
import lookup

wb = load_workbook('.\BackupRequests.xlsx')
ws = wb.active

count = 0#number of tickets

#loop through rows for backup requests
for row in range(1, 300): #row
    for col in range(1, 7): #column
        char = get_column_letter(col)
        val = ws[char + str(row)].value
        if(col == 6 and val != None and "Database Backup Request" in str(val)):
            count += 1
            #get values from excel
            clientID = ws["D" + str(row)].value
            client = ws["E" + str(row)].value
            case = ws["B" + str(row)].value
            product = ws["C" + str(row)].value

            #Generate sftp credentials
            session = SFTP().credGen(case)
            credentials = SFTP().getCred(session)

            #Get instance name 
            domain = ws["G" + str(row)].value #get dlz value
            try:
                instance = re.search('https://(.+?).dlz.deltek.com', domain).group(1).title()
            except AttributeError:
                instance = ""
            #end get instance name

            #get db name - not accurate for VT23


            #Get database type
            subject = ws["F" + str(row)].value #check if preview, sandbox, production
            dbtype = subject.split("-")
            dbtype = dbtype[1].strip()
            def dbtypealias(dbtype):
                switcher = {
                    "Preview": "D",
                    "Production": "P",
                    "Sandbox": "S"
                }
                return switcher.get(dbtype, "XXXXXX")
            #end database type

            dbtype = dbtypealias(dbtype)

            
            #get DB Server if NOT PREVIEW
            if(dbtype != "D"): 
                try:   
                    fqdn = lookup.dnsresolver(instance + ".deltekfirst.com") 
                except:
                    print("\nFQDN not found for " + instance + ", " + clientID + ". Check if the client has different instance name.")
                    fqdn = ""

                if(product == "Vision"):
                    dbserver = lookup.getDBfromCNAME(str(fqdn))
                try:
                    pod = re.search('vt(.+?).deltekfirst.com.', fqdn).group(1)
                    dbserver = "USEAPDVT" + pod +"DB1"
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
            print( dbserver + "," + databaseName + "," + clientID + "," + "N,Y," + "\"" + client + "\"," + case + "," + credentials
            )

            
print("\nNumber of Backup Requests: " + str(count))
