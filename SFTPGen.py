from sftp import SFTP
import sys

def main():
    list = sys.argv[1:]
    for l in list:
        html = SFTP().credGen(l)
        credentials = SFTP().getCred(html)
        print(credentials)

if __name__ == '__main__':
    main()