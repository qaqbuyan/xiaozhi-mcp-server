import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('QQ查询')

def query_qq_info(mcp: FastMCP):
    """QQ信息查询"""
    @mcp.tool()
    def query_qq_info(qq_number: int) -> dict:
        """用于查询QQ用户信息，当查询QQ用户信息，查询QQ或者查询QQ用户时，立即使用该工具。
        Args:
            qq_number (int): QQ号码，必须填写
        Returns:
            dict: 返回QQ用户信息
        """
        url = f"https://qaqbuyan.com:88/api/qq信息/?qq={qq_number}"
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询QQ {qq_number} 信息...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 200:
                message = data["message"]
                result = {
                    "success": True,
                    "result": {
                        "返回码": data["code"],
                        "返回码说明": "成功",
                        "昵称": message["name"],
                        "等级": message["level"],
                        "签名": message["sign"] if message["sign"] else "无",
                        "qid": message["qid"] if message["qid"] else "无",
                        "性别": message["sex"],
                        "年龄": message["age"],
                        "登入天数": message["login_days"],
                        "VIP等级": message["vip_level"] if message["vip_level"] else "无"
                    }
                }
                logger.info(f"成功获取信息: {result}") 
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取QQ信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}