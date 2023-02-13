import datetime
import functools
import re

import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QMessageBox, QFileDialog

import cnu_new
from .Ui_Window import Ui_MainWindow


class HeaderSlot:
    _instance = None

    def __init__(self, ui: Ui_MainWindow, window):
        self.__ui = ui
        self.__window = window

        self.atlas_url = ""
        self.auther_href = ""

        self.__set_signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HeaderSlot, cls).__new__(cls)
        return cls._instance

    def __set_signal(self):
        self._signal_btn_search = self.__ui.btn_search.clicked
        self._signal_line_edit_url = self.__ui.line_edit_url.returnPressed

    def connect(self):
        self._signal_btn_search.connect(self.check_url)
        self._signal_line_edit_url.connect(self.check_url)

    def check_url(self):
        if not self.__ui.line_edit_url.text():
            return

        text = self.__ui.line_edit_url.text()
        self.__ui.line_edit_url.setText('')
        works = re.search(r'http://www.cnu.cc/works/\d{6}$', text)
        portfolio = re.search(r'http://www.cnu.cc/users/\d{6,7}$|http://www.cnu.cc/users/\d{6,7}\?page=\d+$', text)

        if works:
            self.atlas_url = text
            self.inner_view.get_atlas_data()

        elif portfolio:
            self.auther_href = f'{text}?page=1'
            self.inner_auther.get_user_data(True)

    @property
    def inner_view(self):
        return self._view_slot

    @inner_view.setter
    def inner_view(self, value):
        self._view_slot: ViewSlot = value

    @property
    def inner_auther(self):
        return self._auther_slot

    @inner_auther.setter
    def inner_auther(self, value):
        self._auther_slot: AutherSlot = value

    @property
    def inner_setting(self):
        return self._setting_slot

    @inner_setting.setter
    def inner_setting(self, value):
        self._setting_slot: SettingSlot = value


class SidebarSlot:
    _instance = None

    def __init__(self, ui: Ui_MainWindow, window):
        self.__ui = ui
        self.__window = window

        self.STACK_VIEW_INDEX = 0
        self.STACK_AUTHER_INDEX = 1
        self.STACK_SETTING_INDEX = 2

        self.__set_signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SidebarSlot, cls).__new__(cls)
        return cls._instance

    def __set_signal(self):
        self._signal_btn_view = self.__ui.btn_view.clicked
        self._signal_btn_auther = self.__ui.btn_auther.clicked
        self._signal_btn_setting = self.__ui.btn_setting.clicked

    def display(self, index):
        if index == self.STACK_VIEW_INDEX:
            self.__ui.frame_info.show()
            self.__ui.frame_4.hide()
            self.__ui.btn_view.setChecked(True)

        elif index == self.STACK_AUTHER_INDEX:
            self.__ui.frame_info.hide()
            self.__ui.frame_4.hide()
            self.__ui.btn_auther.setChecked(True)

        elif index == self.STACK_SETTING_INDEX:
            self.__ui.frame_info.hide()
            self.__ui.frame_4.show()
            self.__ui.btn_setting.setChecked(True)

        self.__ui.stackedWidget.setCurrentIndex(index)

    def connect(self):
        self._signal_btn_view.connect(lambda: self.display(self.STACK_VIEW_INDEX))
        self._signal_btn_auther.connect(lambda: self.display(self.STACK_AUTHER_INDEX))
        self._signal_btn_setting.connect(lambda: self.display(self.STACK_SETTING_INDEX))


