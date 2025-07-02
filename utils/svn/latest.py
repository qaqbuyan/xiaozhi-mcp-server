import logging
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('最后SVN日志')

def get_svn_logge_latest(mcp: FastMCP):
    """查询最新日志"""
    @mcp.tool()
    def get_svn_logge_latest():
        """获取SVN仓库的最后一次更新日志 ,当查询最后更新的仓库信息或者最新提交的代码时，立刻使用该工具。"""
        try:
            logger.info("开始获取最新SVN日志...")
            svn_config = load_config()['svn']
            repository_url = svn_config['repo_url']
            username = svn_config['username']
            password = svn_config['password']
            cmd = [
                'svn',
                'info',
                repository_url,
                '--show-item',
                'last-changed-revision', 
                '--username',
                username,
                '--password',
                password,
                '--no-auth-cache'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            latest_rev = int(result.stdout.strip())
            logger.info(f"获取到最新版本号: {latest_rev}")
            cmd = [
                'svn',
                'log',
                repository_url,
                '-r',
                str(latest_rev), 
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
            log_entry = root.find('logentry')
            from datetime import datetime
            date_obj = datetime.strptime(log_entry.find('date').text, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date_obj.strftime("%Y年%m月%d日%H:%M:%S")
            msg_content = log_entry.find('msg').text.replace('\n', ' ').strip()
            formatted_result = f"最新版本号：{log_entry.attrib['revision']}，更新时间：{formatted_date}，更新内容：{msg_content}"
            logger.info(f"发送消息: {formatted_result}")
            return {
                "success": True,
                "result": formatted_result
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"SVN命令执行失败: {e.stderr}")
            return {"success": False, "result": str(e.stderr)}
        except Exception as e:
            logger.error(f"获取最新日志失败: {str(e)}")
            return {"success": False, "result": str(e)}