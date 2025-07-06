import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('必应搜索')

def bing_search(mcp: FastMCP):
    """必应搜索"""
    @mcp.tool()
    def bing_search(search: str, pagination: int = None) -> dict:
        """用于在必应搜索引擎中搜索内容，当需要搜索网页内容时使用该工具。
        Args:
            search (str): 搜索关键词
            pagination (int, optional): 分页参数，从第几项开始. Defaults to None.
        Returns:
            dict: 返回搜索结果，格式为:
                {
                    'success': bool,  # 是否成功
                    'result': {
                        'statistics': str,  # 搜索结果统计信息
                        'results': [
                            {
                                'title': str,  # 结果标题
                                'link': str,   # 结果链接
                                'description': str  # 结果描述
                            },
                            ...
                        ]
                    }
                }
        """
        url = f"https://cn.bing.com/search?q={search}&first={pagination}" if pagination is not None else f"https://cn.bing.com/search?q={search}"
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始搜索: {search}")
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('li', class_='b_algo')
            result_count = soup.find('span', class_='sb_count').text
            results = {
                'statistics': result_count,
                'results': [
                    {
                        'title': paragraph.find('h2').text,
                        'link': paragraph.find('a')['href'],
                        'description': paragraph.find('p').text.replace('\u2002', ' ') if paragraph.find('p') else ''
                    }
                    for paragraph in paragraphs
                ]
            }
            logger.info(f"成功获取搜索结果: {results}")
            return {"success": True, "result": results}
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索失败: {e}")
            return {"success": False, "result": f"搜索失败: {e}"}