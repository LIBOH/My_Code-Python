import os
from .utils import data_path, get_data


def get_pred_start(username):
    return get_data(username)['pred_start']


def get_pred_end(username):
    return get_data(username)['pred_end']


def get_next_start(username):
    return get_data(username)['next_start']


def get_cycle(username):
    return get_data(username)['cycle']


def get_default_advance(username):
    return get_data(username)['advance_prompt']


def get_pred_advance(username):
    return get_data(username)['pred_duration']


def delete_data(username):
    os.remove(f'{data_path}/{username}.json')


def total_info(username):
    return [
        f'<{username}>下一次月经预计开始于: {get_next_start(username)}\n',
        f'<{username}>上次月经开始于: {get_pred_start(username)}\n',
        f'<{username}>上次月经结束于: {get_pred_end(username)} -- Tips: 如果不正确请使用命令`update <用户名> 上次结束 <yyyy-mm-dd>`修改!\n',
        f'<{username}>上次月经持续天数为: {get_pred_advance(username)}天\n',
        f'<{username}>经期提前提醒天数为: {get_default_advance(username)}天\n',
        f'<{username}>经期周期为: {get_cycle(username)}天\n',
    ]