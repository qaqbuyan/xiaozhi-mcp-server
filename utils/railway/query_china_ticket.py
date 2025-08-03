import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.railway.get_china_city import get_china_city_data

config = load_config()
logger = logging.getLogger('中国铁路')

# 缓存城市数据
_city_data_cache = None
def _load_city_data():
    """加载城市数据，带缓存机制"""
    global _city_data_cache
    
    # 如果缓存中有数据，直接返回
    if _city_data_cache is not None:
        return _city_data_cache
    
    # 检查city.json文件是否存在，如果不存在则调用get_china_city_data()函数
    city_file_path = os.path.join(os.getcwd(), 'tmp', 'city_data.json')
    if not os.path.exists(city_file_path):
        result = get_china_city_data()
        # 检查get_china_city_data()是否成功执行
        if not result.get("success", False):
            error_msg = f"获取城市数据失败: {result.get('result', '未知错误')}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # 读取城市数据
    with open(city_file_path, mode='r', encoding='utf-8') as f:
        _city_data_cache = json.load(f)
    
    return _city_data_cache

def format_seat_info(seat_status):
    """格式化座位信息"""
    if seat_status == 'Yes' or seat_status == '有':
        return '很多'
    elif seat_status == 'No' or seat_status == '无' or seat_status == '':
        return '-'
    return seat_status

