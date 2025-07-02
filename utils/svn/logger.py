import logging
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('查询SVN日志')

def query_svn_logger(mcp: FastMCP):
    """查询版本到版本日志"""
    @mcp.tool()
    def query_svn_logger(start_revision: int = 1, end_revision: int = 10) -> dict:
        """用于获取查询本人的SVN仓库获取提交日志。当查询仓库时，立刻使用该工具。
        Args:
            start_revision: 起始版本号 必须填写
            end_revision: 结束版本号 必须填写
        注意:
            1. 版本号必须为正整数，且start_revision <= end_revision 并且这两个相差不能超过20，可以等于20。
            2. 版本号不能超过仓库的最大版本号。
            3. 该函数会返回一个包含提交日志的列表，每个日志是一个字典，包含以下键值对:
                - revision: 版本号
                - author: 提交者
                - date: 提交时间
                - message: 提交信息
        """
        logger.info(f"开始获取SVN日志，版本范围：{start_revision} - {end_revision}")
        if not isinstance(start_revision, int) or not isinstance(end_revision, int):
            error_msg = "版本号必须为正整数"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        if start_revision > end_revision:
            error_msg = "起始版本号不能大于结束版本号"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        if (end_revision - start_revision) > 20:
            error_msg = "版本号范围不能超过20个版本"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        svn_info = load_config().get('svn', {})
        repository_url = svn_info.get('repo_url')
        username = svn_info.get('username')
        password = svn_info.get('password')
        if not all([repository_url, username, password]):
            error_msg = "配置文件中缺少必要的SVN信息"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
        cmd = [
            'svn',
            'log',
            repository_url,
            '--xml',
            '--username',
            username,
            '--password',
            password
        ]
        cmd.extend(['-r', f'{start_revision}:{end_revision}'])
        try:
            logger.info(f"执行SVN命令")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            if not result.stdout:
                error_msg = f"SVN命令未返回任何输出，可能原因：1. 版本范围{start_revision}-{end_revision}无效。2. 仓库地址不可访问。3. 认证失败"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            root = ET.fromstring(result.stdout)
            logs = []
            for logentry in root.findall('logentry'):
                message = logentry.find('msg').text if logentry.find('msg') is not None else ''
                logs.append({
                    'revision': int(logentry.get('revision')),
                    'author': logentry.find('author').text,
                    'date': datetime.strptime(logentry.find('date').text, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y年%m月%d日%H:%M:%S'),  # 修改为中文日期格式
                    'message': message.replace('\n', '')
                })
            if len(logs) < (end_revision - start_revision + 1):
                error_msg = f"请求的版本范围({start_revision}-{end_revision})超过实际版本数量"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            logger.info(f"成功获取 {len(logs)} 条SVN日志")
            logger.info(f"返回数据：{logs}")
            return {"success": True, "result": logs}
        except subprocess.CalledProcessError as e:
            logger.error(f"SVN命令执行失败: {e.stderr}")
            return {"success": False, "result": str(e.stderr)}
        except ET.ParseError as e:
            logger.error(f"XML解析失败: {e}")
            return {"success": False, "result": str(e)}