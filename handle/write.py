import logging

logger = logging.getLogger('管道服务')

async def write_data(websocket, process):
    """从WebSocket读取数据并写入进程stdin"""
    try:
        while True:
            message = await websocket.recv()
            logger.info("收到响应...")
            if not isinstance(message, str):
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                else:
                    message = str(message)
            process.stdin.write(message + '\n')
            process.stdin.flush()
    except Exception as e:
        logger.error(f"WebSocket到进程管道错误: {e}")
        raise
    finally:
        if not process.stdin.closed:
            process.stdin.close()