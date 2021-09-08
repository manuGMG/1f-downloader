import requests
import os
import time
import lxml.html
import logging
import PyQt5.sip
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QProgressBar
from .helpers import *
from sys import getrecursionlimit

def download(worker, payload = {'dl_no_ssl': 'on', 'dlinline': 'on'}, downloaded_size = 0, iteration = 0):
    '''
    Name is self-explanatory.
    1 - Get direct 1Fichier link using proxies.
    2 - Attempt to download the file.
    '''
    if (iteration >= getrecursionlimit() - 1):
        logging.debug("Max recursion reached!")
        raise DownloadRecursionError("Max recursion reached!")
    if worker.dl_name:
        try:
            downloaded_size = os.path.getsize(worker.dl_directory + '/' + worker.dl_name)
            logging.debug(f'Previous file found. Downloaded size: {downloaded_size}')
        except FileNotFoundError:
            downloaded_size = 0
            logging.debug('Previous file not found.')

    url = worker.link
    i = 1
    while True:
        if worker.stopped or worker.paused:
            return None if not worker.dl_name else worker.dl_name

        while True:
            if not PyQt5.sip.isdeleted(worker.data[5]):
                if worker.data[5].text() == '':
                    worker.signals.update_signal.emit(worker.data, [None, None, 'Waiting for password'])
                    time.sleep(2)
                else:
                    break
                if worker.stopped or worker.paused:
                    return None if not worker.dl_name else worker.dl_name

        worker.signals.update_signal.emit(worker.data, [None, None, f'Bypassing ({i})'])
        if worker.proxies:
            logging.debug('Popping proxy.')
            p = worker.proxies.pop()
        else:
            logging.debug('Getting proxy.')
            worker.proxies = get_proxies(worker.proxy_settings)

        try:
            p = worker.proxies.pop()
            r = requests.post(url, payload, proxies=p, timeout=worker.timeout)
            html = lxml.html.fromstring(r.content)
            if html.xpath('//*[@id="pass"]'):
                payload['pass'] = worker.data[5].text()
                r = requests.post(url, payload, proxies=p, timeout=worker.timeout)
        except:
            # Proxy failed.
            logging.debug('Proxy failed.')
            i += 1
        else:
            # Proxy worked.
            logging.debug('Proxy worked.')
            if worker.stopped or worker.paused:
                return None if not worker.dl_name else worker.dl_name

            worker.signals.update_signal.emit(worker.data, [None, None, 'Bypassed'])
            break

    if not html.xpath('/html/body/div[4]/div[2]/a'):
        logging.debug('Failed to parse direct link.')
        if 'Bad password' in r.text:
            worker.signals.update_signal.emit(worker.data, [None, None, 'Wrong password'])
            while True:
                if not PyQt5.sip.isdeleted(worker.data[5]):
                    if worker.data[5].text() == payload['pass']:
                        time.sleep(2)
                    else:
                        break
                else:
                    worker.stopped = True
                    return None if not worker.dl_name else worker.dl_name
        download(worker, iteration=iteration + 1)
    else:
        logging.debug('Parsed direct link.')
        old_url = url
        url = html.xpath('/html/body/div[4]/div[2]/a')[0].get('href')
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Referer': old_url,
            'Range': f'bytes={downloaded_size}-' 
        }

        r = requests.get(url, stream=True, headers=headers, proxies=p)
        if 'Content-Disposition' in r.headers:
            logging.debug('Starting download.')
            name = r.headers['Content-Disposition'].split('"')[1]

            if worker.dl_name:
                name = worker.dl_name
            elif os.path.exists(f'{worker.dl_directory}/{name}'):
                i = 1
                while os.path.exists(f'{worker.dl_directory}/({i}) {name}'):
                    i += 1
                name = f'({i}) {name}'

            name = f'{name}.unfinished' if name[-11:] != '.unfinished' else name
            worker.dl_name = name

            if worker.stopped or worker.paused: return name

            worker.signals.update_signal.emit(worker.data, [name[:-11], convert_size(float(r.headers['Content-Length'])+downloaded_size)])

            with open(worker.dl_directory + '/' + name, 'ab') as f:
                worker.signals.update_signal.emit(worker.data, [None, None, 'Downloading'])
                chunk_size = 8192
                bytes_read = 0
                start = time.time()
                for chunk in r.iter_content(chunk_size):
                    f.write(chunk)
                    bytes_read += len(chunk)
                    total_per = 100 * (float(bytes_read) + downloaded_size)
                    total_per /= float(r.headers['Content-Length']) + downloaded_size
                    dl_speed = download_speed(bytes_read, start)
                    if worker.stopped or worker.paused: return name
                    worker.signals.update_signal.emit(worker.data, [None, None, 'Downloading', dl_speed, round(total_per, 1)])
            os.rename(worker.dl_directory + '/' + name, worker.dl_directory + '/' + name[:-11])
            worker.signals.update_signal.emit(worker.data, [None, None, 'Complete'])
        else:
            logging.debug('No Content-Disposition header. Restarting download.')
            download(worker, iteration=iteration + 1)
    return
