from sftp import SFTP

list = ['211013-000245']
for l in list:
    html = SFTP().credGen(l)
    credentials = SFTP().getCred(html)
    print(credentials)
