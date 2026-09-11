import os

from scrapy.crawler import CrawlerProcess

from analyzer.filter import analyze_news
from analyzer.score import calculate_score


results = []


class CollectingPipeline:

    def process_item(self, item, spider):

        results.append(dict(item))

        return item


def process_stock_news(news_list):

    processed = []

    for news in news_list:

        news = analyze_news(news)

        news = calculate_score(news)

        # 只保留与股票或行业相关的新闻
        if (
            news.get("matched_stocks")
            or news.get("matched_industries")
        ):
            processed.append(news)

    return processed


def main():

    process = CrawlerProcess({

        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        ),

        "ROBOTSTXT_OBEY": False,

        "DOWNLOAD_DELAY": 1,

        "CONCURRENT_REQUESTS": 2,

        "ITEM_PIPELINES": {
            "__main__.CollectingPipeline": 300
        },

        "LOG_LEVEL": "INFO",

        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    })


    # =========================
    # CCTV
    # =========================

    from crawler.cctv1 import Cctv1Spider
    from crawler.cctv2 import Cctv2Spider
    from crawler.cctv13 import Cctv13Spider

    process.crawl(Cctv1Spider)
    process.crawl(Cctv2Spider)
    process.crawl(Cctv13Spider)


    # =========================
    # 股票新闻
    # =========================

    from crawler.stock_news import StockNewsSpider

    process.crawl(StockNewsSpider)


    # =========================
    # 开始抓取
    # =========================

    process.start()


    print()
    print("=" * 60)
    print(f"总共抓取 {len(results)} 条新闻")
    print("=" * 60)


    if not results:

        print("没有抓取到任何新闻")

        return


    # =========================
    # 股票新闻分析
    # =========================

    stock_news = process_stock_news(results)


    print()
    print("=" * 60)
    print(
        f"股票/行业相关信息："
        f"{len(stock_news)} 条"
    )
    print("=" * 60)


    # 按重要程度排序

    stock_news.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )


    for news in stock_news[:20]:

        print()

        print(
            f"[{news.get('level')}] "
            f"{news.get('score')}分"
        )

        print(
            f"标题：{news.get('title')}"
        )

        print(
            f"股票："
            f"{', '.join("
                item['name']
                for item in news.get('matched_stocks', [])
            )}"
        )


    # =========================
    # 邮件
    # =========================

    from mailer import send_email

    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get(
        "EMAIL_RECEIVER",
        sender
    )


    if not sender:

        print("错误：没有设置 EMAIL_SENDER")

        return


    if not password:

        print("错误：没有设置 EMAIL_PASSWORD")

        return


    if not receiver:

        print("错误：没有设置 EMAIL_RECEIVER")

        return


    if stock_news:

        send_email(
            stock_news,
            sender,
            password,
            receiver
        )

    else:

        print("没有发现股票相关信息")


if __name__ == "__main__":

    main()
