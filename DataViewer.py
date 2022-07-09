from requests_ntlm import HttpNtlmAuth
from requests_html import HTMLSession
import urllib.parse
import json
import os
from lxml import etree

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path, 'r') as config_file:
    config = json.loads(config_file.read())    
    deltekconfig = config['deltekpages']
    dataviewerconfig = config['dataViewer']

USERNAME = deltekconfig['username']
PASSWORD = deltekconfig['password']
URL = dataviewerconfig['url']
CONTENTTYPE = deltekconfig['content-type']
USERAGENT = deltekconfig['user-agent']


class DataViewer:
    def __init__(self):
        pass

    def auth(self):
        self.authcookie = HttpNtlmAuth(
            USERNAME,
            PASSWORD
        )        
        headers = {'Accept-Encoding': 'identity'}
        self.session = HTMLSession()

        response = self.session.get(
                            URL,
                            auth=self.authcookie,
                            headers=headers)                            
        response.html.render(sleep=5, timeout=20)
        #print(response)
        return response

    def parse(self, response):
        #response.html.xpath('//form//input[@id="ctl00_RadScriptManager1_TSM"]/@value')

        r = response.html.find('form', first=True)
        telrk = r.find('#ctl00_RadScriptManager1_TSM', first=True).attrs['value']
        viewStateToken = r.find('#__VIEWSTATE', first=True).attrs['value']
        viewStateGenToken = r.find('#__VIEWSTATEGENERATOR', first=True).attrs['value']
        eventValidationToken = r.find('#__EVENTVALIDATION', first=True).attrs['value']
        return [viewStateToken, viewStateGenToken, eventValidationToken, telrk]

    def sessionGen(self, clientID):
        self.session_site = self.auth()        
        tokens = self.parse(self.session_site)
        cookies = self.session_site.cookies
        payload = {
            'ctl00$RadScriptManager1': 'ctl00$RadScriptManager1|ctl00$MainSection$btnSearch',
            'ctl00_RadScriptManager1_TSM': tokens[3],
            '__EVENTTARGET': 'ctl00$MainSection$btnSearch',
            '__VIEWSTATE': tokens[0],
            '__VIEWSTATEGENERATOR': tokens[1],
            '__EVENTVALIDATION': tokens[2],
            'ctl00$MainSection$ListOfContacts$options': 'Active',
            'ctl00$MainSection$ListOfAssets$options': 'Active',
            'ctl00$MainSection$tbSearch': clientID, 
            '__ASYNCPOST': 'true',
            'RadAJAXControlID': 'ctl00_MainSection_RadAjaxManager1'
        }
        raw = urllib.parse.urlencode(payload)
        htmlresponse = self.session.post(URL, data=raw, cookies=cookies, headers={            
                'Content-Type': CONTENTTYPE
            })
        return htmlresponse

    def getData(self,r,internal=False,subjdb=""):

        tr = 'table tbody tr'

        #get client id
        flexDiv = r.html.find('.flexcontainer', first=True)
        accountTbl = flexDiv.find('table', containing='Client')
        for y in accountTbl:
            cID = y.find('tr .dataRecordHeader', first=True).text
            
        #get dbs
        dbstable = r.html.find('#ctl00_MainSection_ListOfAxiumHostedDBs_RadGrid_ctl00', first=True)        
        dbs = dbstable.find(tr, containing='Live')
        data = []

        for x in dbs:                               
            db = x.find('td:nth-child(8)') #get Ajera databases that are live
            #if(internal and subjdb != db): continue  
            if(db[0].attrs == {'class': ('inactive',)}): #skip inactive Ajera databases
                continue

            dbname = x.find('td:nth-child(4)')[0].text #get Ajera DB name column
            server = x.find('td:nth-child(9)')[0].text #get Ajera DB server
            sqlinstance = x.find('td:nth-child(10)')[0].text #get Ajera DB server instance
            
            data.append([cID,server,sqlinstance,db[0].text,dbname])
            if(internal and subjdb == db): return data
        return data
