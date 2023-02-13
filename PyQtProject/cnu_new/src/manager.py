from .slots import HeaderSlot, SidebarSlot, ViewSlot, AutherSlot, SettingSlot
from .entity import Atlas, Works
from .thread import GetAtlasData, GetUserData, AtlasPreview, Downloader, UserPreview, HotKeyThread


class SlotsBuilder:
    _instance = None

    def __init__(self, ui, window):
        self.__ui = ui
        self.__window = window

        self.__header = None
        self.__sidebar = None
        self.__view = None
        self.__auther = None
        self.__setting = None

        self._build_slot()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SlotsBuilder, cls).__new__(cls)
        return cls._instance

    def _build_slot(self):
        if not self.__header:
            self.__header = HeaderSlot(self.__ui, self.__window)

        if not self.__sidebar:
            self.__sidebar = SidebarSlot(self.__ui, self.__window)

        if not self.__view:
            self.__view = ViewSlot(self.__ui, self.__window)

        if not self.__auther:
            self.__auther = AutherSlot(self.__ui, self.__window)

        if not self.__setting:
            self.__setting = SettingSlot(self.__ui, self.__window)

    @property
    def header(self) -> HeaderSlot:
        return self.__header

    @property
    def sidebar(self) -> SidebarSlot:
        return self.__sidebar

    @property
    def view(self) -> ViewSlot:
        return self.__view

    @property
    def auther(self) -> AutherSlot:
        return self.__auther

    @property
    def setting(self) -> SettingSlot:
        return self.__setting


class ThreadsBuilder:

    @staticmethod
    def build_thread(crawler,
                     ui=None,
                     window=None,
                     atlas: Atlas = None,
                     atlas_url=None,
                     image_url=None,
                     download_indexes=None,
                     cus_path=None,
                     auther_href=None,
                     thumbnail_url_list=None,
                     get_data: bool = False,
                     atlas_preview: bool = False,
                     downloader: bool = False,
                     get_user_data: bool = False,
                     user_preview: bool = False,
                     hot_key: bool = False):
        if get_data:
            if not atlas_url:
                raise RuntimeError(f'ThreadFactoryError: The params got NoneType, [atlas_url={atlas_url}]')
            return GetAtlasData(crawler, atlas_url)

        if atlas_preview:
            if not (ui and image_url and atlas_url):
                raise RuntimeError(
                    f'ThreadFactoryError: The params got NoneType, [ui={ui}, image_url={image_url}, work_url={atlas_url}]')
            return AtlasPreview(crawler, ui, image_url, atlas_url)

        if downloader:
            if not (atlas and download_indexes):
                raise RuntimeError(
                    f'ThreadFactoryError: The params got NoneType, [atlas={atlas}, download_indexes={download_indexes}]')
            return Downloader(crawler, atlas, download_indexes, cus_path)

        if get_user_data:
            if not auther_href:
                raise RuntimeError(f'ThreadFactoryError: The params got NoneType, [auther_href={auther_href}]')
            return GetUserData(crawler, auther_href)

        if user_preview:
            if not thumbnail_url_list:
                raise RuntimeError(f'ThreadFactoryError: The params got NoneType, [thumbnail_url_list={thumbnail_url_list}]')
            return UserPreview(crawler, thumbnail_url_list)

        if hot_key:
            if not window:
                raise RuntimeError(f'ThreadFactoryError: The params got NoneType, [window={window}]')
            return HotKeyThread(window)
