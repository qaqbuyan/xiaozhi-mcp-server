import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('获取B站主播信息')

config = load_config()

def get_bilibili_anchor_info(mcp: FastMCP):
    """查询B站主播信息"""
    @mcp.tool()
    def get_bilibili_anchor_info(uid: int) -> dict:
        """用于查询B站主播信息，当需要获取主播信息时，立即使用该工具。
        Args:
            uid (int): 目标用户mid
        Returns:
            dict: 返回包含success和result字段的字典，其中result可能包含主播的详细信息
                - success (bool): 请求是否成功
                - result (dict): 主播详细信息
                    - info (dict): 主播基本信息
                        - uname (str): 主播用户名
                        - official_verify (dict): 主播认证信息
                            - type (int): 主播认证类型，-1：无；0：个人认证；1：机构认证
                            - desc (str): 主播认证描述
                    - exp (dict): 经验等级信息
                        - master_level (dict): 主播等级信息
                    - follower_num (int): 主播粉丝数
                    - room_id (int): 直播间id（短号）
                    - medal_name (str): 粉丝勋章名
                    - glory_count (int): 主播荣誉数
                    - pendant (str): 直播间头像框url
                    - room_news (dict): 主播公告
        """
        url = "https://api.live.bilibili.com/live_user/v1/Master/info"
        params = {"uid": uid}
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询用户 {uid} 的主播信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                result = {
                    "info": {
                        "uname": data["data"]["info"]["uname"],
                        "official_verify": {
                            "type": data["data"]["info"]["official_verify"]["type"],
                            "desc": data["data"]["info"]["official_verify"]["desc"]
                        }
                    },
                    "exp": {
                        "master_level": data["data"]["exp"]["master_level"]
                    },
                    "follower_num": data["data"]["follower_num"],
                    "room_id": data["data"]["room_id"],
                    "medal_name": data["data"]["medal_name"],
                    "glory_count": data["data"]["glory_count"],
                    "pendant": data["data"]["pendant"],
                    "room_news": data["data"]["room_news"]
                }
                logger.info(f"成功获取用户 {uid} 的主播信息")
                logger.info(f"返回数据：{result}")
                return {
                    "success": True,
                    "result": result
                }
            logger.error("未获取到主播信息数据")
            return {"success": False, "result": "未获取到主播信息数据"}
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return {"success": False, "result": f"请求失败: {e}"}