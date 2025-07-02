import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('毒鸡汤')

def get_poisonous_chicken_soup(mcp: FastMCP):
    """毒鸡汤"""
    @mcp.tool()
    def get_poisonous_chicken_soup() -> str:
        """用于获取毒鸡汤内容，完整的将内容输出。"""
        url = "https://qaqbuyan.com:88/api/毒鸡汤/?json=true"
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info("开始获取毒鸡汤内容...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 200:
                logger.info(f"成功获取：{data['message']['chicken_soup']}")
                return {
                    "success": True,
                    "result": data["message"]["chicken_soup"]
                }
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": True,"result": "无法得到毒鸡汤的内容"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": "无法访问链接：{e}"}