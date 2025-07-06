import os
import logging
import requests
from datetime import datetime
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.bilibili.wbi_signed import get_wbi_signed

config = load_config()
logger = logging.getLogger('B站视频推荐')

def get_bilibili_recommended_videos(mcp: FastMCP):
    """推荐视频工具"""
    @mcp.tool()
    def get_bilibili_recommended_videos(
            brush: int = config['bilibili_api']['recommended']['fresh'],
            fetch_row: int = config['bilibili_api']['recommended']['fetch_count'],
            sort_by: str = ""
        ) -> dict:
        """获取B站推荐视频列表
            该工具返回的是视频ID，不是视频链接。
            可以询问是否打开视频链接，如果需要使用 'open_website' 工具来进行打开。
        Args:
            brush (int): b站的1小时新鲜度索引, 内容新鲜度索引, 刷新次数，其实这几个参数都是一样的，可选，默认为配置中的fresh
            fetch_row (int): 每次请求返回的视频数量, 可选，默认为配置中的fetch_count
                注意：fetch_row 每一次请求参数必须在之前请求的返回数量中再加3，
                例如：第一次请求返回了10个视频，那么第二次请求的fetch_row必须是13，
                第三次请求的fetch_row必须是16，以此类推。
                否则会返回400错误。
            sort_by (str): 排序方式，可选: 
                'views'(观看最多), 'low_views'(观看最少),
                'likes'(收藏最多), 'low_likes'(收藏最少),
                'oldest'(时间最早), 'newest'(时间最新),
                'danmu'(弹幕最多), 'low_danmu'(弹幕最少),
                'high_likes'(点赞最多), 'low_likes'(点赞最少),
                ''(空字符串表示随机返回全部视频)
        Returns:
            dict: 返回包含success和result字段的字典
                result: 包含视频信息的列表，每个视频信息为字典，
                注意：
                    1.视频返回的是视频ID即bvid，不是视频链接。视频的拼接地址：https://www.bilibili.com/video/ ，视频链接需要自行拼接。
                    2.主页返回的是作者ID即mid，不是作者链接。作者的拼接地址：https://space.bilibili.com/ ，作者主页链接需要自行拼接。
                    3.拼接的视频链接和作者主页链接，不向用户展示，只用于查询视频信息或询问时给予用户。
                    4.时长单位是秒，需要自行转换为分钟或小时。
        """
        signed = get_wbi_signed()
        fetch_count = max(fetch_row, 4)
        url = "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd"
        params = {
            "web_location": config['bilibili_api']['recommended']['web_location'],
            "y_num": config['bilibili_api']['recommended']['y_num'],
            "fresh_type": config['bilibili_api']['recommended']['fresh_type'],
            "feed_version": "V8",
            "fresh_idx_1h": brush,
            "fetch_row": fetch_count,
            "fresh_idx": brush,
            "brush": brush,
            "homepage_ver": 1,
            "ps": config['bilibili_api']['recommended']['ps'],
            "last_y_num": config['bilibili_api']['recommended']['last_y_num'],
            "screen": config['bilibili_api']['recommended']['screen'],
            "seo_info": "",
            "last_showlist": config['bilibili_api']['recommended']['last_showlist'],
            "uniq_id": config['bilibili_api']['recommended']['uniq_id'],
            "w_rid": signed['w_rid'],
            "wts": signed['wts']
        }
        cache_dir = os.path.join(os.getcwd(), 'tmp')
        cache_file = os.path.join(cache_dir, 'bilibili_recommended_videos_cache.tmp')
        try:
            if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
                logger.info("读取缓存文件...")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_ids = f.read().strip()
                    if cached_ids:
                        params["last_showlist"] = cached_ids
                        logger.info(f"使用缓存中的视频ID列表，共 {len(cached_ids.split(', '))} 个ID")
        except Exception as e:
            logger.warning(f"读取缓存文件失败: {e}")
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始获取B站推荐视频...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                video_ids = ""
                videos = []
                count = 0
                for item in data["data"]["item"]:
                    if item["goto"] != "av":
                        continue
                    video_id = str(item["id"])
                    if not (video_id.startswith('av_') or video_id.startswith('ad_') or video_id.startswith('live_')):
                        video_id = f"av_n_{video_id}"
                    if video_ids:
                        video_ids += ","
                    video_ids += video_id
                    video = {
                        "作者": item["owner"]["name"],
                        "主页": item["owner"]["mid"],
                        "标题": item["title"],
                        "链接": item["uri"].split('/')[-1],
                        "时间": datetime.fromtimestamp(item["pubdate"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "观看": item["stat"]["view"],
                        "收藏": item["stat"]["like"],
                        "弹幕": item["stat"]["danmaku"],
                        "点赞": f"{item['stat']['like']//10000}万" if item.get('stat',{}).get('like',0) >= 10000 else "没有",
                        "时长": f"{item['duration']}",
                        "aid": item["id"],
                        "cid": item["cid"]
                    }
                    videos.append(video)
                    count += 1
                    if count >= fetch_count:
                        break
                if sort_by == 'views':
                    videos = sorted(videos, key=lambda x: x['观看'], reverse=True)
                    videos = [videos[0]] if videos else []
                elif sort_by == 'low_views':
                    videos = sorted(videos, key=lambda x: x['观看'])
                    videos = [videos[0]] if videos else []
                elif sort_by == 'likes':
                    videos = sorted(videos, key=lambda x: x['收藏'], reverse=True)
                    videos = [videos[0]] if videos else []
                elif sort_by == 'low_likes':
                    videos = sorted(videos, key=lambda x: x['收藏'])
                    videos = [videos[0]] if videos else []
                elif sort_by == 'oldest':
                    videos = sorted(videos, key=lambda x: x['时间'])
                    videos = [videos[0]] if videos else []
                elif sort_by == 'newest':
                    videos = sorted(videos, key=lambda x: x['时间'], reverse=True)
                    videos = [videos[0]] if videos else []
                elif sort_by == 'danmu':
                    videos = sorted(videos, key=lambda x: x['弹幕'], reverse=True)
                    videos = [videos[0]] if videos else []
                elif sort_by == 'low_danmu':
                    videos = sorted(videos, key=lambda x: x['弹幕'])
                    videos = [videos[0]] if videos else []
                elif sort_by == 'high_likes':
                    videos = sorted(videos, key=lambda x: int(x['点赞'].replace('万','000')) if '万' in str(x['点赞']) else int(x['点赞']) if str(x['点赞']).isdigit() else 0, reverse=True)
                    videos = [videos[0]] if videos else []
                try:
                    os.makedirs(cache_dir, exist_ok=True)
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        f.write(video_ids)
                    logger.info("缓存文件已写入")
                except Exception as e:
                    logger.warning(f"写入缓存文件失败: {e}")
                logger.info(f"成功获取B站推荐视频，共获取到 {len(videos)} 条视频")
                result = {
                    "视频": videos,
                    "新鲜度": brush,
                    "返回数量": fetch_count
                }
                logger.info(f"获取到的视频信息：{result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取推荐失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}