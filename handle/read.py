import asyncio
import logging

logger = logging.getLogger('管道服务')

async def read_data(process, websocket):
    """从进程stdout读取数据并发送到WebSocket"""
    try:
        while True:
            data = await asyncio.get_event_loop().run_in_executor(
                None, process.stdout.readline
            )
            if not data:
                logger.info("进程输出已结束")
                break
            if not isinstance(data, str):
                data = str(data)
            logger.debug(f">> {data[:120]}...")
            await websocket.send(data)
    except Exception as e:
        logger.error(f"进程到WebSocket管道错误: {e}")
        raise