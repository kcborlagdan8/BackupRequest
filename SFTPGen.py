from distutils.log import error
from sftp import SFTP
import sys

def main():
    x = 1
    c = None
    list = sys.argv[1:]
    errormessage = "SFTP credentials already created or SFTP site is down"
    for l in list:
        html = SFTP().credGen(l)
        while(x != 0):
            try:
                credentials = SFTP().getCred(html)                
                x = 0                
                c = credentials
            except Exception:
                credentials = errormessage
                l += "_"
        c = ",".join(credentials)
        print(f"{l}: {c}")
        if(credentials != errormessage):
            print(f"""
SecureFTP Server: secureftp2.deltek.com
SecureFTP Port: 22
Account Username: {credentials[0]}
Account Password: {credentials[1]}
Account Expires: {credentials[2]}
    *All files and the account will be deleted on this date."""
            )

if __name__ == '__main__':
    main()