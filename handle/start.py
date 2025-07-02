from services.register import register
from mcp.server.fastmcp import FastMCP
from handle.logger import setup_logging

def start():
    logger = setup_logging()
    logger.info("启动注册服务...")
    # 创建MCP服务器
    mcp = FastMCP("管道服务")
    # 注册服务
    register(mcp)
    # 添加初始化完成标志
    mcp._initialized = True
    logger.info("服务注册完成，准备接收请求")
    # 确保服务注册完成后再启动服务器
    try:
        mcp.run(transport="stdio")
    except RuntimeError as e:
        logger.error(f"服务器启动失败: {e}")