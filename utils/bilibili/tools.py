import logging
from mcp.server.fastmcp import FastMCP
from utils.bilibili.user import query_bilibili_user
from utils.bilibili.movie import get_bilibili_movie
from utils.bilibili.chasing_fan import get_bilibili_chasing_fan
from utils.bilibili.hot.videos import get_bilibili_popular_videos
from utils.bilibili.history.live import get_bilibili_history_live
from utils.bilibili.live.get_danmu import get_bilibili_live_danmu
from utils.bilibili.live.send_danmu import send_bilibili_live_danmu
from utils.bilibili.referral import get_bilibili_recommended_videos
from utils.bilibili.live.get_room_base_info import get_room_base_info
from utils.bilibili.history.videos import get_bilibili_history_videos
from utils.bilibili.comments.video import get_bilibili_video_comments
from utils.bilibili.history.article import get_bilibili_history_article
from utils.bilibili.live.get_anchor_info import get_bilibili_anchor_info
from utils.bilibili.video_online_total import get_bilibili_video_online_total

def register_bilibili_tools(mcp: FastMCP):
    """集中注册所有B站相关工具"""
    logger = logging.getLogger('B站工具')
    logger.info("准备注册...")
    # 推荐视频工具
    get_bilibili_recommended_videos(mcp)
    # 查询追番信息
    get_bilibili_chasing_fan(mcp)
    # 电影查询(分区查询)
    get_bilibili_movie(mcp)
    # 查询用户空间
    query_bilibili_user(mcp)
    # 查询直播弹幕
    get_bilibili_live_danmu(mcp)
    # 发送直播弹幕
    send_bilibili_live_danmu(mcp)
    # 查询视频在线人数
    get_bilibili_video_online_total(mcp)
    # 获取历史视频
    get_bilibili_history_videos(mcp)
    # 历史直播
    get_bilibili_history_live(mcp)
    # 历史专栏
    get_bilibili_history_article(mcp)
    # 热门视频
    get_bilibili_popular_videos(mcp)
    # 获取主播信息
    get_bilibili_anchor_info(mcp)
    # 获取直播间基本信息
    get_room_base_info(mcp)
    # 视频评论
    get_bilibili_video_comments(mcp)
    logger.info("注册完成")