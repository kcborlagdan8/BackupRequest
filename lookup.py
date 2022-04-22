import dns.resolver
import re

#get DB Server
def getDBfromCNAMEDFVE(cname):
    cnames = {
	"h5.deltekfirst.com.": "USEAPDVE5DB1",
	"h9.deltekfirst.com.": "USEAPDVE7DB1",
	"h11.deltekfirst.com.": "USEAPDVE8DB1",
	"h1.deltekfirst.com.": "USEAPDVE1DB1",
	"h7.deltekfirst.com.": "USEAPDVE6DB1",
	"h15.deltekfirst.com.": "USEAPDVE9DB1",
	"h17.deltekfirst.com.": "APAUPDVE2DB1",
	"h19.deltekfirst.com.": "USEAPDVE3DB1",
	"h23.deltekfirst.com.": "USEAPDVE4DB1",
	"h25.deltekfirst.com.": "USEAPDVE10DB1",
	"h27.deltekfirst.com.": "USEAPDVE11DB1",
	"h29.deltekfirst.com.": "EUWEPDVE12DB1",
	"h31.deltekfirst.com.": "USEAPDVE13DB1",
	"h33.deltekfirst.com.": "CACEPDVE14DB1",
	"h35.deltekfirst.com.": "USEAPDVE15DB1",
	"h37.deltekfirst.com.": "USEAPDVE16DB1",
    "h39.deltekfirst.com.": "USEAPDVE17DB1"
    }
    return cnames.get(cname, "XXXXXX")

def dnsresolver(fqdn):
    result = dns.resolver.resolve(fqdn, 'CNAME')
    for cnameval in result:
        cname = cnameval.target
    return str(cname)

def getVTPod(fqdn):
	region = "USEA"
	try:
		pod = re.search('vt(.+?).deltekfirst.com.', fqdn).group(1)
		if(pod in ["16","36"]): region = "EUWE"
		if(pod == "17"): region = "APAU"
		if(pod == "18"): region = "CACE"
		dbserver = f"{region}PDVT{pod}DB1"
	except AttributeError: dbserver = "XXXXXX"

	return dbserver
	
def getInstanceName(domain):
	try:	
		#instance = re.search('(.+?)@(.+?).com', domain).group(2).title()
		instance = re.search('(.+?).com', domain).group(1).title()
	except AttributeError:
		instance = ""
	return re.sub('[^A-Za-z0-9]+', '', instance) #remove special characters

def getAxiumAccountNum(subj):
	try:	
		axiumNum = re.search('D00(.+?)_(.+?)', subj).group(1).title()
	except AttributeError:
		axiumNum = ""
	return (axiumNum)