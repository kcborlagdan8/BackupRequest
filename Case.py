import lookup
from sftp import SFTP
from DataViewer import DataViewer

class Case():
    def __init__(self, request):
        self.clientID = request['clientID']
        self.client = request['client']
        self.rnt = request['rnt']
        self.product = request['product']
        self.email = request['email']
        self.dlz = request['dlz']
        self.subject = request['subject']
        self.dataconsentdate = request['dataconsentdate']
        self.asc = request['asc']
        self.db = None
        self.dbserver = None
        self.instance = None

    def getDBType(self):
        def dbtypealias(dbtype):
            val = {
                "Preview": "D",
                "Production": "P",
                "Sandbox": "S"
            }
            return val.get(dbtype, "XXXXXX")

        dbtype = self.subject.split("-")
        dbtype = dbtype[1].strip()
        return dbtypealias(dbtype)

    def getDB(self, dbtype):
        self.instance = lookup.getInstanceName(self.dlz)
        if(dbtype == "D"):
            self.dbserver = "USEAPVVT0DB1"
        #get DB Server if NOT PREVIEW
        else: 
            try:     
                fqdn = lookup.dnsresolver(f"{self.instance}.deltekfirst.com") 
            except:
                print(f"FQDN not found for {self.instance}, {self.clientID}. Check if the client has different instance name.", end = "\n")
                fqdn = ""

            if(self.product == "Vision"):
                self.dbserver = lookup.getDBfromCNAMEDFVE(fqdn)
            else:
                self.dbserver = lookup.getVTPod(fqdn)       

                #get database name for VT
        self.db = self.instance #default
        
        if(self.product == "Vantagepoint" or dbtype == "D"):
            self.db = "C00000" \
                + self.clientID \
                + dbtype \
                + "_1_" \
                + ((self.instance.upper() + "00000000000")[:11]) #e.g.C000073333P_1_ontoit00000

        if(dbtype == "S" and self.product == "Vision"):
            self.db += "_Sandbox"


class BackupRequest(Case):
    def __init__(self, request):
        super().__init__(request)
        self.credentials = None
        

    def generateSFTP(self):
        try:
            session = SFTP().sessionGen(self.rnt)
            self.credentials = SFTP().getCred(session)
        except Exception:
            self.credentials = "SFTP already created or the site is inaccessible"

    def ajera(self):
        if("[ajera cloud support] requesting database" in self.subject.lower()):            
            self.clientID = lookup.getAxiumAccountNum(self.subject)
        dv = DataViewer()
        html = dv.sessionGen(self.clientID)
        data = dv.getData(html) 
        dblist = []
        
        for d in data:
            self.clientID = d[0]
            self.dbserver = f"""USEAPD{d[1]}/{d[2]}"""
            dbdesc = d[4]
            self.db = d[3]
            dblist.append([self.dbserver,self.db,self.clientID,f"""{self.client}:{dbdesc}"""])
        return dblist

class DatabaseRefresh(Case):
    def __init__(self, request):
        super().__init__(request)
        self.sourceDB = None
        self.destDB = None
    
    def getDBs(self):
        if(self.subject.find("Sandbox from a Copy of Production") != -1):
            #logging.warning("Sandbox from a Copy of Production")
            super().getDB("P")
            self.sourceDB = self.db
            super().getDB("S")
            self.destDB = self.db
        else:
            #logging.warning("Production from a Copy of Sandbox")
            super().getDB("S")
            self.sourceDB = self.db
            super().getDB("P")
            self.destDB = self.db