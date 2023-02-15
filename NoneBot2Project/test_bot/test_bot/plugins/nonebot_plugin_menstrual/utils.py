import os
import json
from copy import deepcopy
from datetime import date, datetime, timedelta

from nonebot.log import logger


data_path = './data/nonebot_plugin_menstrual'
if not os.path.exists(data_path):
    os.makedirs(data_path)

data_template = {
    'cycle': '',
    'advance_prompt': '',
    'duration': '',
    'pred_duration': '',
    'pred_start': '',
    'pred_end': '',
    'next_start': ''
}

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def init_data(name: str,
              pred_start: str,
              cycle: int,
              duration: int,
              advance_prompt: int) -> None:
    """初次使用时需初始化数据

    Args:
        name (str): 用户名/数据文件名
        pred_start (str): 最近一次经期开始的日期 -> 例: 2023-01-24
        cycle (int): 月经周期 单位：天
        duration (int): 持续时间 单位：天
        advance_prompt (int): 提前几天提醒月经即将到来 单位：天
    """
    data = deepcopy(data_template)
    data['cycle'] = cycle
    data['advance_prompt'] = advance_prompt
    data['duration'] = duration
    data['pred_start'] = pred_start

    with open(f'{data_path}/{name}.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    forecast_date(name)
    set_pred_end(name)
    set_pred_duration(name)


def get_data(user_name: str) -> dict|None:
    try:
        with open(f'{data_path}/{user_name}.json', 'r') as f:
            return json.loads(f.read())

    except FileNotFoundError:
        logger.warning(f'用户<{user_name}>尚未初始化!')
        return None


def forecast_date(user_name: str) -> None:
    user_data = get_data(user_name)
    if user_data is None:
        return

    pred_start = date(*map(int, user_data['pred_start'].split('-')))
    next_date = pred_start + timedelta(int(user_data['cycle']))

    modify_data(user_name, 'next_start', next_date)


def set_pred_duration(user_name: str) -> None:
    user_data = get_data(user_name)
    if user_data is None:
        return
    
    pred_start = date(*map(int, user_data['pred_start'].split('-')))
    pred_end = date(*map(int, user_data['pred_end'].split('-')))
    pred_duration = pred_end - timedelta(pred_start.day)

    modify_data(user_name, 'pred_duration', str(pred_duration.day))



def set_pred_end(user_name: str, value: str = None) -> None:
    user_data = get_data(user_name)
    if user_data is None:
        return
    
    if value:
        modify_data(user_name, 'pred_end', value)

    start = date(*map(int, user_data['pred_start'].split('-')))
    end = start + timedelta(int(user_data['duration']) - 1)  # 从开始那天算起所以-1
    modify_data(user_name, 'pred_end', end)


def modify_data(user_name, key, value) -> None:
    data = get_data(user_name)
    data[key] = value
    with open(f'{data_path}/{user_name}.json','w') as f2:
        json.dump(data,f2, ensure_ascii=False, indent=4, cls=ComplexEncoder)
