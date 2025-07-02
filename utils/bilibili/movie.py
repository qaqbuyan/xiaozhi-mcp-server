import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('电影推荐')

def get_bilibili_movie(mcp: FastMCP):
    """电影查询(分区查询)"""
    @mcp.tool()
    def get_bilibili_movie(sort_by: str = "") -> dict:
        """用于查询B站电影信息
            该工具返回的是视频ID，不是视频链接。
            这些链接除非需要，否则不要将下面这些链接进行返回或者告诉用户。
            视频的拼接地址：https://www.bilibili.com/video/
            你需要自行拼接视频ID，才能获取到对应链接。
        Args:
            sort_by (str): 排序方式，可选: 
            'views'(观看最多), 'low_views'(观看最少),
            'oldest'(时间最早), 'newest'(时间最新),
            'danmu'(弹幕最多), 'low_danmu'(弹幕最少),
            ''(空字符串表示随机返回1个视频)
        Returns:
            dict: 返回动态分区信息
        """
        config = load_config()
        web_location = str(config['bilibili_api']['web_location'])
        url = "https://api.bilibili.com/x/web-interface/dynamic/region"
        params = {
            "ps": config['bilibili_api']['movie']['ps'],
            "pn": config['bilibili_api']['movie']['pn'],
            "rid": config['bilibili_api']['movie']['rid'],
            "web_location": str(config['bilibili_api']['web_location'])
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询B站动态分区信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                result = []
                for item in data["data"]["archives"]:
                    result.append({
                        "title": item["title"],
                        "bvid": item["bvid"],
                        "pubdate": item["pubdate"],
                        "view": item["stat"]["view"],
                        "like": item["stat"]["like"],
                        "danmaku": item["stat"]["danmaku"],
                        "duration": item["duration"],
                        "owner": item["owner"]["name"]
                    })
                if sort_by == 'views':
                    result = sorted(result, key=lambda x: x['view'], reverse=True)
                    result = [result[0]] if result else []
                elif sort_by == 'low_views':
                    result = sorted(result, key=lambda x: x['view'])
                    result = [result[0]] if result else []
                elif sort_by == 'oldest':
                    result = sorted(result, key=lambda x: x['pubdate'])
                    result = [result[0]] if result else []
                elif sort_by == 'newest':
                    result = sorted(result, key=lambda x: x['pubdate'], reverse=True)
                    result = [result[0]] if result else []
                elif sort_by == 'danmu':
                    result = sorted(result, key=lambda x: x['danmaku'], reverse=True)
                    result = [result[0]] if result else []
                elif sort_by == 'low_danmu':
                    result = sorted(result, key=lambda x: x['danmaku'])
                    result = [result[0]] if result else []
                else:
                    import random
                    result = [random.choice(result)] if result else []
                logger.info(f"成功获取B站动态分区信息: {result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取动态分区信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}