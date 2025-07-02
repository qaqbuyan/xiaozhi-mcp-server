import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('B站追番查询')

def get_bilibili_chasing_fan(mcp: FastMCP):
    """查询追番信息"""
    @mcp.tool()
    def get_bilibili_chasing_fan(sort_by: str = "") -> dict:
        """用于查询B站追番信息
            该工具返回的是视频ID，不是视频链接。
            番视频的拼接地址：https://www.bilibili.com/bangumi/play/ss
            你需要自行拼接视频ID，才能获取到对应链接。
            这个番链接除非需要问你，否则不要将这个番链接进行返回或者告诉用户。
        Args:
            sort_by (str): 排序方式，默认随机返回1个视频，可选参数: 
            'views'(观看最多), 'low_views'(观看最少),
            'oldest'(时间最早), 'newest'(时间最新),
            ''(空字符串表示随机返回1个视频)
        Returns:
            dict: 返回追番信息
        """
        config = load_config()
        url = "https://api.bilibili.com/pgc/web/timeline/v2"
        params = {
            "day_before": config['bilibili_api']['chasing_fan']['day_before'],
            "day_after": config['bilibili_api']['chasing_fan']['day_after'],
            "season_type": config['bilibili_api']['chasing_fan']['season_type'],
            "web_location": str(config['bilibili_api']['web_location'])
        }
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info("开始查询B站追番信息...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["code"] == 0:
                result = []
                for item in data["result"]["latest"]:
                    result.append({
                        "follows": item["follows"],
                        "plays": item["plays"],
                        "pub_index": item["pub_index"],
                        "pub_time": item["pub_time"],
                        "pub_ts": item["pub_ts"],
                        "season_id": item["season_id"],
                        "title": item["title"]
                    })
                # 根据参数排序
                if sort_by == 'views':
                    result = sorted(result, key=lambda x: int(x['plays'].replace('亿','00000000').replace('万','0000').replace('.','')) if '亿' in x['plays'] or '万' in x['plays'] else int(x['plays']), reverse=True)
                    result = [result[0]] if result else []
                elif sort_by == 'low_views':
                    result = sorted(result, key=lambda x: int(x['plays'].replace('亿','00000000').replace('万','0000').replace('.','')) if '亿' in x['plays'] or '万' in x['plays'] else int(x['plays']))
                    result = [result[0]] if result else []
                elif sort_by == 'oldest':
                    result = sorted(result, key=lambda x: x['pub_ts'])
                    result = [result[0]] if result else []
                elif sort_by == 'newest':
                    result = sorted(result, key=lambda x: x['pub_ts'], reverse=True)
                    result = [result[0]] if result else []
                else:
                    import random
                    result = [random.choice(result)] if result else []
                logger.info(f"成功获取B站追番信息: {result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"获取失败状态码：{data['code']}")
                return {"success": False, "result": f"获取追番信息失败，状态码: {data['code']}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"无法访问链接：{e}")
            return {"success": False, "result": f"无法访问链接：{e}"}