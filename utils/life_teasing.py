import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('人间凑数')

def get_life_teasing(mcp: FastMCP):
    """人间凑数(生活调侃)"""
    @mcp.tool()
    def get_life_teasing() -> str:
        """用于获取我在人间凑数或者生活调侃的搞笑内容，当查询人间凑数或者感叹生活不如意时，
        比如现在生活真不容易等负面影响的，立刻使用该工具，完整的将内容输出。
        """
        url = "https://qaqbuyan.com:88/api/人间凑数/"
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info("正在获取人间凑数的内容...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 200:
                logger.info(f"成功获取：{data['message']}")
                return {
                    "success": True,
                    "result": data["message"]
                }
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": True,"result": "无法得到人间凑数的内容"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": "无法访问链接：{e}"}