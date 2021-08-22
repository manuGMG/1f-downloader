import os
import json
import requests
import lxml
import time
from .helpers import (get_proxy, convert_size, download_speed, is_valid_link)
from .pyaria2 import PyAria2

def download(url, password = None, payload={'dl_no_ssl': 'on', 'dlinline': 'on'}):
        PyAria2().__init__
        if is_valid_link(url):
            if not 'https://' in url[0:8] and not 'http://' in url[0:7]:
                url = f'https://{url}'
            if '&' in url:
                url = url.split('&')[0]
            if '/dir/' in url:
                folder = requests.get(f'{url}?json=1')
                folder = folder.json()
                print(f'Loaded folder {url} with {len(folder)} files.')
                for f in folder:
                    download(f['link'], password)
        else:
            print(f'{url} is not a valid 1Fichier link.')
            return

        print(f'Starting download: {url}..')

        while True:
            if password: payload['pass'] = password
            proxies = get_proxy()
            try:
                r = requests.post(url, payload, proxies=proxies)
                html = lxml.html.fromstring(r.content)
                if html.xpath('//*[@id="pass"]'):
                    password = input(f'Password needed for {url}: ')
                    payload['pass'] = password
            except:
                # Proxy failed.
                print(f'\rBypassing..\n', end='', flush=True)
                pass
            else:
                # Proxy worked.
                break
        
        if not html.xpath('/html/body/div[4]/div[2]/a'):
            if 'Bad password' in r.text:
                password = input(f'(Wrong password) Password needed for {url}: ')
                payload['pass'] = password
            print("Can't download, retrying......")
            download(url)
        else:
            print("Bypassed,Getting link......")
            old_url = url
            url = html.xpath('/html/body/div[4]/div[2]/a')[0].get('href')
            opts = {"header": ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36', 'Referer: '+old_url+'']}

            PyAria2().addUri([url], options=opts)
            print("Download sent to aria2.")
            return
