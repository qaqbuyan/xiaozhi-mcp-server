import logging
import feedparser
from datetime import datetime
from config.loader import load_config

logger = logging.getLogger('RSS解析')

def parse_rss_feeds(rss_list):
    """解析所有 RSS 订阅源，获取文章信息"""
    all_items = []
    config = load_config()
    headers = {'User-Agent': config.get('http_headers', {}).get('user_agent', '')}
    for name, url in rss_list:
        try:
            feed = feedparser.parse(url, request_headers=headers)
            for entry in feed.entries:
                try:
                    pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                    pub_date = pub_date.replace(tzinfo=None)  # 移除时区信息
                except ValueError:
                    try:
                        pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                    except (ValueError, AttributeError):
                        continue
                all_items.append({
                    'source': name,
                    'title': entry.title,
                    'link': entry.link,
                    'published': pub_date
                })
        except Exception as e:
            # 使用日志记录错误信息
            logger.error(f"请求 {url} 失败，错误信息: {str(e)}，跳过该 RSS 源")
            # 返回错误状态
            return [], f"请求 {url} 失败，错误信息: {str(e)}"
    return all_items, None