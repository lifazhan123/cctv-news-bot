import os

from scrapy.crawler import CrawlerProcess

from analyzer.filter import analyze_news
from analyzer.score import calculate_score


# ==========================================
# 用来保存所有爬虫抓到的新闻
# ==========================================

results = []


# ==========================================
# Scrapy Pipeline
# ==========================================

class CollectingPipeline:

    def process_item(self, item, spider):

        results.append(dict(item))

        return item


# ==========================================
# 股票新闻分析
# ==========================================

def process_stock_news(news_list):

    processed = []

    for news in news_list:

        # ----------------------------------
        # 判断涉及哪些股票、哪些行业
        # ----------------------------------

        news = analyze_news(news)

        # ----------------------------------
        # 给新闻进行重要程度评分
        # ----------------------------------

        news = calculate_score(news)

        # ----------------------------------
        # 只保留：
        # 1. 与关注股票有关
        # 2. 与关注行业有关
        # ----------------------------------

        if (
            news.get("matched_stocks")
            or news.get("matched_industries")
        ):

            processed.append(news)

    return processed


# ==========================================
# 主程序
# ==========================================

def main():

    # ======================================
    # Scrapy 配置
    # ======================================

    process = CrawlerProcess({

        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        ),

        # 不读取 robots.txt
        "ROBOTSTXT_OBEY": False,

        # 请求间隔
        "DOWNLOAD_DELAY": 1,

        # 同时请求数量
        "CONCURRENT_REQUESTS": 2,

        # 新闻收集 Pipeline
        #
        # 注意：
        # 这里必须使用 __main__
        # 不要改成 main
        #
        # 否则会出现：
        # item_scraped_count 有数据
        # 但是最后 results = 0
        #
        "ITEM_PIPELINES": {
            "__main__.CollectingPipeline": 300
        },

        "LOG_LEVEL": "INFO",

        # 消除 Scrapy 2.11 的警告
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    })


    # ======================================
    # 第一部分：央视新闻
    # ======================================

    print()
    print("=" * 60)
    print("开始抓取央视新闻")
    print("=" * 60)

    from crawler.cctv1 import Cctv1Spider
    from crawler.cctv2 import Cctv2Spider
    from crawler.cctv13 import Cctv13Spider

    process.crawl(Cctv1Spider)
    process.crawl(Cctv2Spider)
    process.crawl(Cctv13Spider)


    # ======================================
    # 第二部分：股票财经新闻
    # ======================================

    print()
    print("=" * 60)
    print("开始抓取股票相关新闻")
    print("=" * 60)

    from crawler.stock_news import StockNewsSpider

    process.crawl(StockNewsSpider)


    # ======================================
    # 开始执行所有爬虫
    # ======================================

    process.start()


    # ======================================
    # 抓取结果统计
    # ======================================

    print()
    print("=" * 60)
    print("全部新闻抓取完成")
    print("=" * 60)

    print(f"总共抓取：{len(results)} 条新闻")


    # ======================================
    # 如果什么都没有抓到
    # ======================================

    if not results:

        print()
        print("❌ 没有抓取到任何新闻")

        return


    # ======================================
    # 股票新闻分析
    # ======================================

    print()
    print("=" * 60)
    print("开始分析股票及行业信息")
    print("=" * 60)


    stock_news = process_stock_news(results)


    print(
        f"股票/行业相关信息："
        f"{len(stock_news)} 条"
    )


    # ======================================
    # 按新闻重要程度排序
    # ======================================

    stock_news.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )


    # ======================================
    # 控制台显示前20条重要新闻
    # ======================================

    print()
    print("=" * 60)
    print("今日重点股票新闻")
    print("=" * 60)


    for index, news in enumerate(stock_news[:20], 1):

        print()
        print(f"【{index}】 {news.get('level', '')}")
        print(f"评分：{news.get('score', 0)}")

        print(
            f"标题："
            f"{news.get('title', '')}"
        )


        # ----------------------------------
        # 涉及股票
        # ----------------------------------

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
                + "、".join(matched_names)
            )

        else:

            print("涉及股票：无")


        # ----------------------------------
        # 涉及行业
        # ----------------------------------

        matched_industries = news.get(
            "matched_industries",
            []
        )


        if matched_industries:

            print(
                "涉及行业："
                + "、".join(matched_industries)
            )

        else:

            print("涉及行业：无")


        # ----------------------------------
        # 新闻来源
        # ----------------------------------

        print(
            f"来源："
            f"{news.get('source', '')}"
        )


        # ----------------------------------
        # 新闻链接
        # ----------------------------------

        print(
            f"链接："
            f"{news.get('link', '')}"
        )


        # ----------------------------------
        # 评分原因
        # ----------------------------------

        reasons = news.get(
            "score_reasons",
            []
        )


        if reasons:

            print(
                "关注原因："
                + "、".join(reasons)
            )


    # ======================================
    # 如果没有股票相关信息
    # ======================================

    if not stock_news:

        print()
        print("=" * 60)
        print("今天没有发现与你关注股票相关的新闻")
        print("=" * 60)

        return


    # ======================================
    # 发送163邮箱
    # ======================================

    print()
    print("=" * 60)
    print("准备发送邮件")
    print("=" * 60)


    from mailer import send_email


    # --------------------------------------
    # 从 GitHub Secrets / 环境变量读取邮箱
    # --------------------------------------

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


    # ======================================
    # 检查邮箱配置
    # ======================================

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


    # ======================================
    # 发送邮件
    # ======================================

    try:

        send_email(
            stock_news,
            sender,
            password,
            receiver
        )

        print()
        print("=" * 60)
        print("✅ 股票新闻邮件发送完成")
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print("❌ 邮件发送失败")
        print("=" * 60)

        print(
            f"错误信息：{e}"
        )


# ==========================================
# 程序入口
# ==========================================

if __name__ == "__main__":

    main()
