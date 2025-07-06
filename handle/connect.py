import sys
import asyncio
import logging
import websockets
import subprocess
from typing import Callable
from handle.write import write_data
from handle.read import read_data
from handle.print import print_stderr

logger = logging.getLogger('管道服务')

async def connect_to_server(uri: str):
    """连接到服务器并与管道服务建立双向通信管道"""
    try:
        logger.info(f"正在连接服务器...")
        async with websockets.connect(uri) as websocket:
            logger.info("成功连接到服务器")
            process = subprocess.Popen(
                [sys.executable, '-c', 'from handle.start import start; start()'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                text=True
            )
            logger.info(f"已启动注册进程")
            # 创建管道任务
            await asyncio.gather(
                write_data(websocket, process),
                read_data(process, websocket),
                print_stderr(process)
            )
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"服务器连接关闭: {e}")
        raise
    except Exception as e:
        logger.error(f"连接错误: {e}")
        raise
    finally:
        if 'process' in locals():
            logger.info("正在终止管道服务")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info("管道服务已终止")