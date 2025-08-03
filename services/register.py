import logging
from mcp.server.fastmcp import FastMCP
from utils.tools import register_alone_tools
from utils.svn.tools import register_svn_tools
from utils.rss.tools import register_rss_tools
from utils.games.tools import register_games_tools
from utils.recipe.tools import register_recipe_tools
from handle.packaging_flow import safe_stream_wrapper
from utils.railway.tools import register_railway_tools
from utils.bilibili.tools import register_bilibili_tools
from utils.hot_search.tools import register_hot_search_tools

logger = logging.getLogger('集中注册')

def register(mcp: FastMCP):
    """集中注册所有工具"""
    logger.info("进行所有工具注册...")
    # 注册B站相关工具
    register_bilibili_tools(mcp)
    # 注册菜谱相关工具
    register_recipe_tools(mcp)
    # 注册RSS相关工具
    register_rss_tools(mcp)
    # 注册SVN相关工具
    register_svn_tools(mcp)
    # 注册单独工具
    register_alone_tools(mcp)
    # 注册游戏相关工具
    register_games_tools(mcp)
    # 注册热搜相关工具
    register_hot_search_tools(mcp)
    # 注册铁路相关工具
    register_railway_tools(mcp)
    logger.info("所有工具注册完成")