class ViewSlot:
    _instance = None

    def __init__(self, ui: Ui_MainWindow, window):
        self.__ui = ui
        self.__window = window

        self.__STATU_CODE_OK = 200

        self.atlas_entity = None

        self._thread_builder = None

        self.__set_signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ViewSlot, cls).__new__(cls)
        return cls._instance

    def __set_signal(self):
        self._signal_table_img = self.__ui.table_img.cellClicked
        self._signal_btn_download = self.__ui.btn_download.clicked

    def _get_selected_items_indexes(self):
        selected_items = self.__ui.table_img.selectedItems()  # [xxx_1, xxx_2, ...]
        indexes = []
        for v in selected_items:
            item = v.text().rsplit('_')[-1]
            if item.isdigit():
                indexes.append(int(item) - 1)
        return indexes

    def _download_img(self):
        self._selected_items_indexes = self._get_selected_items_indexes()
        if not self._selected_items_indexes:
            return QMessageBox.warning(self.__window, '错误', '还未选择图片！')

        self.cus_path = QFileDialog.getExistingDirectory(None, '选择文件夹', self._crawler.WORKS_DEFAULT_DIR_PATH)
        if self.cus_path:
            self._start_downloader()

    def _start_downloader(self):
        self._Downloader_thread = self._thread_builder.build_thread(self._crawler, atlas=self.atlas_entity,
                                                                    download_indexes=self._selected_items_indexes,
                                                                    cus_path=self.cus_path, downloader=True)
        self._Downloader_thread.download_signal.connect(lambda: self._btn_enabled(True))
        self._Downloader_thread.start()

    def _btn_enabled(self, cancel=False):
        if cancel is True:
            self.customize_path = None

        # self.__ui.btn_save.setEnabled(True)
        # self.__ui.btn_save_as.setEnabled(True)
        # self.__ui.pb_downloading.hide()
        return QMessageBox.information(self.__window, '通知',
                                       f'下载完成！\n\n完成下载耗时: {self._crawler.complete_time}秒')

    def _set_info(self, entity):
        self.__ui.btn_info_recommend.setText(entity.recommend_count)
        self.__ui.btn_info_read.setText(entity.read_count)
        self.__ui.btn_info_time.setText(entity.release_date)
        self.__ui.btn_info_auther.setText(entity.auther)

    def set_atlas_table(self, entity):
        self._set_info(entity)
        self.atlas_entity = entity
        self.inner_header.auther_href = entity.auther_href

        if self.atlas_entity.statu_code != self.__STATU_CODE_OK:
            self._extracted_from_set_atlas_table()
        else:
            self.__ui.table_img.setRowCount(len(entity))
            for i, _ in enumerate(entity.images_url):
                cell = QTableWidgetItem(f"{entity.atlas_title}_{i + 1}")
                cell.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.__ui.table_img.setItem(i, 0, cell)

            self.inner_sidebar.display(0)
            self.inner_author.get_user_data()

    # TODO Rename this here and in `set_atlas_table`
    def _extracted_from_set_atlas_table(self):
        # 清空列表
        self.__ui.table_img.setRowCount(0)
        self.__ui.table_img.clearContents()

        current_row_count = self.__ui.table_img.rowCount()
        self.__ui.table_img.insertRow(current_row_count)
        cell = QTableWidgetItem(
            f"{datetime.datetime.now().strftime('(%H:%M:%S)')} 错误！当前网页状态码：{self.atlas_entity.statu_code}")
        cell.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.__ui.table_img.setItem(current_row_count, 0, cell)

    def get_atlas_data(self):
        self.atlas_url = self.inner_header.atlas_url
        self._GetData_thread = self.inner_thread_builder.build_thread(self._crawler, atlas_url=self.atlas_url,
                                                                      get_data=True)
        self._GetData_thread.get_data_signal.connect(self.set_atlas_table)
        self._GetData_thread.start()

    def atlas_preview(self):
        image_list = None
        if self.atlas_entity:
            image_list = self.atlas_entity.images_url
            if not image_list:
                self._WorksPreview_thread = self.inner_thread_builder.build_thread(self._crawler, ui=self.__ui,
                                                                                   atlas_url=self.inner_header.atlas_url,
                                                                                   image_url=self.inner_header.atlas_url,
                                                                                   atlas_preview=True)
                self._WorksPreview_thread.start()
                return

        if self.__ui.table_img.selectedItems():
            url_index = self.__ui.table_img.selectedItems()[0].text().rsplit('_', 1)[-1]
            if url_index.isdigit():
                image_url = f"{image_list[int(url_index) - 1]}"

                self._WorksPreview_thread = self.inner_thread_builder.build_thread(self._crawler, ui=self.__ui,
                                                                                   atlas_url=self.inner_header.atlas_url,
                                                                                   image_url=image_url,
                                                                                   atlas_preview=True)
                self._WorksPreview_thread.start()

    def connect(self):
        self._signal_table_img.connect(self.atlas_preview)
        self._signal_btn_download.connect(self._download_img)

    @property
    def inner_header(self) -> HeaderSlot:
        return self._header

    @inner_header.setter
    def inner_header(self, value: HeaderSlot):
        self._header: HeaderSlot = value

    @property
    def inner_sidebar(self):
        return self._sidebar

    @inner_sidebar.setter
    def inner_sidebar(self, value):
        self._sidebar: SidebarSlot = value

    @property
    def inner_author(self):
        return self._author_slot

    @inner_author.setter
    def inner_author(self, value):
        self._author_slot: AutherSlot = value

    @property
    def crawler(self):
        return self._crawler

    @crawler.setter
    def crawler(self, value):
        self._crawler = value

    @property
    def inner_thread_builder(self):
        return self._thread_builder

    @inner_thread_builder.setter
    def inner_thread_builder(self, value):
        self._thread_builder = value


