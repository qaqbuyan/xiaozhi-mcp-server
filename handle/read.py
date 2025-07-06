import json
import asyncio
import logging

logger = logging.getLogger('管道服务')

async def read_data(process, websocket):
    """从进程stdout读取数据并发送到WebSocket"""
    printed = False
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
            try:
                json_data = json.loads(data.strip())
                if json_data.get('id') == 1 and not printed:
                    if 'result' in json_data and 'tools' in json_data['result']:
                        for tool in json_data['result']['tools']:
                            name = tool.get('name', '')
                            description = tool.get('description', '')
                            first_line = description.split('\n')[0]
                            logger.debug(f"{name} - {first_line}")
                        logger.info('已注册工具数量：%d' % len(json_data['result']['tools']))
                    printed = True
            except json.JSONDecodeError:
                pass
            logger.info("发送响应...")
            await websocket.send(data)
    except Exception as e:
        logger.error(f"进程到WebSocket管道错误: {e}")
        raise