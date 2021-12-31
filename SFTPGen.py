from sftp import SFTP
import sys

def main():
    list = sys.argv[1:]
    for l in list:
        html = SFTP().credGen(l)
        credentials = SFTP().getCred(html)
        print(credentials)
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