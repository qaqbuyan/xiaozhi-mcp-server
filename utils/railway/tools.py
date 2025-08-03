import logging
from mcp.server.fastmcp import FastMCP
from utils.railway.query_china_ticket import query_china_train_info

def register_railway_tools(mcp: FastMCP):
    """集中注册所有铁路相关工具"""
    logger = logging.getLogger('铁路工具')
    logger.info("准备注册铁路工具...")
    # 获取中国铁路的信息
    query_china_train_info(mcp)
    logger.info("注册完成")