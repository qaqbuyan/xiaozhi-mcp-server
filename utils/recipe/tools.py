import logging
from mcp.server.fastmcp import FastMCP
from utils.recipe.chinese_food import get_chinese_food
from utils.recipe.chinese_detailed_steps import get_chinese_detailed_steps
from utils.recipe.chinese_weekly_popular_recipe import get_chinese_weekly_popular_recipes

def register_recipe_tools(mcp: FastMCP):
    """集中注册所有菜谱相关工具"""
    logger = logging.getLogger('菜谱工具')
    logger.info("准备注册...")
    # 获取中餐的菜谱以及做法
    get_chinese_food(mcp)
    # 本周热门中餐菜谱
    get_chinese_weekly_popular_recipes(mcp)
    # 获取中餐详细步骤
    get_chinese_detailed_steps(mcp)
    logger.info("注册完成")