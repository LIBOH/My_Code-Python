import json

import cnu_new


class Atlas:
    # Atlas的实例对象
    _instance = None

    def __init__(self, data: str):
        """
        :param data='{
                'statu_code': self._OK,
                'content': {
                    'images_url': rex_json,
                    'works_title': works_title,
                    'auther': auther,
                    'auther_href': f'{auther_href}?page=1'
                },
            }'
        """
        self._content = json.loads(data)
        # list[图片下载地址]
        self._download_domain = cnu_new.utils.get_config_attr('download_domain')
        self._images_url = self.__get_imagesUrl_from_imgItem()

        self.__iter_count = 0

    def __len__(self):
        return len(self._images_url)

    def __repr__(self):
        return f'Atlas: The atlas "{self.atlas_title}" has {self.__len__()} image URLs'

    def __str__(self):
        return f"""
Atlas: {{
    'statu_code': {self._content['statu_code']},
    'content': {{
        'images_url': {self._images_url},
        'works_title': {self.atlas_title},
        'auther': {self.auther},
        'auther_href': f'{self.auther_href}?page=1'
    }}
}}"""

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __iter__(self):
        return self

    def __next__(self):
        if self.__iter_count >= len(self._images_url):
            self.current_count = 0
            raise StopIteration
        item = self._images_url[self.__iter_count]
        self.__iter_count += 1
        return item

    def __get_imagesUrl_from_imgItem(self):
        self._content['content']['images_url'] = [
            f"{self._download_domain}{data['img']}" for data in self._content['content']['images_url']
        ]
        return self._content['content']['images_url']

    @property
    def download_domain(self):
        return self._download_domain

    @download_domain.setter
    def download_domain(self, value):
        self._download_domain = value

    @property
    def statu_code(self):
        return self._content['statu_code']

    @property
    def atlas_title(self):
        return self._content['content']['atlas_title']

    @property
    def auther(self):
        return self._content['content']['auther']

    @property
    def auther_href(self):
        return self._content['content']['auther_href']

    @property
    def release_date(self):
        return self._content['content']['release_date']

    @property
    def recommend_count(self):
        return self._content['content']['recommend_count']

    @property
    def read_count(self):
        return self._content['content']['read_count']

    @property
    def images_url(self):
        return self._images_url


class Works:
    # Works的实例对象
    _instance = None

    def __init__(self, data: str):
        """
        :param data: '[{
            "autherName": "\u732b\u4e0e\u75c5\u718a",
            "content": {
                "works_url": "http://www.cnu.cc/works/585837",
                "thumbnail_url": "http://imgoss.cnu.cc/2207/21/796c85c42a7c334fb21c5a9c1e78727e.jpg",
                "release_time": "2022-07-21",
                "works_title": "\u770b\u4e00\u773c\u6c89\u9ed8\u7684\u4f60"
            }
        }, {...}, ...]'
        """
        self._content: list = json.loads(data)
        self._user_dict = None

        self.__iter_count = 0

    def __getitem__(self, item):
        return self._content[item]

    def __repr__(self):
        return f"Works: This page of user has {self.__len__()} atlas"

    def __str__(self):
        return "Works{" + \
               f"content={self._content}, " + \
               f"autherName='{self.auther_name}'" + \
               "}"

    def __len__(self):
        return len(self._content)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __iter__(self):
        return self

    def __next__(self):
        if self.__iter_count >= self.__len__():
            self.__iter_count = 0
            raise StopIteration
        item = self._content[self.__iter_count]
        self.__iter_count += 1
        return item

    def __eq__(self, other):
        return (
            self._content == getattr(other, 'content')
            if hasattr(other, 'content') else False
        )

    def is_empty(self):
        return self._content == []

    def register_user_dict(self, index):
        try:
            self._user_dict = self._content[index]
            return True
        except IndexError:
            return False

    @property
    def atlas_url(self):
        if not self._user_dict:
            raise RuntimeError('WorksError: method["register_user_dict"] must be called first!')
        return self._user_dict['content']['atlas_url']

    @property
    def atlas_title(self):
        if not self._user_dict:
            raise RuntimeError('WorksError: method["register_user_dict"] must be called first!')
        return self._user_dict['content']['atlas_title']

    @property
    def thumbnail_url(self):
        if not self._user_dict:
            raise RuntimeError('WorksError: method["register_user_dict"] must be called first!')
        return self._user_dict['content']['thumbnail_url']

    @property
    def content(self):
        return self._content

    @property
    def auther_name(self):
        return self._content[0]['autherName'] if self._content else None
