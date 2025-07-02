import logging
from mcp.server.fastmcp import FastMCP
from utils.svn.logger import query_svn_logger
from utils.svn.latest import get_svn_logge_latest
from utils.svn.date import query_svn_time_logger
from utils.svn.revision import query_svn_revision
from utils.svn.changed_files import query_svn_changed_files

def register_svn_tools(mcp: FastMCP):
    """集中注册所有SVN相关工具"""
    logger = logging.getLogger('SVN工具')
    logger.info("准备注册...")
    # 查询版本到版本日志
    query_svn_logger(mcp)
    # 查询最新日志
    get_svn_logge_latest(mcp)
    # 查询日期日志
    query_svn_time_logger(mcp)
    # 查询版本日志
    query_svn_revision(mcp)
    # 查询文件日志
    query_svn_changed_files(mcp)
    logger.info("注册完成")