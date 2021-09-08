import os
from .download import *
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QStandardItem
from .helpers import is_valid_link, DownloadRecursionError

class WorkerSignals(QObject):
    download_signal = pyqtSignal(list, str, bool, str, int)
    alert_signal = pyqtSignal(str)
    update_signal = pyqtSignal(list, list)
    unpause_signal = pyqtSignal(list, str, bool, str)

class FilterWorker(QRunnable):
    def __init__(self, actions, cached_download = '', password = ''):
        super(FilterWorker, self).__init__()
        self.links = actions.gui.links
        self.cached_downloads = actions.cached_downloads
        self.cached_download = cached_download
        self.signals = WorkerSignals()
        self.dl_name = cached_download[1] if self.cached_download else None
        self.password = cached_download[2] if self.cached_download else (password if password else None)
        self.progress = cached_download[3] if self.cached_download else None

    @pyqtSlot()
    def run(self):
        self.valid_links = []

        if isinstance(self.links, str):
            self.valid_links = [self.links]
        else:
            links = self.links.toPlainText().splitlines()

            for link in links:
                link = link.strip()
                if is_valid_link(link):
                    if not 'https://' in link[0:8] and not 'http://' in link[0:7]:
                        link = f'https://{link}'
                    if '&' in link:
                        link = link.split('&')[0]
                    self.valid_links.append(link)

            if not self.valid_links:
                self.signals.alert_signal.emit('The link(s) you inserted were not valid.')

        for link in self.valid_links:
            if '/dir/' in link:
                folder = requests.get(f'{link}?json=1')
                folder = folder.json()
                for f in folder:
                    link = f['link']
                    info = [f['filename'], convert_size(int(f['size']))]
                    info.extend(['Added', '0 B/s', ''])
                    row = []

                    for val in info:
                        data = QStandardItem(val)
                        data.setFlags(data.flags() & ~Qt.ItemIsEditable)
                        row.append(data)

                    if f['password'] == 1:
                        password = QStandardItem(self.password)
                        row.append(password)
                    else:
                        no_password = QStandardItem('No password')
                        no_password.setFlags(data.flags() & ~Qt.ItemIsEditable)
                        row.append(no_password)

                    self.signals.download_signal.emit(row, link, True, self.dl_name, self.progress)
                    if self.cached_download:
                        self.cached_downloads.remove(self.cached_download)           
            else:
                info = get_link_info(link)
                if info is not None:
                    is_private = True if info[0] == 'Private File' else False
                    info[0] = self.dl_name if self.dl_name else info[0]
                    info.extend(['Added', '0 B/s', ''])
                    row = []

                    for val in info:
                        data = QStandardItem(val)
                        data.setFlags(data.flags() & ~Qt.ItemIsEditable)
                        row.append(data)

                    if is_private:
                        password = QStandardItem(self.password)
                        row.append(password)
                    else:
                        no_password = QStandardItem('No password')
                        no_password.setFlags(data.flags() & ~Qt.ItemIsEditable)
                        row.append(no_password)

                    self.signals.download_signal.emit(row, link, True, self.dl_name, self.progress)
                    if self.cached_download:
                        self.cached_downloads.remove(self.cached_download)

class DownloadWorker(QRunnable):
    def __init__(self, link, table_model, data, settings, dl_name = ''):
        super(DownloadWorker, self).__init__()
        # Args
        self.link = link
        self.table_model = table_model
        self.data = data
        self.signals = WorkerSignals()
        self.paused = self.stopped = self.complete = False
        self.dl_name = dl_name

        # Proxies
        self.proxies = []

        # Default settings
        self.timeout = 30
        self.dl_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        self.proxy_settings = None

        # Override defaults
        if settings: 
            if settings[0]: self.dl_directory = settings[0]
            if settings[2]: self.timeout = settings[2]
            if settings[3]: self.proxy_settings = settings[3]

    @pyqtSlot()
    def run(self):
        try:
            dl_name = download(self)
        except DownloadRecursionError:
            self.signals.update_signal.emit(self.data, [None, None, 'Error, Please retry', '0 B/s'])
            return
        self.dl_name = dl_name

        if dl_name and self.stopped:
            try:
                os.remove(self.dl_directory + '/' + dl_name)
            except:
                print(f'Failed to remove: {self.dl_directory}/{dl_name}')

        if self.paused:
            self.signals.update_signal.emit(self.data, [None, None, 'Paused', '0 B/s'])
        else:
            if not dl_name:
                self.complete = True

    def stop(self, i):
        self.table_model.removeRow(i)
        self.stopped = True
    
    def pause(self):
        if not self.complete:
            self.paused = True

    def resume(self):
        if self.paused == True:
            self.paused = False
            self.signals.unpause_signal.emit(self.data, self.link, False, self.dl_name)
    
    def return_data(self):
        if not self.stopped and not self.complete:
            data = []
            data.append(self.link)
            data.append(self.dl_name) if self.dl_name else data.append(None)
            data.append(self.data[5].text()) if self.data[5].text() != 'No password' else data.append(None)
            data.append(self.data[4].value())
            return data