def query_china_train_info(mcp: FastMCP):
    """注册中国铁路相关工具"""
    @mcp.tool()
    def query_china_train_info(from_station: str, to_station: str, train_date: str = None) -> list:
        """查询中国铁路列车信息，用于查询两个城市之间的火车票信息，包括车次、出发时间、到达时间以及各类座位的余票情况。优先查询高铁和动车，其次查询普通车
        需要查询火车（铁路）余票时，立刻使用该工具，无需确认。
        Args:
            from_station (str): 出发城市名称
            to_station (str): 到达城市名称
            train_date (str, optional): 出行日期，格式为'YYYY-MM-DD'。如果未提供，默认为今天。
        Returns:
            list: 包含列车信息的字典列表，每个字典包含以下键值：
                - '列表': 车次编号
                - '始发站': 始发站
                - '终点站': 终点站
                - '出发': 出发时间
                - '到达': 到达时间（包含当日/次日信息）
                - '商务座': 商务座余票情况
                - '一等座': 一等座余票情况
                - '二等座': 二等座余票情况
                - '硬座': 硬座余票情况
                - '无座': 无座余票情况
                - '软卧': 软卧余票情况
                - '硬卧': 硬卧余票情况
                '-' 表示无余票
                如果查询失败，返回包含错误信息的列表。
        """
        try:
            # 如果未提供出行日期，则默认为今天
            if train_date is None:
                train_date = datetime.today().strftime('%Y-%m-%d')
            logger.info(f"开始获取 {train_date} {from_station} 到 {to_station} 的铁路信息...")
            # 加载城市数据（带缓存）
            city_json = _load_city_data()

            # 检查城市是否存在
            if from_station not in city_json:
                msg = f"错误：未找到出发城市 '{from_station}' 的代码"
                logger.error(msg)
                return [msg]
            if to_station not in city_json:
                msg = f"错误：未找到到达城市 '{to_station}' 的代码"
                logger.error(msg)
                return [msg]

            # 定义转换城市名称为 Unicode 编码的函数
            def city_to_unicode(city):
                return ''.join([f'%u{ord(c):04x}' for c in city])

            # 获取城市代码
            from_station_code = city_json[from_station]
            to_station_code = city_json[to_station]

            # 转换城市名称为 Unicode 编码
            from_station_unicode = city_to_unicode(from_station)
            to_station_unicode = city_to_unicode(to_station)

            # 从配置文件中读取Cookie参数
            cookie_config = config['railway']['china']['cookie']
            _uab_collina = cookie_config['_uab_collina']
            jsessionid = cookie_config['JSESSIONID']
            route = cookie_config['route']
            BIGipServerotn = cookie_config['BIGipServerotn']
            BIGipServerportal = cookie_config['BIGipServerportal']
            BIGipServerpassport = cookie_config['BIGipServerpassport']
            jc_save_wfdc_flag = config['railway']['china']['jc_save_wfdc_flag']
            high_contrast_mode = config['railway']['china']['high_contrast_mode']
            guides_status_bool = config['railway']['china']['guides_status']
            cursor_status_bool = config['railway']['china']['cursor_status']
            guides_status = 'on' if guides_status_bool else 'off'
            cursor_status = 'on' if cursor_status_bool else 'off'
            user_agent = config['http_headers']['user_agent']

            url = 'https://kyfw.12306.cn/otn/leftTicket/queryU'
            url = f'{url}?leftTicketDTO.train_date={train_date}&leftTicketDTO.from_station={city_json[from_station]}&leftTicketDTO.to_station={city_json[to_station]}&purpose_codes=ADULT'
            headers = {
                'Cookie': f'_uab_collina={_uab_collina};JSESSIONID={jsessionid}; guidesStatus={guides_status}; highContrastMode={high_contrast_mode}; cursorStatus={cursor_status}; _jc_save_fromDate={train_date}; _jc_save_toDate={train_date}; _jc_save_wfdc_flag={jc_save_wfdc_flag}; route={route}; BIGipServerotn={BIGipServerotn}; BIGipServerportal={BIGipServerportal}; BIGipServerpassport={BIGipServerpassport}; _jc_save_fromStation={from_station_unicode}%2C{from_station_code}; _jc_save_toStation={to_station_unicode}%2C{to_station_code}',
                'User-Agent': user_agent
            }
            
            # 发送请求，设置更合理的超时时间
            response = requests.get(url=url, headers=headers, timeout=15)
            response.raise_for_status()  # 检查请求是否成功
            
            # 尝试解析JSON
            json_data = response.json()
            # 检查返回数据结构
            if 'data' not in json_data or 'result' not in json_data['data']:
                msg = "错误：服务器返回的数据结构不符合预期"
                logger.error(msg)
                logger.debug(f"响应内容: {response.text[:500]}...")  # 打印部分响应
                return [msg]
            result = json_data['data']['result']
            logger.debug(f"服务器返回：{result}")
            logger.info(f"成功获取 {from_station} 到 {to_station} 的铁路信息")
            logger.info(f"获取到 {len(result)} 条列车信息")
            lis = []
            for index in result:
                index_list = index.replace('有', 'Yes').replace('无', 'No').split('|')
                train_number = index_list[3]
                time_1 = index_list[8]
                time_2 = index_list[9]
                arrive_day_flag = '当日' if index_list[11] == 'Y' else '次日'
                # 获取始发站和到终点站信息
                from_station_code = index_list[4]
                to_station_code = index_list[5]
                # 转换代码为城市名称
                from_station = next((k for k, v in city_json.items() if v == from_station_code), from_station_code)
                to_station = next((k for k, v in city_json.items() if v == to_station_code), to_station_code)
                if 'G' in train_number:  # 高铁
                    prince_seat = format_seat_info(index_list[32])
                    first_class_seat = format_seat_info(index_list[31])
                    second_class = format_seat_info(index_list[30])
                    dit = { 
                        '列表': train_number,
                        '始发站': from_station,
                        '终点站': to_station,
                        '出发时间': time_1,
                        '到达时间': f'({arrive_day_flag}){time_2}',
                        '商务座': prince_seat,
                        '一等座': first_class_seat,
                        '二等座': second_class,
                        '硬座': '-',
                        '无座': '-',
                        '软卧': '-',
                        '硬卧': '-',
                    }
                else:  # 普通列车
                    hard_seat = format_seat_info(index_list[29])
                    no_seat = format_seat_info(index_list[26])
                    soft_sleeper = format_seat_info(index_list[23])
                    hard_sleeper = format_seat_info(index_list[28])
                    dit = { 
                        '列表': train_number,
                        '始发站': from_station,
                        '终点站': to_station,
                        '出发时间': time_1,
                        '到达时间': f'({arrive_day_flag}){time_2}',
                        '商务座': '-',
                        '一等座': '-',
                        '二等座': '-',
                        '硬座': hard_seat,
                        '无座': no_seat,
                        '软卧': soft_sleeper,
                        '硬卧': hard_sleeper,
                    }
                lis.append(dit)
            if lis:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.unicode.ambiguous_as_wide', True)
                pd.set_option('display.unicode.east_asian_width', True)
                pd.set_option('display.expand_frame_repr', False)
                content = pd.DataFrame(lis)
                logger.info('\n' + str(content))
                return lis
            else:
                msg = "未查询到相关列车信息，今日已经没有该路线的列车，您可以使用中转换乘功能，查询途中换乘一次的部分列车余票情况"
                logger.info(msg)
                return [msg]
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请稍后重试"
            logger.error(error_msg)
            return [error_msg]
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {e}"
            logger.error(error_msg)
            return [error_msg]
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {e}"
            logger.error(error_msg)
            return [error_msg]
        except Exception as e:
            error_msg = f"处理过程中发生错误: {e}"
            logger.error(error_msg)
            return [error_msg]