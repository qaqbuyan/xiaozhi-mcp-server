import logging
from utils.server import server
from mcp.server.fastmcp import FastMCP
from utils.qq_info import query_qq_info
from utils.bing_search import bing_search
from utils.oil_price import get_oil_price
from utils.web_content import get_web_content
from utils.ip_address import query_ip_address
from utils.life_teasing import get_life_teasing
from utils.exchange_rate import get_exchange_rate
from utils.memory_storage import read_save_memory_data
from utils.poisonous_chicken_soup import get_poisonous_chicken_soup
from utils.standard_weight_calculator import get_standard_weight_calculator

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
    # 记忆管理
    read_save_memory_data(mcp)
    # 今日油价
    get_oil_price(mcp)
    # 汇率查询
    get_exchange_rate(mcp)
    # 标准体重
    get_standard_weight_calculator(mcp)
    logger.info('注册完成')