import os
from scrapy.crawler import CrawlerProcess

# 保存所有爬虫抓取到的新闻
results = []


class CollectingPipeline:
    """
    Scrapy 数据管道。

    每抓到一条新闻，就把新闻保存到 results。
    """

    def process_item(self, item, spider):

        results.append(dict(item))

        print(
            f"[Pipeline] 收到新闻："
            f"{item.get('source', '')} - "
            f"{item.get('title', '')[:50]}"
        )

        return item


def main():

    process = CrawlerProcess({
        'USER_AGENT': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 '
            '(KHTML, like Gecko) '
            'Chrome/153.0.0.0 Safari/537.36'
        ),

        'ROBOTSTXT_OBEY': False,

        'DOWNLOAD_DELAY': 1,

        'CONCURRENT_REQUESTS': 2,

        # 关键：
        # main.py 是通过 python main.py 启动的，
        # 此时当前模块名称是 __main__
        'ITEM_PIPELINES': {
            '__main__.CollectingPipeline': 300
        },

        'LOG_LEVEL': 'INFO',

        # 解决 Scrapy 2.11 的指纹算法警告
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    })

    # 导入三个爬虫
    from crawler.cctv1 import Cctv1Spider
    from crawler.cctv2 import Cctv2Spider
    from crawler.cctv13 import Cctv13Spider

    # 启动 CCTV-1
    process.crawl(Cctv1Spider)

    # 启动 CCTV-2
    process.crawl(Cctv2Spider)

    # 启动 CCTV-13
    process.crawl(Cctv13Spider)

    # 开始执行
    process.start()

    # =========================
    # 爬虫执行结束
    # =========================

    print()
    print('=' * 60)
    print(f'共抓取 {len(results)} 条新闻')
    print('=' * 60)

    # 如果没有新闻，直接结束
    if not results:

        print('没有抓取到任何新闻')

        return

    # =========================
    # 新闻过滤
    # =========================

    from mailer import send_email, filter_news

    filtered = filter_news(results)

    print(f'过滤后剩余 {len(filtered)} 条')

    # =========================
    # 发送邮件
    # =========================

    if filtered:

        sender = os.environ.get('EMAIL_SENDER')

        password = os.environ.get('EMAIL_PASSWORD')

        receiver = os.environ.get(
            'EMAIL_RECEIVER',
            sender
        )

        # 检查邮箱配置
        if not sender:
            print('错误：没有设置 EMAIL_SENDER')

            return

        if not password:
            print('错误：没有设置 EMAIL_PASSWORD')

            return

        if not receiver:
            print('错误：没有设置 EMAIL_RECEIVER')

            return

        send_email(
            filtered,
            sender,
            password,
            receiver
        )

    else:

        print('没有符合条件的新闻')


if __name__ == '__main__':
    main()
