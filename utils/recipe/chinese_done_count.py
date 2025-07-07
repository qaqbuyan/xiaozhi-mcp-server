from bs4 import BeautifulSoup

def get_chinese_done_count(r):
    stats_text = r.select_one('div.info p.stats').text.replace('\n', '').replace('\xa0', '').replace(' ', '')
    try:
        return int(stats_text.split('（')[1].split('做过')[0])
    except IndexError:
        return 0