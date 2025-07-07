import logging
import requests
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('百度热搜')

def get_baidu_hot_search(mcp: FastMCP):
    """百度热搜查询"""
    @mcp.tool()
    def get_baidu_hot_search(limit: int = 10) -> dict:
        """用于查询百度实时热搜信息
            该工具的主要功能是获取百度的实时热搜信息，包括热搜关键词。
            如果需要获取更多的热搜信息，需要询问用户要不要完整的热搜信息。
        Args:
            limit (int): 返回结果数量，默认为10，最大不超过50
        Returns:
            dict: 返回热搜信息
        """
        config = load_config()
        url = "https://top.baidu.com/api/board?platform=wise&tab=realtime&tag=%7B%7D"
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询百度热搜信息...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("success", False):
                result = []
                # 从 content 中提取 query 信息
                content = data.get("data", {}).get("cards", [{}])[0].get("content", [])
                for item in content[:limit]:
                    if "query" in item:
                        result.append(item["query"])
                logger.info(f"成功获取百度热搜信息: {len(result)}条")
                logger.info(f"返回数据：{result}")
                return {"success": True, "list": result}
            else:
                logger.error(f"获取失败，数据中 success 字段为 false")
                return {"success": False, "result": "获取热搜信息失败"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}