import logging
import requests
from bs4 import BeautifulSoup
from config.loader import load_config

logger = logging.getLogger('中餐详情')

def get_chinese_recipe_details(url: str) -> dict:
    try:
        headers = {
            "User-Agent": load_config()['http_headers']['user_agent']
        }
        logger.info("开始获取中文菜谱详情...")
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
        logger.info(f"成功获取 {url} 的中文菜谱详情")
        result = {
            'ingredients': ingredients,
            'steps': steps,
            'tips': tips
        }
        logger.info(f"详情: {result}")
        return result
    except Exception as e:
        logger.error(f"获取菜谱详情失败: {str(e)}")
        return None