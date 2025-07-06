import logging
import requests
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('汇率查询')

def get_exchange_rate(mcp: FastMCP):
    """汇率查询"""
    @mcp.tool()
    def get_exchange_rate(money: float, fromcode: str, tocode: str) -> dict:
        """根据传入的金额、源货币代码和目标货币代码获取汇率信息。
        Args:
            money (float): 要换算的金额。
            fromcode (str): 源货币代码，例如：JPY。
            tocode (str): 目标货币代码，例如：CNY。
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": dict  # 汇率信息，包含当前汇率、换算结果和更新时间
                }
        """
        try:
            logger.info(f'开始获取 {fromcode} 到 {tocode} 的汇率信息...')
            url = 'https://www.huilvbiao.com/transform'
            params = {
                'money': money,
                'fromcode': fromcode,
                'tocode': tocode
            }
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 0:
                result = {
                    "当前汇率": data['rate'],
                    "换算结果": data['result'],
                    "更新时间": data['update_time']
                }
                logger.info(f"成功获取 {fromcode} 到 {tocode} 的汇率信息")
                logger.info(f"汇率信息: {result}")
                return {"success": True, "result": result}
            else:
                error_msg = f"获取汇率失败，错误信息: {data.get('msg', '未知错误')}"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"请求出错: {e}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        except Exception as e:
            error_msg = f"获取汇率失败: {e}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}