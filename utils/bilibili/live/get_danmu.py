import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('获取B站直播弹幕')

config = load_config()

def get_bilibili_live_danmu(mcp: FastMCP):
    """查询直播弹幕"""
    @mcp.tool()
    def get_bilibili_live_danmu(roomid: int = config['bilibili_api']['live']['roomid']) -> dict:
        """用于查询B站直播弹幕，当查询直播间弹幕时，立即使用该工具。
        Args:
            roomid (int): 直播间ID，默认为配置中的roomid
        Returns:
            dict: 返回包含success和result字段的字典，其中result可能包含最后十条弹幕的详细信息，具体每条弹幕包含如下字段：
                - text (str): 弹幕文本内容
                - dm_type (int): 弹幕类型
                - uid (int): 发送者的用户ID
                - nickname (str): 发送者的昵称
                - uname_color (str): 发送者昵称的颜色
                - timeline (str): 弹幕发送的时间线
                - isadmin (int): 发送者是否为管理员
                - vip (int): 发送者是否为VIP
                - svip (int): 发送者是否为年费VIP
                - medal (dict): 发送者的粉丝勋章信息
                - title (str): 发送者的头衔信息
        """
        url = "https://api.live.bilibili.com/ajax/msg"
        params = {"roomid": roomid}
        headers = {
            "User-Agent": config['http_headers']['user_agent']
        }
        try:
            logger.info(f"开始查询直播间 {roomid} 的弹幕...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                # 获取最后十条弹幕
                danmus = data["data"]["room"][-10:] if data["data"]["room"] else []
                if danmus:
                    result = []
                    for danmu in danmus:
                        result.append({
                            "text": danmu["text"],
                            "dm_type": danmu["dm_type"],
                            "uid": danmu["uid"],
                            "nickname": danmu["nickname"],
                            "uname_color": danmu["uname_color"],
                            "timeline": danmu["timeline"],
                            "isadmin": danmu["isadmin"],
                            "vip": danmu["vip"],
                            "svip": danmu["svip"],
                            "medal": danmu["medal"],
                            "title": danmu["title"]
                        })
                    logger.info(f"成功获取直播间 {roomid} 的弹幕")
                    logger.info(f"返回数据：{result}")
                    return {
                        "success": True,
                        "result": result
                    }
                else:
                    logger.info(f"直播间 {roomid} 没有弹幕")
                    return {"success": False, "result": "直播间没有弹幕"}
            logger.error("未获取到弹幕数据")
            return {"success": False, "result": "未获取到弹幕数据"}
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return {"success": False, "result": f"请求失败: {e}"}