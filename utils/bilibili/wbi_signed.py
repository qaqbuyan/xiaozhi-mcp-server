import time
import json
import logging
import requests
import urllib.parse
from hashlib import md5
from functools import reduce
from config.loader import load_config

logger = logging.getLogger('Wbi签名')

def get_wbi_signed():
    mixinKeyEncTab = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
        33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
        61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
        36, 20, 34, 44, 52
    ]
    headers = {
        'User-Agent': load_config()['http_headers']['user_agent'],
        'Referer': 'https://www.bilibili.com/'
    }
    logger.info("开始查询Wbi签名...")
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url = json_content['data']['wbi_img']['img_url']
    sub_url = json_content['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    mixin_key = reduce(lambda s, i: s + (img_key + sub_key)[i], mixinKeyEncTab, '')[:32]
    params = {
        'foo': '114',
        'bar': '514',
        'baz': 1919810
    }
    curr_time = round(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {
        k : ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v 
        in params.items()
    }
    query = urllib.parse.urlencode(params)
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    result = {
        'w_rid': params['w_rid'],
        'wts': params['wts']
    }
    logger.info(f"返回数据：{result}")
    return result