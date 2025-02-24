from bs4 import BeautifulSoup as bs
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import schedule
import time
import os
import certifi

def generate_rss():
    # 定义学科列表
    subjects = ['chemistry', 'engineering', 'materials-science', 'nanoscience-and-technology', 'optics-and-photonics', 'physics']
    base_url_template = "https://www.nature.com/search?q=%28%22topological%22+OR+%22phononic%22+OR+%22Valley+Hall%22%29+-%28%22metamaterials%22+OR+%22metamaterial%22+OR+%22metasurface%22+OR+%22metasurfaces%22%29&article_type=research%2C+reviews&subject={}&order=date_desc&date_range=2023-2025&journal=lsa%2Cnature%2Cnchem%2Cncomms%2Cnatelectron%2Cnmat%2Cnnano%2Cnphoton%2Cnphys%2Cnatrevphys%2Cnpjacoustics%2Cnpjqi%2Csrep&article_type=research%2C+reviews&page={}"
    all_articles = []  # 用于存储所有学科的文章

    # 遍历每个学科，抓取前三页（page=1, page=2, page=3）
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36'}
    for subject in subjects:
        for page in range(1, 2):  # range(1, 4) 生成 1、2、3
            url = base_url_template.format(subject, page)
            try:
                response = requests.get(url, headers=headers, verify=certifi.where(), timeout=10)
                response.raise_for_status()
                soup = bs(response.text, 'html.parser')

                # 抓取当前页的文章
                articles = soup.select('article')
                if not articles:  # 如果页面无文章，提前跳出（理论上 page=3 仍可能有内容）
                    break
                all_articles.extend(articles)
                time.sleep(5)  # 增加间隔避免反爬
            except requests.exceptions.RequestException as e:
                print(f"学科 {subject}，页面 {page} 请求错误：{e}")
                continue

    # 去重（基于 URL 链接，避免重复文章）
    unique_articles = []
    seen_urls = set()
    for article in all_articles:
        link = article.select_one('h3.c-card__title a')
        if link and 'href' in link.attrs:
            url = 'https://www.nature.com' + link['href']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

    # 按日期升序排序（旧文章在前）
    unique_articles.sort(key=lambda x: datetime.strptime(x.select_one('time')['datetime'], '%Y-%m-%d'), reverse=False)

    fg = FeedGenerator()
    fg.title('Nature Topological Phononic Multi-Discipline RSS')
    fg.link(href=base_url_template.format(subjects[0], 1), rel='alternate')  # 使用第一个学科的第一页 URL 作为主链接
    fg.description('Latest topological and phononic articles from Nature across chemistry, engineering, materials-science, nanoscience-and-technology, optics-and-photonics, physics (first 3 pages per subject, 2023-2025, research and reviews)')

    for article in unique_articles:
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
    with open('nature_tp_pt_vh_3.xml', 'w', encoding='utf-8') as f:
        f.write(fg.rss_str(pretty=True).decode('utf-8'))  # 使用 pretty=True 格式化输出
    print("Nature Topological Phononic Multi-Discipline RSS 文件已生成！")
    # 上传到 GitHub Pages（手动或用 Git 脚本）
    os.system("git add nature_tp_pt_vh_3.xml")
    os.system('git commit -m "Update nature_tp_pt_vh_3.xml with latest changes (first 3 pages per subject, 2023-2025, research and reviews, multiple disciplines)"')
    os.system("git push origin main")  # 假设主分支为 main
    print("Nature Topological Phononic Multi-Discipline RSS 文件已更新到 GitHub Pages")

# 定时任务：每12小时运行一次（可调整为每小时）
schedule.every(12).hours.do(generate_rss)

# 运行定时任务
if __name__ == "__main__":
    generate_rss()  # 立即运行一次
    while True:
        schedule.run_pending()
        time.sleep(600)  # 每10分钟检查一次