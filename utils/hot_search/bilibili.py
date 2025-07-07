import logging
import requests
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.bilibili.wbi_signed import get_wbi_signed

logger = logging.getLogger('B站热搜')

def get_bilibili_hot_search(mcp: FastMCP):
    """热搜查询"""
    @mcp.tool()
    def get_bilibili_hot_search(limit: int = 10) -> dict:
        """用于查询B站热搜信息
            该工具的主要功能是获取B站的热搜信息，包括关键字和热度等。
            如果需要获取更多的热搜信息，需要询问用户要不要完整的热搜信息。
        Args:
            limit (int): 返回结果数量，默认为10，最大不超过30
        Returns:
            dict: 返回热搜信息
                "keyword": 热搜关键词
                "heat_score": 热搜热度值
        """
        config = load_config()
        signed = get_wbi_signed()
        url = "https://api.bilibili.com/x/web-interface/wbi/search/square"
        params = {
            "limit": limit,
            "platform": "web",
            "web_location": str(config['bilibili_api']['web_location']),
            "w_rid": signed['w_rid'],
            "wts": signed['wts']
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询B站热搜信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                result = []
                for item in data["data"]["trending"]["list"]:
                    result.append({
                        "keyword": item["keyword"],
                        "heat_score": item["heat_score"]
                    })
                logger.info(f"成功获取B站热搜信息: {len(result)}条")
                logger.info(f"返回数据：{result}")
                return {"success": True, "list": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取热搜信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}