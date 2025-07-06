import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('今日油价')

def get_oil_price(mcp: FastMCP):
    """今日油价"""
    @mcp.tool()
    def get_oil_price(province: str) -> dict:
        """根据省份获取今日油价信息，省份名称必须是 “省”，可以获取 “92号汽油”、“95号汽油”、“98号汽油”、“0号柴油” 。
        油价调整周期为每10个工作日一次，调整时间为工作日的24时。
        比如：省份为 “安徽” ，工具会返回 “安徽” 的今日油价信息。
        Args:
            province (str): 省份名称，例如：安徽
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": dict  # 油价信息，包含省份、92号汽油、95号汽油、98号汽油、0号柴油、更新时间
                }
        """
        try:
            logger.info(f'开始获取 {province} 的油价信息...')
            url = 'https://youjia.bazhepu.com/'
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='table table-bordered table-hover')
            if not table:
                error_msg = '未找到油价表格'
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if cols and province in cols[0].text:
                    result = {
                        "省份名称": province,
                        "92号汽油": cols[1].text,
                        "95号汽油": cols[2].text,
                        "98号汽油": cols[3].text,
                        "0号柴油": cols[4].text,
                        "更新时间": cols[5].text
                    }
                    logger.info(f"成功获取 {province} 的油价信息")
                    logger.info(f"油价信息: {result}")
                    return {"success": True, "result": result}
            logger.error(f'未找到 {province} 的油价信息')
            return {"success": False, "result": f"未找到 {province} 的油价信息"}
        except requests.exceptions.RequestException as e:
            error_msg = f"请求出错: {e}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        except Exception as e:
            error_msg = f"获取油价失败: {e}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}