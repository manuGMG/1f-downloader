import sys
import os
from core.download import cli_download_aria2

# Pyinstaller
excludedhooks=['PyQt5']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'''
 __  __ _      _     _                     _ _ 
/_ |/ _(_)    | |   (_)                   | | |
 | | |_ _  ___| |__  _  ___ _ __ ______ __| | |
 | |  _| |/ __| '_ \| |/ _ \ '__|______/ _` | |
 | | | | | (__| | | | |  __/ |        | (_| | |
 |_|_| |_|\___|_| |_|_|\___|_|         \__,_|_|

Usage: {os.path.basename(__file__)} link (password)''')
    elif len(sys.argv) == 2:
        cli_download_aria2.download(sys.argv[1])
    elif len(sys.argv) == 3:
        cli_download_aria2.download(sys.argv[1], sys.argv[2])