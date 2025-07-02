import logging
import subprocess
import xml.etree.ElementTree as ET
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

logger = logging.getLogger('查询时间SVN日志')

def query_svn_time_logger(mcp: FastMCP):
    """查询日期日志"""
    @mcp.tool()
    def query_svn_time_logger(date_str: str) -> dict:
        """根据日期查询SVN仓库的更新日志, 当查询某一天的仓库信息或者某一天提交的代码时，立刻使用该工具。
        args:
            date_str: 日期字符串，格式为'YYYY年MM月DD日' 必须填写, 例如：2024年01月01日
        注意:
            1. 日期格式必须为'YYYY年MM月DD日'，且不能超过当前日期。
            2. 不能传入这样子的日期格式，例如：２０２３年０４月２５日
            2. 该函数会返回一个包含提交日志的列表，每个日志是一个字典，包含以下键值对:
                - revision: 版本号
                - author: 提交者
                - date: 提交时间
        """
        try:
            logger.info(f"开始查询日期 {date_str} 的SVN日志")
            try:
                datetime.strptime(date_str, "%Y年%m月%d日")
            except ValueError:
                logger.error(f"日期格式错误: {date_str}")
                return {
                    "success": False,
                    "result": "日期格式错误，请使用'YYYY年MM月DD日'格式"
                }
            svn_config = load_config()['svn']
            repository_url = svn_config['repo_url']
            username = svn_config['username']
            password = svn_config['password']
            date_obj = datetime.strptime(date_str, "%Y年%m月%d日")
            start_date = date_obj.strftime("%Y-%m-%d")
            end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
            cmd = [
                'svn',
                'log', 
                repository_url, 
                '-r',
                f'{{{start_date}}}:{{{end_date}}}',
                '--username',
                username,
                '--password',
                password,
                '--no-auth-cache',
                '--xml'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            root = ET.fromstring(result.stdout)
            log_entries = root.findall('logentry')
            logger.info(f"原始获取 {len(log_entries)} 条SVN日志")
            filtered_entries = []
            target_date = datetime.strptime(date_str, "%Y年%m月%d日").date()
            for entry in log_entries:
                entry_date = datetime.strptime(entry.find('date').text, "%Y-%m-%dT%H:%M:%S.%fZ").astimezone().date()
                if entry_date == target_date:
                    filtered_entries.append(entry)
            logger.info(f"过滤后获取 {len(filtered_entries)} 条当天SVN日志")
            if not filtered_entries:
                return {
                    "success": True,
                    "result": f"{date_str} 没有更新记录"
                }
            formatted_results = []
            for entry in filtered_entries:
                date_obj = datetime.strptime(entry.find('date').text, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = date_obj.strftime("%Y年%m月%d日%H:%M:%S")
                msg_content = entry.find('msg').text.replace('\n', '').strip()
                formatted_results.append(
                    f"版本号：{entry.attrib['revision']}，更新时间：{formatted_date}，更新内容：{msg_content}"
                )
            logs = "\n".join(formatted_results)
            logger.info(f"返回数据：{logs}")
            return {
                "success": True,
                "result": logs
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"SVN命令执行失败: {e.stderr}")
            return {"success": False, "result": str(e.stderr)}
        except Exception as e:
            logger.error(f"获取日志失败: {str(e)}")
            return {"success": False, "result": str(e)}