class AutherSlot:
    _instance = None

    def __init__(self, ui: Ui_MainWindow, window):
        self.__ui = ui
        self.__window = window

        self.STACK_VIEW = 0
        self.STACK_AUTHER = 1
        self.ROW_COUNT = 5
        self.COL_COUNT = 4
        self._DEFAULT_PREV_COUNT = 1
        self._DEFAULT_NEXT_COUNT = 2

        self._GetUserData_thread = None
        self._UserPreview_thread = None

        self.next_flag = None
        self.prev_count = None
        self.next_count = None
        self.auther_href = None
        self.__set_signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AutherSlot, cls).__new__(cls)
        return cls._instance

    def __set_signal(self):
        self._signal_btn_prev = self.__ui.btn_prev.clicked
        self._signal_btn_next = self.__ui.btn_next.clicked
        self._signal_btn_paste = self.__ui.btn_paste.clicked
        self._signal_table_auther = self.__ui.table_auther.cellClicked

    def _get_thumbnail_url_list(self, works, jump):
        self.works = works

        if self.works.is_empty():
            self.next_flag = False
            return QMessageBox.information(self.__window, '提示', '已经没有作品啦~')

        self.next_flag = True
        url_list = [data['content']['thumbnail_url'] for data in works]
        self._works_preview(url_list, jump)

    def _works_preview(self, thumbnail_url_list, jump):
        self._UserPreview_thread = self.inner_thread_builder.build_thread(self.crawler,
                                                                          thumbnail_url_list=thumbnail_url_list,
                                                                          user_preview=True)
        self._UserPreview_thread.user_preview_signal.connect(self._set_works_table)
        self._UserPreview_thread.start()

        if jump:
            self.inner_sidebar.display(self.STACK_AUTHER)

    def _create_table_cell(self, serialized_list):
        cell_list = []
        for value in serialized_list:
            cell_label = QLabel()
            cell_label.resize(338, 315)
            cell_label.setAlignment(Qt.AlignCenter)
            image = QImage().fromData(value)
            pixmap = QPixmap(QPixmap.fromImage(image)).scaled(cell_label.size(), aspectRatioMode=Qt.KeepAspectRatio)

            cell_label.setPixmap(pixmap)
            cell_list.append(cell_label)

        total_cell_count = self.ROW_COUNT * self.COL_COUNT
        while len(cell_list) < total_cell_count:
            empty_label = QLabel()
            empty_label.resize(338, 315)
            empty_label.setAlignment(Qt.AlignCenter)
            cell_list.append(empty_label)

        return cell_list

    def _set_works_table(self, bytes_list):
        if not bytes_list:
            return QMessageBox.warning(self.__window, 'Error', '图集缩略图获取失败！')

        data = self._create_table_cell(bytes_list)

        self.__ui.table_auther.setEnabled(True)
        self.__ui.table_auther.setRowCount(self.ROW_COUNT)
        self.__ui.table_auther.setColumnCount(self.COL_COUNT)

        cell_count = 0
        for row in range(self.ROW_COUNT):
            for col in range(self.COL_COUNT):
                self.__ui.table_auther.setCellWidget(row, col, data[cell_count])
                c_item = QTableWidgetItem(f'{cell_count}')
                c_item.setTextAlignment(Qt.AlignCenter)
                self.__ui.table_auther.setItem(row, col, c_item)

                cell_count += 1

    def _paste_url(self):
        selected_item = self.__ui.table_auther.selectedItems()
        if len(selected_item) > 1:
            return QMessageBox.warning(self.__window, 'Warning', '只能选择一个图集！')
        if len(selected_item) < 1:
            return

        item = selected_item[0]
        if not item.text().isdigit():
            return
        if self.works.register_user_dict(int(item.text())):
            self.__ui.line_edit_url.setText(self.works.atlas_url)

    def _check_url(self):
        self.inner_header.check_url()
        self.inner_sidebar.display(self.STACK_VIEW)

    def _get_prev_and_next_count(self):
        if not self.inner_header.auther_href:
            return
        page, current_count = self.inner_header.auther_href.rsplit('=', 1)
        self.prev_count = int(current_count) - 1
        self.next_count = int(current_count) + 1

        if self.prev_count <= 0:
            self.prev_count = self._DEFAULT_PREV_COUNT
            self.next_count = self._DEFAULT_NEXT_COUNT
            self.inner_header.auther_href = f'{page}={self.prev_count}'

        if not self.next_flag:
            self.prev_count -= 1
            self.next_count = self.prev_count + 1
            self.inner_header.auther_href = f'{page}={self.prev_count}'
        return page

    def _prev_works(self):
        page = self._get_prev_and_next_count()
        if not page:
            return
        if self.prev_count == self._DEFAULT_PREV_COUNT:
            self._get_prev_and_next_count()

        self.inner_header.auther_href = f'{page}={self.prev_count}'
        self.get_user_data()

    def _next_works(self):
        page = self._get_prev_and_next_count()
        if not page:
            return
        self.inner_header.auther_href = f'{page}={self.next_count}'
        self.get_user_data()
        self._get_prev_and_next_count()

    def get_user_data(self, jump=False):
        self._GetUserData_thread = self.inner_thread_builder.build_thread(self._crawler,
                                                                          auther_href=self.inner_header.auther_href,
                                                                          get_user_data=True)
        self._GetUserData_thread.get_user_data_signal.connect(
            functools.partial(self._get_thumbnail_url_list, jump=jump))
        self._GetUserData_thread.start()

    def connect(self):
        self._signal_btn_prev.connect(self._prev_works)
        self._signal_btn_next.connect(self._next_works)
        self._signal_btn_paste.connect(self._check_url)
        self._signal_table_auther.connect(self._paste_url)

    @property
    def inner_header(self):
        return self._header

    @inner_header.setter
    def inner_header(self, value):
        self._header: HeaderSlot = value

    @property
    def inner_sidebar(self):
        return self._sidebar

    @inner_sidebar.setter
    def inner_sidebar(self, value):
        self._sidebar: SidebarSlot = value

    @property
    def crawler(self):
        return self._crawler

    @crawler.setter
    def crawler(self, value):
        self._crawler = value

    @property
    def inner_thread_builder(self):
        return self._thread_builder

    @inner_thread_builder.setter
    def inner_thread_builder(self, value):
        self._thread_builder = value


