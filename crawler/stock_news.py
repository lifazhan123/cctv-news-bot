# crawler/stock_news.py

import scrapy
from datetime import datetime
from urllib.parse import quote


class StockNewsSpider(scrapy.Spider):

    name = "stock_news"

    allowed_domains = [
        "search.sina.com.cn",
        "finance.sina.com.cn",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 2,
    }

    def start_requests(self):

        stocks = [
            ("长城军工", "601606"),
            ("高德红外", "002414"),
            ("天富能源", "600509"),
            ("奥瑞德", "600666"),
            ("金正大", "002470"),
            ("隆华科技", "300263"),
            ("中电鑫龙", "002298"),
            ("达实智能", "002421"),
            ("协鑫集成", "002506"),
            ("天融信", "002212"),
            ("万马股份", "002276"),
            ("合众思壮", "002383"),
        ]

        for name, code in stocks:

            keyword = quote(name)

            url = (
                "https://search.sina.com.cn/"
                f"?q={keyword}"
                "&c=news"
                "&from=channel"
            )

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "stock_name": name,
                    "stock_code": code,
                }
            )

    def parse(self, response):

        stock_name = response.meta["stock_name"]
        stock_code = response.meta["stock_code"]

        self.logger.info(
            "[股票新闻] 正在抓取：%s %s",
            stock_name,
            stock_code
        )

        items = response.css("div.box-result")

        count = 0

        for item in items:

            title = "".join(
                item.css("h2 a::text").getall()
            ).strip()

            link = item.css("h2 a::attr(href)").get()

            body = "".join(
                item.css("p::text").getall()
            ).strip()

            if not title or not link:
                continue

            count += 1

            yield {
                "title": title,
                "link": link,
                "body": body,
                "source": "新浪财经",
                "stock_name": stock_name,
                "stock_code": stock_code,
                "crawl_time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

        self.logger.info(
            "[股票新闻] %s 共发现 %d 条",
            stock_name,
            count
        )
