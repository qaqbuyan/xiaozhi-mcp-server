import logging
import requests
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.bilibili.wbi_signed import get_wbi_signed

config = load_config()
logger = logging.getLogger('B站热门视频')

def get_bilibili_popular_videos(mcp: FastMCP):
    """热门视频查询"""
    @mcp.tool()
    def get_bilibili_popular_videos(pn: int = config['bilibili_api']['hot_videos']['pn']) -> dict:
        """用于查询B站热门视频信息
            该工具的主要功能是获取B站的热门视频信息，包括aid、标题等。
        Args:
            pn (int): 页码，默认为配置文件中的值
        Returns:
            dict: 返回热门视频信息
                "aid": 视频的唯一标识符
                "copyright": 视频版权信息
                "title": 视频标题
                "pubdate": 视频发布时间
                "desc": 视频描述
                "duration": 视频时长（秒）
                "mid": 视频作者的用户ID
                "name": 视频作者的用户名
                "view": 视频观看量
                "danmaku": 视频弹幕数
                "reply": 视频评论数
                "favorite": 视频收藏数
                "coin": 视频投币数
                "share": 视频分享数
                "like": 视频点赞数
                "bvid": 视频的BVID
                "pub_location": 视频发布地点（若有）
            注意：
                1.视频返回的是视频ID即bvid，不是视频链接。视频的拼接地址：https://www.bilibili.com/video/ ，视频链接需要自行拼接。
                2.主页返回的是作者ID即mid，不是作者链接。作者的拼接地址：https://space.bilibili.com/ ，作者主页链接需要自行拼接。
                3.拼接的视频链接和作者主页链接，不向用户展示，只用于查询视频信息或询问时给予用户。
        """
        logger.info(f"开始查询B站热门视频信息，页码为{pn}")
        config = load_config()
        signed = get_wbi_signed()
        url = "https://api.bilibili.com/x/web-interface/popular"
        params = {
            "pn": pn,
            "ps": config['bilibili_api']['hot_videos']['ps'],
            "w_rid": signed['w_rid'],
            "wts": signed['wts']
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询B站热门视频信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                result = []
                for item in data["data"]["list"]:
                    result.append({
                        "aid": item["aid"],
                        "copyright": item["copyright"],
                        "title": item["title"],
                        "pubdate": item["pubdate"],
                        "desc": item["desc"].replace('\n', ''),
                        "duration": item["duration"],
                        "mid": item["owner"]["mid"],
                        "name": item["owner"]["name"],
                        "view": item["stat"]["view"],
                        "danmaku": item["stat"]["danmaku"],
                        "reply": item["stat"]["reply"],
                        "favorite": item["stat"]["favorite"],
                        "coin": item["stat"]["coin"],
                        "share": item["stat"]["share"],
                        "like": item["stat"]["like"],
                        "bvid": item["bvid"],
                        "pub_location": item.get("pub_location", "")
                    })
                logger.info(f"成功获取B站热门视频信息: {len(result)}条")
                result = {
                    "success": True,
                    "result": {
                        "list": result,
                        "present": f"当前页码：{pn}"
                    }
                }
                log_result_str = str(result).replace('\n', '')
                logger.info(f"返回数据：{log_result_str}")
                return {"success": True, "list": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取热门视频信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}