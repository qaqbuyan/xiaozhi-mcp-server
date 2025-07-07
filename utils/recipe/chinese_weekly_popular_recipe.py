import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config
from mcp.server.fastmcp import FastMCP
from utils.recipe.chinese_done_count import get_chinese_done_count
from utils.recipe.chinese_recipe_details import get_chinese_recipe_details

logger = logging.getLogger('本周中餐热门菜谱')

def get_chinese_weekly_popular_recipes(mcp: FastMCP):
    @mcp.tool()
    def get_chinese_weekly_popular_recipes(get_most_done: bool = False, page: int = 1) -> dict:
        """获取本周最受欢迎的中餐菜品。
        当用户询问“本周最受欢迎的中餐菜品”，“今天吃什么”或者“推荐中餐菜品”时，立刻使用该工具。
        Args:
            get_most_done (bool): 默认为False，表示获取菜谱列表；设为True时，表示获取做过最多的一个菜。
            page (int): 页码，默认等于1，如果等于1就不带page请求参数。
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": list[dict]  # 菜谱列表，每个元素包含:
                        # 'description': 菜谱名称描述
                        # 'ingredients': list[str]  # 材料列表
                        # 'info': str  # 评分以及多少人做过这个菜
                        # 'link': str  # 步骤链接
                }
        """
        try:
            base_url = 'https://www.xiachufang.com/explore/'
            if page != 1:
                url = f'{base_url}?page={page}'
            else:
                url = base_url
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            logger.info(f"开始获取本周热门菜谱，页码: {page}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            recipe_list = soup.select('div.normal-recipe-list ul.list li div.recipe')
            if get_most_done:
                recipe = max(recipe_list, key=get_chinese_done_count)
                link = 'https://www.xiachufang.com' + recipe.select_one('a')['href']
                details = get_chinese_recipe_details(link)
                result = {
                    'description': recipe.select_one('p.name a').get_text(strip=True),
                    'type': '成品菜',
                    'page': page,
                    'ingredients': [f'{ing.get_text(strip=True)}：{span.get_text(strip=True)}' if span.get_text(strip=True) else ing.get_text(strip=True) for ing, span in zip(recipe.select('p.ing a'), recipe.select('p.ing span'))] + 
                        [span.get_text(strip=True) for span in recipe.select('p.ing span') if not span.find_previous('a')],
                    'steps': details['steps'] if details else [],
                    'tips': details['tips'] if details and details['tips'] else None,
                    'info': recipe.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                }
                logger.info(f"获取到的(中餐)菜谱详细信息: {result}")
                return {
                    "success": True,
                    "result": result
                }
            else:
                result = []
                for recipe in recipe_list:
                    name = recipe.select_one('p.name a').get_text(strip=True)
                    link = recipe.select_one('p.name a')['href']
                    ingredients = [ing.get_text(strip=True) for ing in recipe.select('p.ing a')] + \
                        [span.get_text(strip=True) for span in recipe.select('p.ing span')]
                    result.append({
                        'description': name,
                        'ingredients': ingredients,
                        'info': recipe.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', ''),
                        'link': link
                    })
            logger.info(f"成功获取 {len(result)} 条本周热门菜谱信息")
            logger.info(f"获取到的(中餐)菜谱信息: {result}")
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            error_msg = f"获取本周热门菜谱失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}