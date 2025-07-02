import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('B站视频在线人数')

def get_bilibili_video_online_total(mcp: FastMCP):
    """查询视频在线人数"""
    @mcp.tool()
    def get_bilibili_video_online_total(aid: int, cid: int) -> dict:
        """获取B站视频在线人数
        Args:
            aid (int): 视频AV号
            cid (int): 视频CID号
        Returns:
            dict: 返回包含success和result字段的字典
        """
        logger
        url = "https://api.bilibili.com/x/player/online/total"
        params = {
            "aid": aid,
            "cid": cid
        }
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始获取视频在线人数，AV号: {aid}, CID号: {cid}")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                logger.info(f"成功获取视频在线人数: {data.get('data', {}).get('total')}")
                return {
                    "success": True,
                    "result": data.get("data", {})
                }
            logger.error(f"请求失败，状态码: {data.get('code')}")
            return {
                "success": False,
                "result": f"请求失败，状态码: {data.get('code')}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return {
                "success": False,
                "result": f"请求失败: {e}"
            }