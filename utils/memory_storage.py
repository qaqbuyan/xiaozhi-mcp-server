import os
import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('记忆数据')

def read_save_memory_data(mcp: FastMCP):
    """记忆数据"""
    @mcp.tool()
    def read_save_memory_data(name: str, content: str = '') -> dict:
        """管理记忆数据，用来存储或读取用户的记忆数据。
        只要是用户的记忆数据，都可以调用该工具进行存储。
        关于记忆体：
            记忆体是指用户的记忆数据，包括用户的聊天记录、用户的问题、用户的回答、用户的指令等。
            每次存储记忆数据时，必须要带上本次用户的全部询问问题内容，以及用户的全部回答内容。
            不建议存储用户的敏感信息，比如用户的手机号、用户的身份证号、用户的银行卡号等。
            不要存储用户 '请求存储本轮记忆数据' 以及 '要求储存本轮对话记忆数据' 这种数据内容。
        比如存储本次的记忆（记忆体），那么就调用该工具进行存储。
        每一次退出前，必须先调用该工具存储本次对话的用户记忆数据，然后再退出
        而后每一次启动时，必须先调用该工具读取上次记忆数据。
        查一下 '张三' 的记忆或查一下记忆库，就调用该工具。
        若 content 为空，则读取 name 对应的全部记忆数据；否则将 content 存储到对应 name 下。
        Args:
            name (str): 用户名称（用于区分不同用户的记忆）。
            content (str): 记忆内容，默认为空字符串，表示读取记忆数据。
        Returns:
            dict: 包含操作成功状态和结果的字典。
        """
        logger.info("开始执行记忆存储操作")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        storage_path = os.path.join(base_dir, '..', 'tmp', 'memory_storage.json')
        data = {}
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info("成功加载记忆存储文件")
            except json.JSONDecodeError:
                logger.warning("记忆存储文件格式错误，将使用空数据")
                pass
        if not content:
            logger.info(f"成功获取 {name} 的记忆内容")
            return {"success": True, "result": data.get(name, [])}
        if name in data and content in data[name]:
            error_msg = f"{name} 记忆内容已存在"
            logger.info(error_msg)
            return {"success": False, "result": error_msg}
        if name not in data:
            data[name] = []
        data[name].append(content)
        storage_dir = os.path.dirname(storage_path)
        os.makedirs(storage_dir, exist_ok=True)
        try:
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"成功更新记忆存储文件，存储内容为：{content}")
            return {"success": True, "result": "记忆存储成功"}
        except Exception as e:
            error_msg = f"更新记忆存储文件失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}