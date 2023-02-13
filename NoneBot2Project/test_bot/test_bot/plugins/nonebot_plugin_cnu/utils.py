import datetime
import time

week_mapping = {
    'Monday': '周一',
    'Tuesday': '周二',
    'Wednesday': '周三',
    'Thursday': '周四',
    'Friday': '周五',
    'Saturday': '周六',
    'Sunday': '周日'
}


def title_format(title):
    """
    输出格式化后的图集标题
    :param title: 图集标题
    :return: 格式化后的图集标题
    """
    illegal_chars = ['\\', '/', '|', '.', ':', '<', '>', '?', '*', '\u200b']
    title = title.strip()
    if ' ' in title:
        title = title.replace(' ', '_')

    for char in illegal_chars:
        if char in title:
            title = title.replace(char, '')

    return title


def get_iso_weekday():
    date = datetime.datetime.now()
    return week_mapping.get(date.strftime("%A"))


def get_date(formatted_date: str):
    struct_time = time.strptime(formatted_date, '%Y-%m-%d')
    return datetime.date(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday)
