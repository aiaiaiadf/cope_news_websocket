import re
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from common.utils import format_date


# 从新闻链接中提取网站名称
def extract_webset(src):
    match = re.search(r'www\.([^.]+)\.com', src)
    if match:
        return match.group(1)
    else:
        return "Unknown"
    

# 解析新闻页面内容
async def parse_news_page(url_base,html):
    # url_base https://www.panewslab.com
    soup = BeautifulSoup(html, 'html.parser')
    news_data = []

    articles = soup.find_all('div', class_='item')

    if not articles:
        print("No articles found on this page.")
        return  news_data

    for article in articles:
        title_tag = article.find('a', class_='n-title')
        title = title_tag.text.strip() if title_tag else "No Title"

        content_tag = article.find('p')
        content = content_tag.text.strip() if content_tag else "No Content"

        pubtime_tag = article.find('div', class_='pubtime')
        pubtime = pubtime_tag.text.strip() if pubtime_tag else "00:00"

        news_data.append({
            "date": format_date(pubtime),
            "title": title,
            "content": content,
            # "webset": extract_webset(title_tag['href'] if title_tag and title_tag.has_attr('href') else ""),
            "webset": url_base.split(".")[1],
            "src": f"{url_base}{title_tag['href'] if title_tag and title_tag.has_attr('href') else ''}"
        })

    return news_data



