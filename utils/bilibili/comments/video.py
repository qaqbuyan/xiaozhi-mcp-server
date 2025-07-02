import re
import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.bilibili.wbi_signed import get_wbi_signed

logger = logging.getLogger('B站视频评论')

def get_bilibili_video_comments(mcp: FastMCP):
    """获取视频评论"""
    @mcp.tool()
    def get_bilibili_video_comments(aid: int, next_offset: str = '', mode: int = 3) -> dict:
        """用于获取B站视频评论信息，调用该工具即可获取该视频的评论信息。
        当查询B站视频评论时，立刻调用该工具。
        需要询问用什么排序模式。
        Args:
            aid (int): 视频的 'aid' （必须，比如 '114747164856285'）
            next_offset (str): 下一页偏移量 （可选）
            mode (int): 排序模式（可选），默认是 '3' ，不需要告诉信息的传入参数，说明：
                - 1: 按时间排序
                - 2: 按点赞数排序
                - 3: 按热度排序
        Returns:
            dict: 返回包含success和result字段的字典，result中包含:
                - all_count: 总评论数
                - prev: 上一页
                - next: 下一页
                - next_offset: 下一页偏移量（用来下一次当前视频的分页）
                - mode: 排序模式
                - is_ad_loc: 是否为广告视频
                - input_disable: 是否可以评论
                - replies: 评论列表，每个评论包含:
                    - mid: 用户ID
                    - count: 评论数（加上他的评论一共多少）
                    - rcount: 回复数（有多少人回复他）
                    - ctime: 创建时间
                    - root: 根评论ID
                    - like: 点赞数
                    - uname: 用户名
                    - sign: 用户签名
                    - current_level: 用户等级
                    - message: 评论内容
                    - sub_reply_entry_text: 回复（有多少人回复）
                    - location: IP属地
                    - time_desc: 时间描述
        """
        if not aid:
                logger.error("视频aid不能为空")
                return {"success": False, "result": "视频aid不能为空"}
        if not aid.isdigit():
            logger.error(f"视频aid必须是数字，当前值: {aid}")
            return {"success": False, "result": "视频aid必须是数字"}
        config = load_config()
        signed = get_wbi_signed()
        url = "https://api.bilibili.com/x/v2/reply/wbi/main"
        params = {
            "oid": aid,
            "type": 1,
            "mode": mode,
            "pagination_str": "{\"offset\":\"" + (next_offset if next_offset else "") + "\"}",
            "plat": 1,
            "web_location": 1315875, # 表示评论区
            "w_rid": signed['w_rid'],
            "wts": signed['wts']
        }
        if not next_offset:
            params["seek_rpid"] = ""
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始获取视频 {aid} 的评论信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                logger.info(f"获取视频 {aid} 的评论信息成功")
                result = {
                    "all_count": data["data"]["cursor"]["all_count"],
                    "prev": data["data"]["cursor"]["prev"],
                    "next": data["data"]["cursor"]["next"],
                    "mode": data["data"]["cursor"]["mode"],
                    "is_ad_loc": data["data"]["cursor"].get("is_ad_loc", False),
                    "input_disable": data["data"]["cursor"].get("input_disable", False),
                    "next_offset": data["data"]["cursor"]["pagination_reply"].get("next_offset", ""),
                    "replies": [{
                        "mid": reply["member"]["mid"],
                        "count": reply["count"],
                        "rcount": reply["rcount"],
                        "ctime": reply["ctime"],
                        "root": reply["root"],
                        "like": reply["like"],
                        "uname": reply["member"]["uname"],
                        "sign": reply["member"]["sign"].replace('\n', ' ').strip(),
                        "current_level": reply["member"]["level_info"]["current_level"],
                        "message": re.sub(r'\[[^\]]*\]', '', reply["content"]["message"].replace('\n', ' ')).strip(),
                        "sub_reply_entry_text": reply["reply_control"].get("sub_reply_entry_text", "").strip(),
                        "location": reply["reply_control"].get("location", "").strip(),
                        "time_desc": reply["reply_control"].get("time_desc", "").strip()
                    } for reply in data["data"].get("replies", [])]
                }
                logger.info(f"成功获取视频 {aid} 的评论信息")
                logger.info(f"获取到的评论信息: {result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取评论失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}