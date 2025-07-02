import logging
from mcp.server.fastmcp import FastMCP
from utils.rss.articles import get_rss_articles

def register_rss_tools(mcp: FastMCP):
    """集中注册所有RSS相关工具"""
    logger = logging.getLogger('RSS工具')
    logger.info("准备注册...")
    # 获取 RSS 文章
    get_rss_articles(mcp)
    logger.info("注册完成")