from sftp import SFTP

list = ['211118-000760']
for l in list:
    html = SFTP().credGen(l)
    credentials = SFTP().getCred(html)
    print(credentials)
