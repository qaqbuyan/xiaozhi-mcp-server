import logging
import requests
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('获取B站历史直播')

config = load_config()

def get_bilibili_history_live(mcp: FastMCP):
    """查询B站历史直播"""
    @mcp.tool()
    def get_bilibili_history_live(view_at_timestamp: int = int(datetime.now().timestamp())) -> dict:
        """用于查询B站历史直播，调用该工具即可获取历史直播信息。
        Args:
            view_at_timestamp (int): 查询直播的时间戳，默认为当前时间戳，即查询今天的直播。
        Returns:
            dict: 返回包含success和result字段的字典，其中result中的original_result列表里每个元素为包含以下信息的字典：
                - "oid": 直播房间或视频的唯一标识符
                - "author_name": 直播作者的名称
                - "author_mid": 直播作者的用户 ID
                - "tag_name": 直播的标签名称
                - "badge": 直播的徽章信息，如是否开播等状态提示
                - "view_at": 观看直播的时间戳
        """
        if 'bilibili_api' not in config or 'auth' not in config['bilibili_api'] or 'cookie' not in config['bilibili_api']['auth']:
            logger.error("配置文件中没有找到B站cookie")
            return {"success": False, "result": "配置文件中没有找到B站cookie"}
        url = "https://api.bilibili.com/x/web-interface/history/cursor"
        params = {
            "max": 0,  # 历史记录的最大时间戳，0 表示从最新记录开始查询
            "view_at": view_at_timestamp,  # 查询直播的时间戳，默认为当前时间戳，即查询今天的直播
            "business": "",  # 业务类型，空字符串表示查询所有业务类型的历史记录
            "ps": config['bilibili_api']['history']['ps'],  # 获取每页返回的记录数量
            "type": "live",  # 查询的历史记录类型，这里指定为直播类型
            "web_location": str(config['bilibili_api']['recommended']['web_location'])  # 网页位置标识符，用于标识查询的来源位置
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent'],
            "Cookie": config['bilibili_api']['auth']['cookie']
        }
        try:
            logger.info("开始查询B站历史直播...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data") and data["data"].get("list"):
                result = []
                for item in data["data"]["list"]:
                    live_info = {
                        "oid": item["history"]["oid"],  # 直播房间或视频的唯一标识符
                        "author_name": item["author_name"],  # 直播作者的名称
                        "author_mid": item["author_mid"],  # 直播作者的用户 ID
                        "tag_name": item["tag_name"],  # 直播的标签名称
                        "badge": item["badge"],  # 直播的徽章信息，如是否开播等状态提示
                        "view_at": item["view_at"]  # 观看直播的时间戳
                    }
                    result.append(live_info)
                loen_result = len(result)
                logger.info(f"成功获取B站历史直播，共获取到 {loen_result} 条直播")
                # 判断是否查询今天以外的数据
                today = datetime.now().date()
                today_timestamp = int(datetime.combine(today, datetime.min.time()).timestamp())
                if view_at_timestamp < today_timestamp:
                    result = result[-5:]  # 取后 5 条数据
                else:
                    result = result[:5]  # 取前 5 条数据
                result = {
                    "success": True,
                    "result": {
                        "original_result": result,
                        "result_length": f"一共看了 {'超过 ' if loen_result > config['bilibili_api']['history']['ps'] else ''}{loen_result} 条直播"
                    }
                }
                logger.info(f"返回数据：{result}")
                return result
            else:
                logger.error("未获取到历史直播数据")
                return {"success": False, "result": "未获取到历史直播数据"}
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return {"success": False, "result": f"请求失败: {e}"}