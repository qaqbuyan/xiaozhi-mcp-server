import logging
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.rss.parser import parse_rss_feeds

logger = logging.getLogger('RSS解析')

def get_rss_articles(mcp: FastMCP):
    """获取 RSS 文章"""
    @mcp.tool()
    def get_rss_articles(rss_name=None, get_latest=True) -> dict:
        """获取指定 RSS 源的文章，若不指定则获取所有 RSS 源的文章。
        当查询文章或者rss时，立刻使用该工具。
        Args:
            rss_name (str): 要获取文章的 RSS 源名称，可选参数，（例如：'卟言博客'）。
            get_latest (bool): 是否获取最新文章，默认为 True，若为 False 则获取最旧文章。
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": list    # 文章列表，列表中的每个元素是一个字典，包含以下字段：
                        # 'source': RSS 源名称
                        # 'title': 文章标题
                        # 'link': 文章链接（
                        不需要告诉用户，用户可以根据自己的需要自行询问是否打开这个链接
                        如果需要请使用 'open_website' 工具来进行打开。）
                        # 'published': 文章发布时间，格式为 '%Y-%m-%d %H:%M:%S'
                }
        """
        try:
            logger.info(f"开始获取 {'所有' if not rss_name else rss_name} RSS 文章")
            config = load_config()
            # 获取所有 RSS 订阅源
            all_rss_list = [(item['name'], item['url']) for item in config.get('rss', [])]
            if rss_name:
                rss_list = [item for item in all_rss_list if item[0] == rss_name]
                if not rss_list:
                    error_msg = f"未找到名为 {rss_name} 的 RSS 源，请检查配置文件。"
                    logger.error(error_msg)
                    return {"success": False, "result": error_msg}
            else:
                rss_list = all_rss_list
            # 解析 RSS 订阅源
            all_items, error = parse_rss_feeds(rss_list)
            if error:
                logger.error(error)
                return {"success": False, "result": error}
            if not all_items:
                error_msg = "未获取到文章，请检查 RSS 源配置或网络连接。"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            # 按发布时间排序
            reverse = get_latest
            sorted_items = sorted(all_items, key=lambda x: x['published'], reverse=reverse)
            recent_items = sorted_items[:10]
            # 转换为字典列表输出
            result = []
            for item in recent_items:
                result.append({
                    'source': item['source'],
                    'title': item['title'],
                    'link': item['link'],
                    'published': item['published'].strftime('%Y-%m-%d %H:%M:%S')
                })
            logger.info(f"成功获取 {'所有' if not rss_name else rss_name} RSS 文章")
            logger.info(f"共获取到 {len(result)} 条文章")
            logger.info(f"获取到的文章: {result}")
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            error_msg = f"获取 RSS 文章失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}