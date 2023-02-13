import asyncio

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap
from system_hotkey import SystemHotkey

import cnu_new
from .manager import Atlas, Works


class GetAtlasData(QThread):
    get_data_signal = pyqtSignal(Atlas)

    def __init__(self, crawler, atlas_url):
        super(GetAtlasData, self).__init__()
        self.works_url = atlas_url
        self.__crawler = crawler

    def run(self) -> None:
        data = self.__crawler.get_atlas(self.works_url)
        self.get_data_signal.emit(Atlas(data))


class GetUserData(QThread):
    get_user_data_signal = pyqtSignal(Works)

    def __init__(self, crawler, author_href):
        super(GetUserData, self).__init__()
        self.__crawler = crawler
        self.author_href = author_href

    def run(self) -> None:
        data = self.__crawler.get_works(self.author_href)
        self.get_user_data_signal.emit(Works(data))


class AtlasPreview(QThread):
    def __init__(self, crawler, ui, image_url, work_url):
        super(AtlasPreview, self).__init__()
        self.__crawler = crawler
        self.ui = ui
        self.image_url = image_url
        self.work_url = work_url

    def run(self) -> None:
        content = self.__crawler.atlas_preview(self.image_url)

        if content[0] != 200 and content[1] is None:
            self.ui.label_viewer.setText(f'{content[0]}\nConnection To This Page {self.work_url} Failed.')
        else:
            img = QImage.fromData(content[1])
            pixmap = QPixmap(QPixmap.fromImage(img)).scaled(self.ui.label_viewer.size(),
                                                            aspectRatioMode=Qt.KeepAspectRatio)
            self.ui.label_viewer.setPixmap(pixmap)


class UserPreview(QThread):
    user_preview_signal = pyqtSignal(list)

    def __init__(self, crawler, thumbnail_url_list: list):
        super(UserPreview, self).__init__()
        self.__crawler = crawler
        self.thumbnail_url_list = thumbnail_url_list

    def run(self) -> None:
        serialized_list = []
        for url in self.thumbnail_url_list:
            content = self.__crawler.atlas_preview(url)
            if content is not None:
                serialized_list.append(content[1])

        self.user_preview_signal.emit(serialized_list)


class Downloader(QThread):
    download_signal = pyqtSignal()

    def __init__(self, crawler, atlas, download_indexes, cus_path):
        super(Downloader, self).__init__()
        self.__crawler = crawler
        self.atlas = atlas
        self.download_indexes = sorted(download_indexes)
        self.cus_path = cus_path

    def run(self) -> None:
        asyncio.run(self.__crawler.start_downloader(self.atlas, self.download_indexes, self.cus_path))
        self.download_signal.emit()


class HotKeyThread(QThread, SystemHotkey):
    hot_key_thread_signal = pyqtSignal()

    def __init__(self, window):
        super(HotKeyThread, self).__init__()
        self.window = window
        keys = cnu_new.utils.get_config_attr('show_window')
        self.register(tuple(keys), callback=lambda x: self.start())
        self.hot_key_thread_signal.connect(self.hot_key_event)

    def run(self):
        self.hot_key_thread_signal.emit()

    def hot_key_event(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == QtCore.Qt.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def quit_thread(self):
        if self.isRunning():
            self.quit()
