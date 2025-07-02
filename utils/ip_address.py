import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('IP查询')

def query_ip_address(mcp: FastMCP):
    """IP查询"""
    @mcp.tool()
    def query_ip_address(ip_address: str) -> dict:
        """用于查询IP地址归属地信息，当需要查询IP地址信息或者ip位置时，立即使用该工具。
        Args:
            ip_address (str): IP地址或域名，必须填写, 例如：127.0.0.1 或 www.baidu.com
        Returns:
            dict: 返回IP地址归属地信息
        """
        url = f"https://qaqbuyan.com:88/api/ip/?ip={ip_address}"
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询IP {ip_address} 信息...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 200:
                result = {
                    "success": True,
                    "result": {
                        "返回码": data["code"],
                        "返回码说明": "成功",
                        "归属地": data["message"]
                    }
                }
                logger.info(f"成功获取IP {ip_address} 信息: {result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取IP信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}