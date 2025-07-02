import time
import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('B站发送直播弹幕')

config = load_config()

def send_bilibili_live_danmu(mcp: FastMCP):
    """发送直播弹幕"""
    @mcp.tool()
    def send_bilibili_live_danmu(msg: str, roomid: int = config['bilibili_api']['live']['roomid']) -> dict:
        """发送B站直播弹幕
        Args:
            msg (str): 要发送的弹幕内容，不能为空, 不能超过20个字符
            roomid (int, optional): 直播间ID，默认为配置文件中的roomid
        Returns:
            dict: 返回包含success和result字段的字典，表示操作结果
        """
        logger.info(f"开始发送弹幕到直播间 {roomid}")
        if not msg:
            logger.error("弹幕内容不能为空")
            return {"success": False, "result": "弹幕内容不能为空"}
        if not config['bilibili_api']['auth'].get('csrf_token'):
            logger.error("CSRF token未配置")
            return {"success": False, "result": "CSRF token未配置"}
        if not config['bilibili_api']['auth'].get('cookie'):
            logger.error("Cookie未配置")
            return {"success": False, "result": "Cookie未配置"}
        if not roomid:
            logger.error("直播间ID不能为空")
            return {"success": False, "result": "直播间ID不能为空"}
        url = 'https://api.live.bilibili.com/msg/send'
        data = {
            'color': config['bilibili_api']['live']['danmu']['color'],
            'fontsize': config['bilibili_api']['live']['danmu']['fontsize'],
            'mode': config['bilibili_api']['live']['danmu']['mode'],
            'msg': msg,
            'rnd': str(int(time.time())),
            'roomid': roomid,
            'bubble': config['bilibili_api']['live']['danmu']['bubble'],
            'csrf_token': config['bilibili_api']['auth']['csrf_token'],
            'csrf': config['bilibili_api']['auth']['csrf_token']
        }
        cookie = {
            'Cookie': config['bilibili_api']['auth']['cookie']
        }
        headers = {
            'User-Agent': config['http_headers']['user_agent']
        }
        logger.info(f"发送弹幕: {msg}")
        response = requests.post(url, data=data, cookies=cookie, headers=headers)
        try:
            if response.status_code != 200:
                logger.error(f"请求失败，HTTP状态码: {response.status_code}")
                return {"success": False, "result": f"HTTP请求失败: {response.status_code}"}
            if not response.text:
                logger.error("API返回空响应")
                return {"success": False, "result": "API返回空响应"}
            response_data = response.json()
            if not isinstance(response_data, dict):
                logger.error("响应格式无效")
                return {"success": False, "result": "响应格式无效"}
            if response_data.get('code') == 0:
                logger.info("弹幕发送成功")
                return {"success": True, "result": "弹幕发送成功"}
            else:
                error_msg = response_data.get('message', '未知错误')
                logger.error(f"弹幕发送失败: {error_msg}")
                return {"success": False, "result": f"弹幕发送失败: {error_msg}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return {"success": False, "result": f"请求异常: {str(e)}"}
        except ValueError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return {"success": False, "result": f"JSON解析失败: {str(e)}"}
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {"success": False, "result": f"未知错误: {str(e)}"}