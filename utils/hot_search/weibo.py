import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('微博热搜')

def get_weibo_hot_search(mcp: FastMCP):
    """获取微博实时热搜内容"""
    @mcp.tool()
    def get_weibo_hot_search(limit: int = 10) -> dict:
        """用于获取微博实时热搜内容
        Args:
            limit (int): 返回结果数量，默认为10
        Returns:
            dict: 返回热搜内容信息
        """
        config = load_config()
        url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot%26eqid%3Dcd8960f80007f2e00000000464748a67"
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询微博实时热搜内容...")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            result = []
            cards = data.get('data', {}).get('cards', [])
            for card in cards:
                card_group = card.get('card_group', [])
                for item in card_group:
                    if 'desc' in item:
                        result.append(item.get('desc', ''))
                        if len(result) >= limit:
                            break
                if len(result) >= limit:
                    break
            logger.info(f"成功获取 {len(result)} 条微博实时热搜内容")
            logger.info(f"获取到的热搜内容: {result}")
            return {"success": True, "list": result}
        except requests.exceptions.RequestException as e:
            error_msg = f"获取微博热搜失败: {e}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}