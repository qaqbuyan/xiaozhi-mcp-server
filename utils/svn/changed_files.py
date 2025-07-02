import logging
import subprocess
import xml.etree.ElementTree as ET
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('查询SVN修改文件')

def query_svn_changed_files(mcp: FastMCP):
    """查询文件日志"""
    @mcp.tool()
    def query_svn_changed_files(revision: int) -> dict:
        """查询特定版本中修改的文件列表
        Args:
            revision: 要查询的版本号(必须为正整数)
        """
        try:
            logger.info(f"开始查询版本 {revision} 的修改文件")
            if not isinstance(revision, int) or revision <= 0:
                error_msg = "版本号必须为正整数"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            svn_config = load_config()['svn']
            repository_url = svn_config['repo_url']
            username = svn_config['username']
            password = svn_config['password']
            cmd = [
                'svn',
                'log',
                repository_url,
                '-r',
                str(revision),
                '--username', username,
                '--password', password,
                '--no-auth-cache',
                '--xml',
                '-v'
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
            paths = log_entry.find('paths')
            changed_files = []
            for path in paths.findall('path'):
                file_info = {
                    'path': path.text,
                    'action': path.attrib['action'],  # A:添加, M:修改, D:删除
                    'kind': path.attrib.get('kind', 'file')  # file/dir
                }
                changed_files.append(file_info)
            # 统计不同类型修改的文件数量
            modified_count = 0
            added_count = 0
            deleted_count = 0
            directories = set()
            for file_info in changed_files:
                if file_info['action'] == 'M':
                    modified_count += 1
                elif file_info['action'] == 'A':
                    added_count += 1
                elif file_info['action'] == 'D':
                    deleted_count += 1
                # 提取主目录
                path_parts = file_info['path'].split('/')
                if len(path_parts) > 1:
                    directories.add(path_parts[1])  # 假设主目录是第二级目录
            # 确定主要修改目录
            main_directory = directories.pop() if directories else "根目录"
            result = {
                "modified": modified_count,
                "added": added_count,
                "deleted": deleted_count,
                "main_directory": main_directory
            }
            logger.info("成功获取版本修改的文件信息")
            logger.info(f"返回信息: {result}")
            return {
                "success": True,
                "result": result
            }
        except subprocess.CalledProcessError as e:
            if "No such revision" in e.stderr:
                error_msg = f"版本 {revision} 不存在"
                logger.error(error_msg)
                return {"success": False, "result": error_msg}
            logger.error(f"SVN命令执行失败: {e.stderr}")
            return {"success": False, "result": str(e.stderr)}
        except Exception as e:
            logger.error(f"获取修改文件失败: {str(e)}")
            return {"success": False, "result": str(e)}