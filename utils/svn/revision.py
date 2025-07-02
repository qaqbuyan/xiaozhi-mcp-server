import logging
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('查询SVN版本')

def query_svn_revision(mcp: FastMCP):
    """查询版本日志"""
    @mcp.tool()
    def query_svn_revision(revision: int) -> dict:
        """查询特定版本的SVN仓库信息，当查询仓库某一个版本时，立刻使用该工具。
        Args:
            revision: 要查询的版本号(必须为正整数，最少为1)
        """
        try:
            logger.info(f"开始查询版本 {revision} 的SVN信息")
            if not isinstance(revision, int) or revision <= 0:
                error_msg = "版本号必须为正整数"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            svn_config = load_config()['svn']
            repository_url = svn_config['repo_url']
            username = svn_config['username']
            password = svn_config['password']
            cmd_info = [
                'svn',
                'info',
                repository_url,
                '-r', str(revision),
                '--username', username,
                '--password', password,
                '--no-auth-cache'
            ]
            try:
                subprocess.run(
                    cmd_info,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8',
                    errors='replace'
                )
            except subprocess.CalledProcessError as e:
                if "No such revision" in e.stderr:
                    error_msg = f"版本 {revision} 不存在"
                    logger.error(error_msg)
                    return {"success": False, "result": error_msg}
                raise
            cmd_log = [
                'svn',
                'log',
                repository_url,
                '-r', str(revision),
                '--username',
                username,
                '--password',
                password,
                '--no-auth-cache',
                '--xml'
            ]
            result = subprocess.run(
                cmd_log,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            root = ET.fromstring(result.stdout)
            log_entry = root.find('logentry')
            date_obj = datetime.strptime(log_entry.find('date').text, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date_obj.strftime("%Y年%m月%d日%H:%M:%S")
            msg_content = log_entry.find('msg').text.replace('\n', ' ').strip()
            result_dict = {
                'revision': int(log_entry.attrib['revision']),
                'author': log_entry.find('author').text,
                'date': formatted_date,
                'message': msg_content
            }
            logger.info(f"返回数据：{result_dict}")
            return {
                "success": True,
                "result": result_dict
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"SVN命令执行失败: {e.stderr}")
            return {"success": False, "result": str(e.stderr)}
        except Exception as e:
            logger.error(f"获取版本信息失败: {str(e)}")
            return {"success": False, "result": str(e)}