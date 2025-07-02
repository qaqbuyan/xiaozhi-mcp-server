import logging
from mcp.server.fastmcp import FastMCP
from utils.recipe.chinese import get_chinese_food

def register_recipe_tools(mcp: FastMCP):
    """集中注册所有菜谱相关工具"""
    logger = logging.getLogger('菜谱工具')
    logger.info("准备注册...")
    # 获取中餐的菜谱以及做法
    get_chinese_food(mcp)
    logger.info("注册完成")