import logging
from mcp.server.fastmcp import FastMCP
from utils.recipe.chinese_recipe_details import get_chinese_recipe_details

logger = logging.getLogger('中餐详细步骤')

def get_chinese_detailed_steps(mcp: FastMCP):
    @mcp.tool()
    def get_chinese_detailed_steps(url: str) -> dict:        
        """根据菜谱链接获取详细的步骤信息。
        当用户询问某中餐菜谱的详细做法步骤时，立刻使用该工具。  
        Args:
            url (str): 中餐菜谱的链接，格式可以是相对路径（如 `/recipe/107401526/`）或完整路径（如 `https://www.xiachufang.com/recipe/107401526/`）。        
        Returns:      
            dict: 包含操作结果的字典，格式为:          
                {                    
                    "success": bool,  # 是否成功                    
                    "result": dict  # 菜谱详情，包含食材、步骤和小贴士                
                }        
        """
        try:            
            logger.info(f"开始获取 {url} 的详细步骤信息")
            # 拼接基础URL            
            if not url.startswith('https://www.xiachufang.com'):                
                url = f'https://www.xiachufang.com{url}'            
            # 验证URL格式            
            import re            
            if not re.match(r'^https://www\.xiachufang\.com/recipe/\d+/', url):                
                error_msg = f'无效的菜谱链接格式: {url}'                
                logger.error(error_msg)                
                return {"success": False, "result": error_msg}            
            details = get_chinese_recipe_details(url)            
            if details:                
                logger.info("成功获取的详细步骤信息")                
                return {                    
                    "success": True,                    
                    "result": details                
                }            
            else:                
                error_msg = "获取菜谱详情失败，返回结果为空。"                
                logger.error(error_msg)                
                return {"success": False, "result": error_msg}        
        except Exception as e:            
            error_msg = f"获取详细步骤失败: {str(e)}"            
            logger.error(error_msg)
            return {"success": False, "result": error_msg}