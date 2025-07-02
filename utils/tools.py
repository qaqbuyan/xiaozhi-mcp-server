import logging
from utils.server import server
from mcp.server.fastmcp import FastMCP
from utils.qq_info import query_qq_info
from utils.bing_search import bing_search
from utils.web_content import get_web_content
from utils.ip_address import query_ip_address
from utils.life_teasing import get_life_teasing
from utils.poisonous_chicken_soup import get_poisonous_chicken_soup

def register_alone_tools(mcp: FastMCP):
    """注册单独工具"""
    logger = logging.getLogger('单独工具')
    logger.info('准备注册...')
    # 服务器状态
    server(mcp)
    # 人间凑数(生活调侃)
    get_life_teasing(mcp)
    # 毒鸡汤
    get_poisonous_chicken_soup(mcp)
    # QQ信息查询
    query_qq_info(mcp)
    # IP查询
    query_ip_address(mcp)
    # 网页内容查询
    get_web_content(mcp)
    # 必应搜索
    bing_search(mcp)
    logger.info('注册完成')