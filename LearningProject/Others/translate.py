import time
import hashlib

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/99.0.4844.51 "
                  "Safari/537.36 Edg/99.0.1150.39 ",
    "Cookie": "OUTFOX_SEARCH_USER_ID=-989463063@10.108.160.100; OUTFOX_SEARCH_USER_ID_NCOO=1670383406.049223; "
              "JSESSIONID=aaaoeB1SzHITX71OVz_9x; ___rl__test__cookies=1647098782127",
    "Referer": "https://fanyi.youdao.com/"
}
languages = {
    '0': {'from_': 'AUTO', 'to_': 'AUTO'},
    '1': {'from_': 'zh-CHS', 'to_': 'ja'},
    '2': {'from_': 'zh-CHS', 'to_': 'ko'},
    '3': {'from_': 'zh-CHS', 'to_': 'fr'},
    '4': {'from_': 'zh-CHS', 'to_': 'de'},
    '5': {'from_': 'zh-CHS', 'to_': 're'},
    '6': {'from_': 'zh-CHS', 'to_': 'es'},
    '7': {'from_': 'zh-CHS', 'to_': 'pt'},
    '8': {'from_': 'ja', 'to_': 'zh-CHS'},
    '9': {'from_': 'ko', 'to_': 'zh-CHS'},
    '10': {'from_': 'fr', 'to_': 'zh-CHS'},
    '11': {'from_': 'de', 'to_': 'zh-CHS'},
    '12': {'from_': 're', 'to_': 'zh-CHS'},
    '13': {'from_': 'es', 'to_': 'zh-CHS'},
    '14': {'from_': 'pt', 'to_': 'zh-CHS'},
}
translate_api = 'https://fanyi.youdao.com/translate_o'


def get_time() -> tuple[str, str]:
    t1 = str(time.time()).split('.')[0]
    t2 = str(time.time()).split('.')[1]
    return t1, t2


def create_lts(t1: str, t2: str) -> str:
    return t1 + t2[:3]


def create_salt(t1: str, t2: str) -> str:
    return t1 + t2[:4]


def create_sign(i_: str, salt: str) -> str:
    sign_str = f'fanyideskweb{i_}{salt}Ygy_4c=r#e#4EX^NUGUc5'
    return hashlib.md5(sign_str.encode()).hexdigest()


def select_languages():
    while True:
        print('[0]自动翻译  [1]中译日  [2]中译韩  [3]中译法  [4]中译德  [5]中译俄  [6]中译西班牙  [7]中译葡萄牙')
        print('[8]日译中  [9]韩译中  [10]法译中  [11]德译中  [12]俄译中  [13]西班牙译中  [14]葡萄牙译中')
        mode = input('请选择翻译语种: ')
        if mode in languages:
            from__ = languages[mode]['from_']
            to__ = languages[mode]['to_']
            return from__, to__

        else:
            print('语种选择错误!')


def create_data(text: str, from_: str, to_: str) -> dict:
    t1, t2 = get_time()
    salt = create_salt(t1, t2)
    sign = create_sign(text, salt)
    lts = create_lts(t1, t2)

    return {
        'i': text,
        'from': from_,
        'to': to_,
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': salt,
        'sign': sign,
        'lts': lts,
        'bv': 'cdd63870d07eb5030b9324cc7f7de35b',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTlME'
    }


def translate(url: str, text: str):
    from_, to_ = select_languages()
    data = create_data(text, from_, to_)
    res_json = requests.post(url, data=data, headers=headers).json()

    tgt = res_json['translateResult'][0][0]['tgt']

    smart_tgts = None
    if 'smartResult' in res_json:
        smart_result = res_json['smartResult']['entries'][1:]
        smart_tgts = [i.replace('\r\n', '') for i in smart_result]

    print(result(text, tgt, smart_tgts))


def result(target_text: str,
           result_text: str,
           smart_list: list[str]) -> str:
    smart_text = '无' if smart_list is None else ' '.join(smart_list)
    return f"""+——————————————————————+
 >>查询字段: {target_text}
 >>翻译结果: {result_text}
 >>相关翻译: {smart_text}
+——————————————————————+
"""


if __name__ == '__main__':
    translate_api = 'https://fanyi.youdao.com/translate_o'

    while True:
        input_text = input('请输入你要查询的文字(输入"-sys_quit"退出程序.): ')
        if input_text == '-sys_quit':
            break

        translate(translate_api, input_text)
