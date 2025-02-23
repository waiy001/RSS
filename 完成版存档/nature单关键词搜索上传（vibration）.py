from bs4 import BeautifulSoup as bs
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import schedule
import time
import os

def generate_rss():
    url = "https://www.nature.com/search?q=vibration&order=date_desc"
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')

    fg = FeedGenerator()
    fg.title('Nature Vibration RSS')
    fg.link(href=url, rel='alternate')
    fg.description('Latest vibration articles from Nature')

    # 抓取所有文章，并按日期升序排序（新文章在前面）
    articles = soup.select('article')  # 根据 Nature 页面调整选择器
    articles = list(reversed(articles))  # 反转顺序，新文章在前

    for article in articles[:54]:  # 限制 54 个 <item>
        fe = fg.add_entry()
        title = article.select_one('h3.c-card__title a')  # 更新标题选择器
        link = article.select_one('h3.c-card__title a')  # 更新链接选择器
        date = article.select_one('time')  # 保持日期选择器
        summary = article.select_one('div.c-card__summary p')  # 更新摘要选择器
        authors = article.select('ul.c-author-list li span[itemprop="name"]')  # 提取作者

        if title and link:
            fe.title(title.text.strip())
            fe.link({'href': 'https://www.nature.com' + link['href']})  # 拼接完整链接
        if date:
            date_str = date['datetime']  # 比如 "2025-02-21"
            print("调试：日期时间字符串 =", date_str)  # 打印日期时间，确认格式
            dt = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            fe.pubDate(dt)
        if summary:
            fe.description(summary.text.strip())  # 将摘要文本设置成描述
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

    # 自定义输出带换行符的 XML
    with open('nature_vibration_rss.xml', 'w', encoding='utf-8') as f:
        f.write(fg.rss_str(pretty=True).decode('utf-8'))  # 使用 pretty=True 格式化输出
    print("RSS 文件已生成！")
    # 上传到 GitHub Pages（手动或用 Git 脚本）
    # 示例：用 os.system 调用 git 命令（需配置 Git 和 GitHub）
    os.system("git add nature_vibration_rss.xml")
    os.system('git commit -m "Update nature_vibration_rss.xml with latest changes"')  # 使用双引号
    os.system("git push origin main")  # 假设主分支为 main
    print("RSS 文件已更新到 GitHub Pages")

# 定时任务：每10分钟运行一次（可调整为每小时）
schedule.every(10).minutes.do(generate_rss)

# 运行定时任务
if __name__ == "__main__":
    generate_rss()  # 立即运行一次
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次