import requests
import logging
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('获取B站直播间基本信息')
config = load_config()

def get_room_base_info(mcp: FastMCP):
    """获取B站直播间基本信息的工具函数"""
    @mcp.tool()
    def get_room_base_info(room_short_ids):
        """
        获取B站直播间基本信息
        Args:
            room_short_ids (list): 直播间短ID列表
        Returns:
            dict: 返回包含success和result字段的字典，其中result可能包含所需直播间信息
                - success (bool): 请求是否成功
                - result (dict): 各直播间信息，键为直播间ID，值为该直播间的详细信息
                    - online (int): 直播间在线人数
                    - attention (int): 直播间关注数
                    - tags (str): 直播间标签
                    - description (str): 直播间描述
                    - live_time (str): 直播开始时间
                    - uname (str): 主播用户名
                    - area_name (str): 子分区名称
                    - parent_area_name (str): 主分区名称
                    - title (str): 直播间标题
                    - live_url (str): 直播间链接
        """
        if not isinstance(room_short_ids, list):
            logger.error("room_short_ids 必须是一个列表")
            return {"success": False, "result": "room_short_ids 必须是一个列表"}
        url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomBaseInfo"
        params = {
            "req_biz": "web_room_componet",
            "room_ids": ",".join(map(str, room_short_ids))
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询直播间短ID为 {room_short_ids} 的基本信息...")
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('code') != 0:
                logger.error("API请求失败")
                return {"success": False, "result": f"API请求失败: {response_data.get('message', '未知错误')}"}
            result = {}
            if 'data' in response_data and 'by_room_ids' in response_data['data']:
                for room_id, room_info in response_data['data']['by_room_ids'].items():
                    result[room_id] = {
                        "online": room_info.get('online', 0),
                        "attention": room_info.get('attention', 0),
                        "tags": room_info.get('tags', ''),
                        "description": room_info.get('description', ''),
                        "live_time": room_info.get('live_time', ''),
                        "uname": room_info.get('uname', ''),
                        "area_name": room_info.get('area_name', ''),
                        "parent_area_name": room_info.get('parent_area_name', ''),
                        "title": room_info.get('title', ''),
                        "live_url": room_info.get('live_url', '')
                    }
            logger.info(f"成功获取直播间短ID为 {room_short_ids} 的基本信息")
            return {"success": True, "result": result}
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return {"success": False, "result": f"请求异常: {str(e)}"}
        except ValueError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return {"success": False, "result": f"JSON解析失败: {str(e)}"}
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {"success": False, "result": f"未知错误: {str(e)}"}