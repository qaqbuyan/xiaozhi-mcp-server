import asyncio
import sys
import logging

logger = logging.getLogger('管道服务')

async def print_stderr(process):
    """从进程标准错误输出读取数据并打印到终端"""
    try:
        while True:
            data = await asyncio.get_event_loop().run_in_executor(
                None, process.stderr.readline
            )
            if not data:
                logger.info("进程标准错误输出输出已结束")
                break
            sys.stderr.write(data)
            sys.stderr.flush()
    except Exception as e:
        logger.error(f"进程标准错误输出管道错误: {e}")
        raise