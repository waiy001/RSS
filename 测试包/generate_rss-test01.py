# Description: 生成一个简单的 RSS 订阅源
import requests
from bs4 import BeautifulSoup  as bs
from feedgen.feed import FeedGenerator
url = "https://www.nature.com/search?q=vibration&order=date_desc"

# 用 requests 抓取网页
response = requests.get(url)  # 访问网页，返回内容保存到 response

# 用 BeautifulSoup 解析网页
soup = bs(response.text, 'html.parser')  # 解析 HTML，找到结构化的内容

# 打印网页标题，测试是否成功
print(soup.title.text)