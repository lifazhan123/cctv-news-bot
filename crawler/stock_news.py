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

            self.logger.info(
                "[股票新闻] 开始访问：%s %s",
                name,
                code
            )

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "stock_name": name,
                    "stock_code": code,
                },
                headers={
                    "Referer": "https://www.sina.com.cn/",
                }
            )

    def parse(self, response):

        stock_name = response.meta["stock_name"]
        stock_code = response.meta["stock_code"]

        self.logger.info(
            "[股票新闻] 搜索结果：%s %s status=%s",
            stock_name,
            stock_code,
            response.status
        )

        # -------------------------------------------------
        # 方法一：新浪旧版搜索结果
        # -------------------------------------------------

        items = response.css(
            "div.box-result"
        )

        count = 0

        for item in items:

            title = "".join(
                item.css(
                    "h2 a::text"
                ).getall()
            ).strip()

            link = item.css(
                "h2 a::attr(href)"
            ).get()

            body = "".join(
                item.css(
                    "p::text"
                ).getall()
            ).strip()

            if not title or not link:
                continue

            if not self.is_valid_link(link):
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

        # -------------------------------------------------
        # 方法二：页面结构变化时，寻找所有新闻链接
        # -------------------------------------------------

        if count == 0:

            self.logger.warning(
                "[股票新闻] %s 未找到 box-result，"
                "尝试备用解析方式",
                stock_name
            )

            seen_links = set()

            anchors = response.css(
                "a[href]"
            )

            for anchor in anchors:

                href = anchor.attrib.get(
                    "href"
                )

                if not href:
                    continue

                href = href.strip()

                if href in seen_links:
                    continue

                seen_links.add(href)

                link = href

                title_nodes = anchor.xpath(
                    ".//text()"
                ).getall()

                title = "".join(
                    text.strip()
                    for text in title_nodes
                    if text.strip()
                ).strip()

                if not title:
                    continue

                if not self.is_valid_link(link):
                    continue

                # 股票名称必须出现在标题附近
                # 或者链接本身属于财经新闻页面
                if (
                    stock_name not in title
                    and "finance.sina.com.cn" not in link
                ):
                    continue

                count += 1

                self.logger.info(
                    "[股票新闻] %s 备用方式发现：%s",
                    stock_name,
                    title[:80]
                )

                yield scrapy.Request(
                    url=link,
                    callback=self.parse_detail,
                    meta={
                        "title": title,
                        "link": link,
                        "stock_name": stock_name,
                        "stock_code": stock_code,
                    },
                    dont_filter=True
                )

        self.logger.info(
            "[股票新闻] %s 共发现 %d 条",
            stock_name,
            count
        )

    def parse_detail(self, response):

        title = response.meta["title"]
        link = response.meta["link"]

        stock_name = response.meta[
            "stock_name"
        ]

        stock_code = response.meta[
            "stock_code"
        ]

        body = self.extract_body(
            response
        )

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

    @staticmethod
    def is_valid_link(link):

        if not link:
            return False

        if not (
            link.startswith(
                "http://"
            )
            or link.startswith(
                "https://"
            )
        ):
            return False

        if (
            "sina.com.cn" not in link
            and "sina.cn" not in link
        ):
            return False

        return True

    @staticmethod
    def extract_body(response):

        selectors = [

            "//div[contains(@class,'article')]//text()",

            "//div[contains(@class,'article-content')]//text()",

            "//div[contains(@class,'content')]//p//text()",

            "//article//p//text()",

            "//p//text()",
        ]

        for selector in selectors:

            texts = response.xpath(
                selector
            ).getall()

            cleaned = []

            for text in texts:

                text = text.strip()

                if text:
                    cleaned.append(text)

            body = "\n".join(
                cleaned
            )

            if len(body) >= 50:

                return body

        return ""