class SettingSlot:
    _instance = None

    def __init__(self, ui: Ui_MainWindow, window):
        self.__ui = ui
        self.__window = window
        self.resource_flag = False

        self.__set_signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingSlot, cls).__new__(cls)
        return cls._instance

    def __set_signal(self):
        self._signal_combo_theme = self.__ui.combo_theme.currentIndexChanged
        self._signal_btn_cache_folder = self.__ui.btn_cache_folder.clicked
        self._signal_btn_full_folder = self.__ui.btn_full_folder.clicked
        self._signal_btn_dir_folder = self.__ui.btn_dir_folder.clicked
        self._signal_btn_save = self.__ui.btn_save.clicked
        self._signal_btn_cansel = self.__ui.btn_cancel.clicked

    def _update_resource_file(self, key, value):
        self.resource_data = cnu_new.utils.global_configuration
        self.resource_flag = True
        cnu_new.utils.modify_resource(self.resource_data, key, value)

    def _check_clear_cache(self):
        clear_cache = self.__ui.box_clearCache.isChecked()
        self._update_resource_file('clear_cache', value=clear_cache)

    def _check_exit_or_minimize(self):
        if self.__ui.radio_exit.isChecked():
            self._exit_flag = True
        elif self.__ui.radio_minimize.isChecked():
            self._exit_flag = False
        self._update_resource_file('exit_window', value=self._exit_flag)

    def _check_theme(self):
        current_theme = self.__ui.combo_theme.currentText()
        self._update_resource_file('theme', value=current_theme)

    def _choose_folder(self, cache_path=False, download_path=False, dir_path=False):
        if cache_path:
            if folder := QFileDialog.getExistingDirectory(
                None, '选择文件夹', self.crawler.CACHE_DEFAULT_PATH
            ):
                self._update_resource_file('cache_path', value=folder)
                self.__ui.lineEdit_cache.setText(folder)

        elif download_path:
            if folder := QFileDialog.getExistingDirectory(
                None, '选择文件夹', self.crawler.WORKS_DEFAULT_FULL_PATH
            ):
                self._update_resource_file('works_full_path', value=folder)
                self.__ui.lineEdit_full.setText(folder)

        elif dir_path:
            if folder := QFileDialog.getExistingDirectory(
                None, '选择文件夹', self.crawler.WORKS_DEFAULT_DIR_PATH
            ):
                self._update_resource_file('works_dir_path', value=folder)
                self.__ui.lineEdit_dir.setText(folder)

    def _save_resource_file(self):
        self._check_clear_cache()
        self._check_exit_or_minimize()
        self._check_theme()

        if self.resource_flag:
            file_path = cnu_new.utils.file_path
            with open(file_path, 'w') as f:
                yaml.safe_dump(self.resource_data, f, default_flow_style=False)

    def _config_backtrack(self):
        self.resource_flag = False

        # 清楚缓存设置
        enable_clear: bool = cnu_new.utils.get_config_attr('clear_cache')
        self.__ui.box_clearCache.setChecked(enable_clear)

        # 确认退出设置
        enable_exit: bool = cnu_new.utils.get_config_attr('exit_window')
        if enable_exit:
            self.__ui.radio_exit.setChecked(True)
        else:
            self.__ui.radio_minimize.setChecked(True)

        # 老板键设置
        boss_key: list[str] = cnu_new.utils.get_config_attr('show_window')
        self.__ui.lineEdit_hotkey.setText(' + '.join(boss_key))

        # 文件地址栏设置
        self._update_resource_file('cache_path', value='')
        self._update_resource_file('works_full_path', value='')
        self._update_resource_file('works_dir_path', value='')

        cache_path = cnu_new.utils.get_config_attr('default_cache_path')
        full_path = cnu_new.utils.get_config_attr('default_full_path')
        save_path = cnu_new.utils.get_config_attr('default_save_path')

        self.__ui.lineEdit_cache.setText(cache_path)
        self.__ui.lineEdit_full.setText(full_path)
        self.__ui.lineEdit_dir.setText(save_path)

    def _switch_theme(self):
        theme_name = self.__ui.combo_theme.currentText()
        data = cnu_new.utils.load_themes(self.__ui)
        cnu_new.utils.change_theme(self.__ui, data, theme_name)

    def connect(self):
        self._signal_combo_theme.connect(self._switch_theme)
        self._signal_btn_cache_folder.connect(functools.partial(self._choose_folder, cache_path=True))
        self._signal_btn_full_folder.connect(functools.partial(self._choose_folder, download_path=True))
        self._signal_btn_dir_folder.connect(functools.partial(self._choose_folder, dir_path=True))
        self._signal_btn_save.connect(self._save_resource_file)
        self._signal_btn_cansel.connect(self._config_backtrack)

    @property
    def crawler(self):
        return self._crawler

    @crawler.setter
    def crawler(self, value):
        self._crawler = value
