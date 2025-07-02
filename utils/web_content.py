import re
import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('网页内容')

def get_web_content(mcp: FastMCP):
    """网页内容查询"""
    @mcp.tool()
    def get_web_content(url: str) -> dict:
        """用于获取网页内容，当查询网页，获取网页内容或者网站内容信息时，立即使用该工具。
        Args:
            url (str): 网页URL，必须填写，例如：https://www.bilibili.com/
        Returns:
            dict: 返回包含success和result字段的字典
        """
        try:
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            content = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', response.text)
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
            if body_match:
                clean_text = re.sub(r'<[^>]+>', '', body_match.group(1))
                clean_text = '\n'.join(line.strip() for line in clean_text.split('\n') if line.strip())
                logger.info(f"成功获取网页内容，长度: {len(clean_text)} 字符")
                logger.info(f"返回数据：{' '.join(clean_text.split())}")
                return {"success": True, "result": clean_text}
            logger.error("未能提取正文内容")
            return {"success": False, "result": "未能提取正文内容"}
        except requests.exceptions.RequestException as e:
            error_message = f"请求出错: {e}"
            logger.error(error_message)
            return {"success": False, "result": error_message}
        except Exception as e:
            error_message = f"配置读取错误: {e}"
            logger.error(error_message)
            return {"success": False, "result": error_message}