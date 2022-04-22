import requests
from lxml import etree
from requests_ntlm import HttpNtlmAuth
import urllib.parse
from bs4 import BeautifulSoup

import json
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path, 'r') as config_file:
    config = json.loads(config_file.read())
    sftpconfig = config['sftp']
    deltekconfig = config['deltekpages']

USERNAME = deltekconfig['username']
PASSWORD = deltekconfig['password']
URL = sftpconfig['url']
CONTENTTYPE = deltekconfig['content-type']
USERAGENT = deltekconfig['user-agent']

class SFTP:
    def __init__(self):
        pass

    def auth(self):
        self.authcookie = HttpNtlmAuth(
            USERNAME,
            PASSWORD
        )
        self.session = requests.Session()
        tokenRequest = self.session.get(
            URL,
            auth=self.authcookie
        )
        return tokenRequest

    def parse(self, token):
        parser = etree.HTMLParser()
        tree = etree.fromstring(token.text, parser)
        viewStateToken = tree.xpath('//form//input[@name="__VIEWSTATE"]/@value')[0]
        viewStateGenToken = tree.xpath('//form//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        eventValToken = tree.xpath('//form//input[@name="__EVENTVALIDATION"]/@value')[0]
        return [viewStateToken,viewStateGenToken,eventValToken]


    def sessionGen(self, rnt):
        self.session_site = self.auth()
        tokens = self.parse(self.session_site)
        cookies = self.session_site.cookies
        
        payload = {
            '__VIEWSTATE': tokens[0],
            '__VIEWSTATEGENERATOR': tokens[1],
            '__EVENTVALIDATION': tokens[2],
            'ctl00$ContentPlaceHolder1$UName':rnt, 
            'ctl00$ContentPlaceHolder1$ReqFTP':'Create Account',
        }
        raw = urllib.parse.urlencode(payload)
        html_text = self.session.post(URL, data=raw, cookies=cookies, headers={            
                'Content-Type': CONTENTTYPE
            }).text
        return html_text

    def getCred(self, html):
        soup = BeautifulSoup(html, 'lxml')
        sftpUsername = soup.find(id='ContentPlaceHolder1_ftpUsername').text
        sftpPass= soup.find(id='ContentPlaceHolder1_ftpPassword').text
        sftpExpiry = soup.find(id='ContentPlaceHolder1_ftpExpires').text

        return [sftpUsername,sftpPass,sftpExpiry]