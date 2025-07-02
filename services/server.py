import asyncio
import random
import logging
import sys
from config.loader import load_config
from handle.connect import connect_to_server
from handle.start import start

logger = logging.getLogger('管道服务')

config = load_config()

# 从配置获取重连设置
INITIAL_BACKOFF = config['reconnection']['initial_backoff']
MAX_BACKOFF = config['reconnection']['max_backoff']
reconnect_attempt = config['reconnection']['reconnect_attempt']
backoff = config['reconnection']['backoff']

async def server(uri):
    """带重试机制的WebSocket服务器连接"""
    global reconnect_attempt, backoff
    while True:  # 无限重连
        try:
            if reconnect_attempt > 0:
                wait_time = backoff * (1 + random.random() * 0.1)
                logger.info(f"等待 {wait_time:.2f} 秒后进行第 {reconnect_attempt} 次重连尝试...")
                await asyncio.sleep(wait_time)
            await connect_to_server(uri)
        except Exception as e:
            reconnect_attempt += 1
            logger.warning(f"连接关闭(尝试次数: {reconnect_attempt}): {e}")
            backoff = min(backoff * 2, MAX_BACKOFF)