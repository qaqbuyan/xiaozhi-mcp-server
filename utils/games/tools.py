import logging
from mcp.server.fastmcp import FastMCP
from utils.games.oxygennotincluded_item_details import get_oxygennotincluded_item_details

def register_games_tools(mcp: FastMCP):
    """集中注册所有游戏相关工具"""
    logger = logging.getLogger('游戏工具')
    logger.info("准备注册...")
    # 获取缺氧物品详情
    get_oxygennotincluded_item_details(mcp)
    logger.info("注册完成")