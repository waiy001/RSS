# Description: 生成一个简单的RSS文件
import requests      
from feedgen.feed import FeedGenerator

url = "https://www.nature.com/search?q=vibration&order=date_desc"
response = requests.get(url)
fg = FeedGenerator()
fg.title('Nature Vibration RSS')
fg.link(href=url, rel='alternate')
fg.description('Latest vibration articles from Nature')
fg.rss_file('nature_vibration_rss.xml')

print("RSS 文件已生成！")