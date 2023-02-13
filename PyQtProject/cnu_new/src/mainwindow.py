import os
import shutil

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QSystemTrayIcon, QApplication, QMessageBox

import cnu_new
from .manager import *
from .crawler import Crawler


class MainWindow(QMainWindow):

    def __init__(self, ui):
        super(MainWindow, self).__init__()
        self.__ui = ui
        self.__ui.setupUi(self)

        self.m_flag = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 窗口阴影
        self._add_shadow()

        self.__local_init__()

    def __local_init__(self):
        self._slot_builder = SlotsBuilder(self.__ui, self)
        self._thread_builder = ThreadsBuilder()
        self._crawler = Crawler()

        self.sysIcon = QIcon(r'./resources/logo.ico')
        self.setWindowIcon(self.sysIcon)
        self._create_tray_icon()
        self.trayIcon.show()

        self.__ui.frame_4.hide()

        enable_exit: bool = cnu_new.utils.get_config_attr('exit_window')
        if enable_exit:
            self.__ui.radio_exit.setChecked(True)
        else:
            self.__ui.radio_minimize.setChecked(True)

        boss_key: list[str] = cnu_new.utils.get_config_attr('show_window')
        self.__ui.lineEdit_hotkey.setText(' + '.join(boss_key))

        clear_cache: str = cnu_new.utils.get_config_attr('clear_cache')
        self.__ui.box_clearCache.setChecked(clear_cache)

        version: str = cnu_new.utils.get_config_attr('version')
        self.__ui.label_subtitle_6.setText(f'当前版本：v{version}')

        theme_data: dict = cnu_new.utils.load_themes(self.__ui, True)
        theme = cnu_new.utils.get_config_attr('theme')
        cnu_new.utils.change_theme(self.__ui, data=theme_data, name=theme)

    def _add_shadow(self):
        # 添加阴影
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(10)  # 阴影半径
        effect_shadow.setColor(QtCore.Qt.darkBlue)  # 阴影颜色
        self.__ui.centralwidget.setGraphicsEffect(effect_shadow)  # 将设置套用到widget窗口中

    def _create_tray_icon(self):
        aRestore = QAction('恢复(&R)', self, triggered=self.showNormal)
        aMinimize = QAction('最小化(&M)', self, triggered=self.showMinimized)
        aQuit = QAction('退出(&Q)', self, triggered=QApplication.instance().quit)

        menu = QMenu(self)
        menu.addAction(aRestore)
        menu.addAction(aMinimize)
        menu.addAction(aQuit)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(self.sysIcon)
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.activated.connect(self._icon_activated)

    def _icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()

    def closeEvent(self, event):
        if not cnu_new.utils.get_config_attr('exit_window'):
            self.showMinimized()
            event.ignore()
            return

        reply = QtWidgets.QMessageBox.question(self, '提示', "确认退出吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if cnu_new.utils.get_config_attr('clear_cache'):
                shutil.rmtree(self._crawler.CACHE_DEFAULT_PATH)
            event.accept()
            QApplication.instance().quit()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False

    def _inject_slot(self):
        # 注入 slot内部依赖的 其他slot
        self._header_slots.inner_view = self._view_slots
        self._header_slots.inner_auther = self._auther_slots

        self._view_slots.inner_header = self._header_slots
        self._view_slots.inner_sidebar = self._sidebar_slots
        self._view_slots.inner_author = self._auther_slots

        self._auther_slots.inner_header = self._header_slots
        self._auther_slots.inner_sidebar = self._sidebar_slots

    def _inject_builder(self):
        # 注入 slot内部依赖的 thread_builder
        self._view_slots.inner_thread_builder = self._thread_builder
        self._auther_slots.inner_thread_builder = self._thread_builder

    def _inject_crawler(self):
        # 注入 slot内部依赖的 crawler
        self._view_slots.crawler = self._crawler
        self._auther_slots.crawler = self._crawler
        self._setting_slots.crawler = self._crawler

    def _inject_crawler_dependence(self):
        # 注入爬虫需要的依赖
        cache_default_path = cnu_new.utils.get_config_attr('cache_path')
        if not cache_default_path:
            cache_default_path = cnu_new.utils.get_config_attr('default_cache_path')
        self._crawler.CACHE_DEFAULT_PATH = cache_default_path
        self.__ui.lineEdit_cache.setText(os.path.abspath(cache_default_path))

        works_default_dir_path = cnu_new.utils.get_config_attr('save_path')
        if not works_default_dir_path:
            works_default_dir_path = cnu_new.utils.get_config_attr('default_save_path')
        self._crawler.WORKS_DEFAULT_DIR_PATH = works_default_dir_path
        self.__ui.lineEdit_dir.setText(os.path.abspath(works_default_dir_path))

        works_default_full_path = cnu_new.utils.get_config_attr('full_path')
        if not works_default_full_path:
            works_default_full_path = cnu_new.utils.get_config_attr('default_full_path')
        self._crawler.WORKS_DEFAULT_FULL_PATH = works_default_full_path
        self.__ui.lineEdit_full.setText(os.path.abspath(works_default_full_path))

    def _injection(self):
        self._inject_slot()
        self._inject_builder()
        self._inject_crawler()
        self._inject_crawler_dependence()

        self._crawler.make_dir()

    def bind(self):
        # 依赖注入
        self._header_slots: HeaderSlot = self._slot_builder.header
        self._sidebar_slots: SidebarSlot = self._slot_builder.sidebar
        self._view_slots: ViewSlot = self._slot_builder.view
        self._auther_slots: AutherSlot = self._slot_builder.auther
        self._setting_slots: SettingSlot = self._slot_builder.setting

        self._header_slots.connect()
        self._sidebar_slots.connect()
        self._view_slots.connect()
        self._auther_slots.connect()
        self._setting_slots.connect()

        self._thread_builder.build_thread(None, window=self, hot_key=True)
        self._injection()

    @property
    def slot_builder(self):
        return self._slot_builder

    @slot_builder.setter
    def slot_builder(self, factory):
        self._slot_builder = factory

    @property
    def thread_builder(self):
        return self._thread_builder

    @thread_builder.setter
    def thread_builder(self, factory):
        self._thread_builder = factory

    @property
    def entity_factory(self):
        return self._entity_factory

    @entity_factory.setter
    def entity_factory(self, factory):
        self._entity_factory = factory
