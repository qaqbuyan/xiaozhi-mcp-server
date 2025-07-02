import sys
import logging

logger = logging.getLogger('管道服务')

def signal_handler(sig, frame):
    """处理中断信号"""
    logger.info("收到中断信号，正在关闭...")
    sys.exit(0)