import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('B站用户信息')

def query_bilibili_user(mcp: FastMCP):
    """查询用户空间"""
    @mcp.tool()
    def query_bilibili_user(mid: str) -> dict:
        """用于查询B站用户空间信息的公开信息，不包含私密信息
            video：用户发布的视频数量
            bangumi：追番的数量
            cinema：在B站有作品的电影数量
            channel（master和guest）：可能分别指主频道和客频道相关情况
            favourite（master和guest）：可能跟收藏相关
            tag：可能是设置的标签数量
            article：发布的文章数量
            playlist：播放列表数量
            album：相册数量
            audio：音频数量
            pugv：可能是专业用户创作视频相关
            season_num：也许是系列作品的季数
            opus：可能指作品总数
            following：关注人数
            whisper：可能是悄悄话相关数量
            black：也许是黑名单人数
            follower：粉丝数量
        Args:
            mid (str): B站用户UID，必须填写，例如：86920865
        Returns:
            dict: 返回合并后的用户空间信息和关系统计信息
        """
        config = load_config()
        web_location = str(config['bilibili_api']['web_location'])
        space_url = f"https://api.bilibili.com/x/space/navnum?mid={mid}&web_location={web_location}"
        relation_url = f"https://api.bilibili.com/x/relation/stat?vmid={mid}&web_location={web_location}"
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询B站用户 {mid} 信息...")
            space_response = requests.get(space_url, headers=headers, timeout=5)
            space_response.raise_for_status()
            space_data = space_response.json()
            relation_response = requests.get(relation_url, headers=headers, timeout=5)
            relation_response.raise_for_status()
            relation_data = relation_response.json()
            if space_data["code"] == 0 and relation_data["code"] == 0:
                relation_data["data"].pop("mid", None)
                result = {
                    "success": True,
                    "result": {
                        **space_data["data"],
                        **relation_data["data"]
                    }
                }
                logger.info(f"成功获取B站用户 {mid}")
                logger.info(f"返回数据：{result}")
                return result
            else:
                error_code = space_data["code"] if space_data["code"] != 0 else relation_data["code"]
                logger.error(f"获取失败状态码：{error_code}")
                return {"success": False, "result": f"获取用户信息失败，状态码: {error_code}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}