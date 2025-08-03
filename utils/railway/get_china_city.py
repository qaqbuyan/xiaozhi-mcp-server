import os
import json
import logging
import requests
from config.loader import load_config

config = load_config()
logger = logging.getLogger('中国铁路')

def get_china_city_data() -> dict:
    # 获取城市数据
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9053"
    logger.info("正在获取城市数据...")
    # 设置请求头，从配置文件获取User-Agent
    headers = {
        'User-Agent': config['http_headers']['user_agent']
    }
    # 发送请求，获取返回的数据
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()  # 检查请求是否成功
        data = str(res.content, encoding="utf8")
    except requests.exceptions.RequestException as e:
        error_msg = f"请求失败: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "result": error_msg
        }
    # 格式化返回的数据
    dict_data = dict()
    # 根据'|'分隔数据
    list_data = data.split('|')
    # 从下标'1'开始, 每间隔5个为字典key
    result_x = list_data[1:len(list_data):5]
    # 从下标'2'开始, 每间隔5个为字典value
    result_y = list_data[2:len(list_data):5]
    # 循环将数据写入字典
    for i in range(len(result_x)):
        dict_data[result_x[i].replace(" ", "")] = result_y[i]
    # 保存数据
    json_data = json.dumps(dict_data, indent=1, ensure_ascii=False)
    # 创建tmp目录
    cache_dir = os.path.join(os.getcwd(), 'tmp')
    os.makedirs(cache_dir, exist_ok=True)
    # 保存文件到tmp目录
    cache_file = os.path.join(cache_dir, 'city_data.json')
    # 显式指定编码为utf-8
    try:
        with open(cache_file, 'w', encoding='utf-8') as w:
            w.write(json_data)
        msg = "城市数据保存完成！"
        logger.info(msg)
        return {
            "success": True,
            "result": msg
        }
    except IOError as e:
        error_msg = f"城市数据保存失败: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "result": error_msg
        }