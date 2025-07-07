import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('缺氧物品详情')

def get_oxygennotincluded_item_details(mcp: FastMCP):
    """注册获取缺氧物品详情的工具"""
    @mcp.tool()
    def get_oxygennotincluded_item_details(keyword: str) -> dict:
        """根据关键词获取缺氧物品的详细内容。
        当用户询问缺氧游戏中某物品的信息时，立刻使用该工具。
        Args:
            keyword (str): 搜索关键词，例如：浆果糕
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": dict  # 物品详情，包含制作方法、资源分析和介绍
                }
        """
        try:
            base_url = 'https://oxygennotincluded.fandom.com/zh/wiki/'
            url = base_url + keyword
            logger.info(f"开始获取关键词 {keyword} 的物品信息")
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                error_msg = f"获取物品信息失败: 404 Client Error: Not Found for url: {url}"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # 提取介绍信息
            description_meta = soup.find('meta', attrs={'name': 'description'})
            description = description_meta['content'] if description_meta else ''
            # 提取 class="mw-headline" 及其后续内容
            usages = {}
            headlines = soup.find_all(class_="mw-headline")
            for headline in headlines:
                section_title = headline.get_text(strip=True)
                sibling = headline.find_parent('h2' or 'h3').find_next_sibling()
                section_content = []
                while sibling and sibling.name not in ('h2', 'h3'):
                    if sibling.name == 'p':
                        section_content.append(sibling.get_text(strip=True))
                    sibling = sibling.find_next_sibling()
                if section_content:
                    usages[section_title] = ' '.join(section_content)
            result = {
                'description': description,
                'usages': usages
            }
            logger.info(f"成功获取关键词 {keyword} 的物品信息")
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            error_msg = f"获取物品信息失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}