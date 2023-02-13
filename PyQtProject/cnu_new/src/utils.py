import contextlib
import os
import re
from copy import deepcopy

import yaml


default_data = """boss_key: true
cache_path: ''
clear_cache: true
default_cache_path: crawl_images/cache
default_full_path: crawl_images/full
default_save_path: crawl_images/
download_domain: http://imgoss.cnu.cc/
exit_window: true
full_path: ''
save_path: ''
show_window:
  - control
  - shift
  - w
theme: Default
version: 3.4.4
"""


class Utils:
    __MAX_ACTIVE_SCOPE_NUM = 1
    __DOT = '.'
    __COMMA = ','
    __HYPHEN = '-'
    __UNDERSCORE = '_'
    __CONFIG_PATH = './resources/config'
    __THEME_PATH = './resources/themes'

    __suffix_pattern = r'.*?.yaml|.*?.yml'
    __filename_pattern = r'application.yaml|application.yml'
    __file_path = None
    __valid_resources = []  # 应用资源
    __effective_resources = []  # 有效资源

    def __init__(self):
        self.__origin_config = None
        self.global_configuration = None
        if not os.path.exists(self.__CONFIG_PATH):
            os.makedirs(self.__CONFIG_PATH)
        if not os.path.exists(self.__THEME_PATH):
            os.makedirs(self.__THEME_PATH)
        self.resource()

    def __get_file_path(self, filename=None):
        if filename:
            return f'{self.__CONFIG_PATH}/{filename}'

        return f'{self.__CONFIG_PATH}/{self.__valid_resources[0]}'

    def __load_yaml_resource(self, file=None):
        if file:
            file_path = self.__get_file_path(filename=file)
        else:
            file_path = self.__get_file_path()
        self.__file_path = file_path

        with open(file_path, 'r') as f:
            resource_data = yaml.load(f, Loader=yaml.FullLoader)

            with contextlib.suppress(KeyError):
                scope = resource_data['application_resource']['profile']['active']
                scope_list = scope.split(self.__COMMA)
                length = len(scope_list)

                if length != self.__MAX_ACTIVE_SCOPE_NUM:
                    raise RuntimeError(
                        f'ConfigValueError: There can only be one value in the active field, but got {length}, {scope_list}')

            if scope:
                for effective_file in self.__effective_resources:
                    # 使用 _ 分割
                    if scope == effective_file.split(self.__DOT)[0].rsplit(self.__UNDERSCORE, 1)[-1]:
                        return self.__load_yaml_resource(file=f'{effective_file}')

                    # 使用 - 分割
                    elif scope == effective_file.split(self.__DOT)[0].rsplit(self.__HYPHEN, 1)[-1]:
                        return self.__load_yaml_resource(file=f'{effective_file}')

            return resource_data

    def resource(self):
        self.__valid_resources.clear()

        files: list[str] = os.listdir(self.__CONFIG_PATH)
        if not files:
            print('未检测到配置文件，正在创建默认配置...')
            self.write_resource_file()

        files: list[str] = os.listdir(self.__CONFIG_PATH)
        for file in files:
            if rex := re.match(self.__suffix_pattern, file):
                suffix = rex.group()
                self.__effective_resources.append(suffix)

        if self.__effective_resources:
            for file in self.__effective_resources:
                if rex := re.match(self.__filename_pattern, file):
                    filename = rex.group()
                    if filename not in self.__valid_resources:
                        self.__valid_resources.append(filename)

        length = len(self.__valid_resources)
        if length != self.__MAX_ACTIVE_SCOPE_NUM:
            raise RuntimeError('ConfigFileConflict: Have at most one application.* file, ' +
                               f'but got {length}, {self.__valid_resources}')

        self.__origin_config = self.__load_yaml_resource()
        self.global_configuration = deepcopy(self.__origin_config)
        return self.global_configuration

    def get_config_attr(self, field: str):
        return self.global_configuration[field]

    def write_resource_file(self):
        with open(f'{self.__CONFIG_PATH}/application.yaml', 'w', encoding='utf-8') as f:
            f.write(default_data)
        print('配置文件创建完成！')

    def load_themes(self, ui, add_flag=False):
        data = {}
        themes = os.listdir(self.__THEME_PATH)
        for i, v in enumerate(themes):
            d = {v: i}
            data |= d
        if add_flag:
            ui.combo_theme.addItems(themes)

        return data

    def change_theme(self, ui, data, name='Default'):
        """切换、加载主题"""
        try:
            with open(f'{self.__THEME_PATH}/{name}/main.qss', encoding='utf-8') as f:
                main_style = f.read()
                ui.centralwidget.setStyleSheet(main_style)
            ui.combo_theme.setCurrentIndex(data[name])

        except FileNotFoundError:
            print(">>>: 切换主题失败, 文件不存在或文件名异常, 文件必须命名为main.qss")
            print(">>>: 已使用默认主题")
            theme_data = self.load_themes(ui)
            self.change_theme(ui, theme_data)
            ui.label_theme_status.setText('切换主题失败, 已使用默认主题')

    @staticmethod
    def modify_resource(dic: dict, key, value):
        try:
            dic[key] = value
        except KeyError:
            print(f'全局配置中没有字段: [{key}]')

    @property
    def file_path(self):
        return self.__file_path

    @property
    def origin_config(self):
        return self.__origin_config
