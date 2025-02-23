from bs4 import BeautifulSoup as bs
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

url = "https://www.nature.com/search?q=metamaterial&order=date_desc"
response = requests.get(url)
soup = bs(response.text, 'html.parser')

fg = FeedGenerator()
fg.title('Nature metamaterial RSS')
fg.link(href=url, rel='alternate')
fg.description('Latest metamaterial articles from Nature')

articles = soup.select('article')  # 根据 Nature 页面调整选择器
for article in articles:  # 抓取整页所有文章
    fe = fg.add_entry()
    title = article.select_one('h3.c-card__title a')  # 更新标题选择器
    link = article.select_one('h3.c-card__title a')  # 更新链接选择器
    date = article.select_one('time')  # 保持日期选择器
    summary = article.select_one('div.c-card__summary p')  # 更新摘要选择器
    authors = article.select('ul.c-author-list li span[itemprop="name"]')  # 提取作者

    if title and link:
        fe.title(title.text.strip())
        fe.link({'href': 'https://www.nature.com' + link['href']})#href属性值是相对链接，需要拼接完整链接，link['href']是link的href
    if date:
        dt_str = date['datetime']  # 比如 "2025-02-21"
        print("调试：日期时间字符串 =", dt_str)  # 打印日期时间，确认格式
        dt = datetime.strptime(dt_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        fe.pubDate(dt)
    if summary:
        fe.description(summary.text.strip())#将摘要文本设置成描述
    else:
        print("调试：未找到摘要，尝试其他选择器")  # 调试信息
        alternative_summary = article.select_one('p.summary-text') or article.select_one('.article-abstract') or article.select_one('.c-card__text')
        if alternative_summary:
            fe.description(alternative_summary.text.strip())
        else:
            fe.description('No summary')
    if authors:  # 添加作者（可选）
        author_list = ", ".join(author.text.strip() for author in authors)
        fe.author({'name': author_list})

fg.rss_file('nature_metamaterial_rss.xml')

print("RSS 文件已生成！")