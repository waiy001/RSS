from bs4 import BeautifulSoup as bs
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import schedule
import time
import os
import certifi

def generate_rss():
    base_url = "https://www.nature.com/search?q=%28%22vibration%22+OR+%22vibrations%22%29+AND+%28%22metamaterial%22+OR+%22metamaterials%22%29&order=date_desc&page={}"
    all_articles = []

    # 循环抓取多页内容，直到无结果
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36'}
    page = 1
    while True:
        url = base_url.format(page)
        try:
            response = requests.get(url, headers=headers, verify=certifi.where(), timeout=10)
            response.raise_for_status()
            soup = bs(response.text, 'html.parser')

            # 抓取当前页的文章
            articles = soup.select('article')
            if not articles:  # 如果页面无文章，停止循环
                break
            all_articles.extend(articles)
            page += 1  # 进入下一页
            time.sleep(5)  # 增加间隔避免反爬
        except requests.exceptions.RequestException as e:
            print(f"页面 {page} 请求错误：{e}")
            break

    # 按日期升序排序（旧文章在前）
    all_articles.sort(key=lambda x: datetime.strptime(x.select_one('time')['datetime'], '%Y-%m-%d'), reverse=False)

    fg = FeedGenerator()
    fg.title('Nature Vibration Metamaterials RSS')
    fg.link(href=base_url.format(1), rel='alternate')  # 使用第一页 URL 作为主链接
    fg.description('Latest articles from Nature with both "vibration/vibrations" and "metamaterial/metamaterials"')

    # 遍历文章（已按日期升序排序）
    for article in all_articles:
        fe = fg.add_entry()
        title = article.select_one('h3.c-card__title a')
        link = article.select_one('h3.c-card__title a')
        date = article.select_one('time')
        summary = article.select_one('div.c-card__summary p')
        authors = article.select('ul.c-author-list li span[itemprop="name"]')

        if title and link:
            fe.title(title.text.strip())
            fe.link({'href': 'https://www.nature.com' + link['href']})
        if date:
            date_str = date['datetime']  # 比如 "2025-02-21"
            print("调试：日期时间字符串 =", date_str)  # 打印日期时间，确认格式
            dt = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            fe.pubDate(dt)
        if summary:
            fe.description(summary.text.strip())
        else:
            alternative_summary = article.select_one('p.summary-text') or article.select_one('.article-abstract') or article.select_one('.c-card__text')
            if alternative_summary:
                fe.description(alternative_summary.text.strip())
            else:
                fe.description('No summary')
        if authors:
            author_list = ", ".join(author.text.strip() for author in authors)
            fe.author({'name': author_list})

    # 自定义输出带换行符的 XML
    with open('nature_vib_meta_ALL.xml', 'w', encoding='utf-8') as f:
        f.write(fg.rss_str(pretty=True).decode('utf-8'))  # 使用 pretty=True 格式化输出
    print("Nature Vibration Metamaterials RSS 文件已生成！")
    # 上传到 GitHub Pages（手动或用 Git 脚本）
    os.system("git add nature_vib_meta_ALL.xml")
    os.system('git commit -m "Update nature_vib_meta_ALL.xml with latest changes"')
    os.system("git push origin main")  # 假设主分支为 main
    print("Nature Vibration Metamaterials RSS 文件已更新到 GitHub Pages")

# 定时任务：每12小时运行一次（可调整为每小时）
schedule.every(12).hours.do(generate_rss)

# 运行定时任务
if __name__ == "__main__":
    generate_rss()  # 立即运行一次
    while True:
        schedule.run_pending()
        time.sleep(300)  # 每 5 分钟检查一次，减少频率