import os
from collections import Counter

from scrapy.crawler import CrawlerProcess

from analyzer.filter import analyze_news
from analyzer.score import calculate_score


results = []


class CollectingPipeline:

    def process_item(self, item, spider):

        results.append(
            dict(item)
        )

        return item


def process_stock_news(news_list):

    processed = []

    for news in news_list:

        news = analyze_news(news)

        news = calculate_score(news)

        # =================================
        # 股票 / 行业 / 军事
        # 任意一个匹配就进入邮件
        # =================================

        if (
            news.get("matched_stocks")
            or news.get("matched_industries")
            or news.get("matched_military_keywords")
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

    # =====================================
    # CCTV-1
    # =====================================

    print()
    print("=" * 60)
    print("开始抓取央视新闻")
    print("=" * 60)

    from crawler.cctv1 import Cctv1Spider

    process.crawl(
        Cctv1Spider
    )

    # =====================================
    # CCTV-2
    # =====================================

    from crawler.cctv2 import Cctv2Spider

    process.crawl(
        Cctv2Spider
    )

    # =====================================
    # CCTV-13
    # =====================================

    from crawler.cctv13 import Cctv13Spider

    process.crawl(
        Cctv13Spider
    )

    # =====================================
    # 股票相关新闻
    # =====================================

    print()
    print("=" * 60)
    print("开始抓取股票相关新闻")
    print("=" * 60)

    from crawler.stock_news import StockNewsSpider

    process.crawl(
        StockNewsSpider
    )

    # =====================================
    # 央视军事
    # =====================================

    print()
    print("=" * 60)
    print("开始抓取央视军事相关新闻")
    print("=" * 60)

    from crawler.military_news import MilitaryNewsSpider

    process.crawl(
        MilitaryNewsSpider
    )

    # =====================================
    # 开始执行
    # =====================================

    process.start()

    print()
    print("=" * 60)
    print("全部新闻抓取完成")
    print("=" * 60)

    print(
        f"总共抓取：{len(results)} 条新闻"
    )

    # =====================================
    # 来源统计
    # =====================================

    source_counter = Counter(
        news.get(
            "source",
            "未知来源"
        )
        for news in results
    )

    print()
    print("=" * 60)
    print("各新闻来源抓取统计")
    print("=" * 60)

    for source, count in source_counter.items():

        print(
            f"{source}：{count} 条"
        )

    # =====================================
    # 没有数据
    # =====================================

    if not results:

        print()
        print(
            "❌ 没有抓取到任何新闻"
        )

        return

    # =====================================
    # 分析
    # =====================================

    print()
    print("=" * 60)
    print("开始分析股票、行业及军事信息")
    print("=" * 60)

    stock_news = process_stock_news(
        results
    )

    print(
        f"股票/行业/军事相关信息："
        f"{len(stock_news)} 条"
    )

    # =====================================
    # 排序
    # =====================================

    stock_news.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True
    )

    # =====================================
    # 控制台输出
    # =====================================

    print()
    print("=" * 60)
    print("今日重点股票/行业/军事新闻")
    print("=" * 60)

    for index, news in enumerate(
        stock_news[:20],
        1
    ):

        print()

        print(
            f"【{index}】 "
            f"{news.get('level', '')}"
        )

        print(
            f"评分："
            f"{news.get('score', 0)}"
        )

        print(
            f"标题："
            f"{news.get('title', '')}"
        )

        # 股票
        matched_names = [
            item["name"]
            for item in news.get(
                "matched_stocks",
                []
            )
        ]

        if matched_names:

            print(
                "涉及股票："
                + "、".join(
                    matched_names
                )
            )

        else:

            print(
                "涉及股票：无"
            )

        # 行业
        matched_industries = news.get(
            "matched_industries",
            []
        )

        if matched_industries:

            print(
                "涉及行业："
                + "、".join(
                    matched_industries
                )
            )

        else:

            print(
                "涉及行业：无"
            )

        # 军事关键词
        military_keywords = news.get(
            "matched_military_keywords",
            []
        )

        if military_keywords:

            print(
                "军事关键词："
                + "、".join(
                    military_keywords
                )
            )

        # 来源
        print(
            f"来源："
            f"{news.get('source', '')}"
        )

        # 链接
        print(
            f"链接："
            f"{news.get('link', '')}"
        )

        # 原因
        reasons = news.get(
            "score_reasons",
            []
        )

        if reasons:

            print(
                "关注原因："
                + "、".join(
                    reasons
                )
            )

    # =====================================
    # 没有相关信息
    # =====================================

    if not stock_news:

        print()
        print("=" * 60)
        print(
            "今天没有发现与你关注股票、"
            "行业或军事信息相关的新闻"
        )
        print("=" * 60)

        return

    # =====================================
    # 发送邮件
    # =====================================

    print()
    print("=" * 60)
    print("准备发送邮件")
    print("=" * 60)

    from mailer import send_email

    sender = os.environ.get(
        "EMAIL_SENDER"
    )

    password = os.environ.get(
        "EMAIL_PASSWORD"
    )

    receiver = os.environ.get(
        "EMAIL_RECEIVER",
        sender
    )

    if not sender:

        print(
            "❌ 错误：没有设置 EMAIL_SENDER"
        )

        return

    if not password:

        print(
            "❌ 错误：没有设置 EMAIL_PASSWORD"
        )

        return

    if not receiver:

        print(
            "❌ 错误：没有设置 EMAIL_RECEIVER"
        )

        return

    try:

        send_email(
            stock_news,
            sender,
            password,
            receiver
        )

        print()
        print("=" * 60)
        print(
            "✅ 股票新闻邮件发送完成"
        )
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print(
            "❌ 邮件发送失败"
        )
        print("=" * 60)

        print(
            f"错误信息：{e}"
        )


if __name__ == "__main__":
    main()
