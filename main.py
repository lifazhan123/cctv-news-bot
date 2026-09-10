import os
import sys
from scrapy.crawler import CrawlerProcess

results = []


class CollectingPipeline:
    def process_item(self, item, spider):
        results.append(dict(item))
        return item


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 2,
        'ITEM_PIPELINES': {'main.CollectingPipeline': 300},
        'LOG_LEVEL': 'INFO',
    })

    from crawler.cctv1 import Cctv1Spider
    from crawler.cctv13 import Cctv13Spider
    from crawler.cctv2 import Cctv2Spider

    process.crawl(Cctv1Spider)
    process.crawl(Cctv13Spider)
    process.crawl(Cctv2Spider)
    process.start()

    print(f"共抓取 {len(results)} 条新闻")

    from mailer import send_email, filter_news
    filtered = filter_news(results)
    print(f"过滤后剩余 {len(filtered)} 条")

    if filtered:
        sender = os.environ.get('EMAIL_SENDER')
        password = os.environ.get('EMAIL_PASSWORD')
        receiver = os.environ.get('EMAIL_RECEIVER', sender)
        send_email(filtered, sender, password, receiver)
    else:
        print("没有符合条件的新闻")


if __name__ == '__main__':
    main()
