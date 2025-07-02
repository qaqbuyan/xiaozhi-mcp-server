import sys
import signal
import asyncio
import logging
from services.server import server
from config.loader import load_config
from handle.logger import setup_logging
from handle.signal import signal_handler

if __name__ == "__main__":
    logger = setup_logging()
    logger = logging.getLogger('管道代理')
    signal.signal(signal.SIGINT, signal_handler)
    endpoint_url = load_config()['endpoint']['url']
    if not endpoint_url.startswith(('wss://', 'ws://')):
        logger.error("请设置有效的`MCP_ENDPOINT`，必须以wss://或ws://开头")
        sys.exit(1)
    try:
        asyncio.run(server(endpoint_url))
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行错误: {e}")