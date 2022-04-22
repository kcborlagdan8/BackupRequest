from DataViewer import DataViewer

import sys

#cID = sys.argv[1:]
dv = DataViewer()
html = dv.sessionGen('16314')
#print(html)
db = dv.getData(html)   
print(db)