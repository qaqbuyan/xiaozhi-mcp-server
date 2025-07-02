import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('菜谱获取')

def get_chinese_food(mcp: FastMCP):
    """注册菜谱相关工具"""
    @mcp.tool()
    def get_chinese_food(keyword: str , is_finished_dish: bool = False, page: int = 1) -> dict:
        """根据关键词获取中餐的菜（食）谱以及食材信息。
            只要是关于成品菜（成品菜、家常菜、快手菜等中餐）或者食材（中餐）的一律都调用该工具。
            比如当询问某一个材料（成品菜）或者是某（材料）道菜的可以做什么（菜）或者怎么做（包括做什么需要什么材料）时，立刻使用该工具。
        Args:
            keyword (str): 搜索关键词
            is_finished_dish (bool): 是否获取 "成品菜" ，默认为 False ，表示查询的是 "食材"
                - True: 获取做的人数最多的菜谱的做法
                - False: 只获取菜谱名称、材料和评分
            page (int): 页码，默认为1
        Returns:
            dict: 包含操作结果的字典，格式为:
                {
                    "success": bool,  # 是否成功
                    "result": list[dict]  # 菜谱列表，每个元素包含:
                        # 'description': 菜谱名称描述
                        # 'type': 当前类型
                        # 'page': 当前页码，下一次翻页时加 1 即可获取新的
                        # 'ingredients': list[str]  # 材料列表，格式为 "材料名称\t用量"
                        # 'steps': list[str]  # 做法步骤列表，格式为 "步骤1、步骤2、步骤3"，用户询问时完整的将该内容进行返回
                        # 'tips': list[str]  # 小贴士
                        # 'info': str  # 评分以及多少人做过这个菜，格式为 "综合评分8.2（31做过）" （）里面的数字表示做过这个菜的人数而不是评分
                }
        """
        try:
            query_type = "菜品" if is_finished_dish else "材料"
            logger.info(f"开始获取(中餐)关键词 {keyword} 的 {query_type} 信息" + (f"，页码: {page}" if page else ""))
            url = f'https://www.xiachufang.com/search/?keyword={keyword}&cat=1001'
            if page and page != 1:
                url += f'&page={page}'
            headers = {
                "User-Agent": load_config()['http_headers']['user_agent']
            }
            def get_recipe_details(url):
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    ingredients = []
                    for row in soup.select('table.ings tr'):
                        name = row.select_one('td.name').get_text(strip=True)
                        unit = row.select_one('td.unit').get_text(strip=True)
                        ingredients.append(f"{name}\t{unit}")
                    steps = []
                    for step in soup.select('div.steps p'):
                        steps.append(step.get_text(strip=True))
                    tips = []
                    tips_section = soup.select_one('div.tip-container')
                    if tips_section:
                        tip_content = tips_section.select_one('div.tip').get_text(strip=True)
                        tips = [line.strip() for line in tip_content.split('<br>') if line.strip()]
                    return {
                        'ingredients': ingredients,
                        'steps': steps,
                        'tips': tips
                    }
                except Exception as e:
                    logger.error(f"获取菜谱详情失败: {str(e)}")
                    return None
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            recipe_list = soup.select('div.normal-recipe-list ul.list li div.recipe')
            if is_finished_dish:
                def get_done_count(r):
                    stats_text = r.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                    try:
                        return int(stats_text.split('（')[1].split('做过')[0])
                    except IndexError:
                        return 0
                recipe = max(recipe_list, key=get_done_count)
                link = 'https://www.xiachufang.com' + recipe.select_one('a')['href']
                details = get_recipe_details(link)
                result = {
                    'description': recipe.select_one('p.name a').get_text(strip=True),
                    'type': '成品菜',
                    'page': page,
                    'ingredients': [ing.get_text(strip=True) for ing in recipe.select('p.ing a')] + 
                        [span.get_text(strip=True) for span in recipe.select('p.ing span')],
                    'steps': details['steps'] if details else [],
                    'tips': details['tips'] if details and details['tips'] else None,
                    'info': recipe.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                }
                logger.info(f"成功获取(中餐)关键词 {keyword} 的成品菜做法")
                logger.info(f"获取到的菜谱: {result}")
                return {
                    "success": True,
                    "result": result
                }
            else:
                result = []
                for recipe in recipe_list:
                    name = recipe.select_one('p.name a').get_text(strip=True)
                    ingredients = [ing.get_text(strip=True) for ing in recipe.select('p.ing a')] + \
                        [span.get_text(strip=True) for span in recipe.select('p.ing span')]
                    result.append({
                        'description': name,
                        'ingredients': ingredients,
                        'info': recipe.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', '')
                    })
                logger.info(f"成功获取(中餐)关键词 {keyword} 的 {len(result)} 条食材信息")
                logger.info(f"获取到的菜谱: {result}")
                return {
                    "success": True,
                    'type': '食材',
                    'page': page,
                    "result": result
                }
        except Exception as e:
            error_msg = f"获取菜谱失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}