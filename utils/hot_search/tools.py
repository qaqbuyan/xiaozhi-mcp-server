import logging
from mcp.server.fastmcp import FastMCP
from utils.hot_search.baidu import get_baidu_hot_search
from utils.hot_search.weibo import get_weibo_hot_search
from utils.hot_search.bilibili import get_bilibili_hot_search

def register_hot_search_tools(mcp: FastMCP):
    """集中注册所有热搜相关工具"""
    logger = logging.getLogger('热搜工具')
    logger.info("准备注册...")
    # 哔哩哔哩热搜查询
    get_bilibili_hot_search(mcp)
    # 百度热搜查询
    get_baidu_hot_search(mcp)
    # 微博热搜查询
    get_weibo_hot_search(mcp)
    logger.info("注册完成")