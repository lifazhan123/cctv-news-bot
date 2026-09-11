import scrapy
from datetime import datetime
from urllib.parse import urljoin


class Cctv13Spider(scrapy.Spider):

    name = "cctv13"

    allowed_domains = [
        "tv.cctv.com",
        "tv.cctv.cn",
    ]

    start_urls = [
        "https://tv.cctv.com/cctv13/"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 2,
    }

    def parse(self, response):

        self.logger.info(
            "[CCTV-13] 页面访问成功：status=%s url=%s",
            response.status,
            response.url
        )

        anchors = response.css("a[href]")

        self.logger.info(
            "[CCTV-13] 页面发现链接：%d 个",
            len(anchors)
        )

        seen_links = set()
        news_count = 0

        for anchor in anchors:

            href = anchor.attrib.get("href")

            if not href:
                continue

            href = href.strip()

            link = urljoin(
                response.url,
                href
            )

            if not self.is_news_url(link):
                continue

            if link in seen_links:
                continue

            seen_links.add(link)

            # 直接从当前 a 标签获取文字
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

            if not self.is_valid_title(title):
                continue

            news_count += 1

            self.logger.info(
                "[CCTV-13] 发现新闻 %d：%s",
                news_count,
                title[:80]
            )

            yield scrapy.Request(
                url=link,
                callback=self.parse_detail,
                meta={
                    "title": title,
                    "link": link,
                    "source": "CCTV-13新闻"
                },
                dont_filter=True
            )

        self.logger.info(
            "[CCTV-13] 共发现新闻链接：%d 条",
            news_count
        )

        if news_count == 0:

            self.logger.warning(
                "[CCTV-13] 没有发现有效新闻链接"
            )

    def parse_detail(self, response):

        title = response.meta["title"]
        link = response.meta["link"]
        source = response.meta["source"]

        body = self.extract_body(response)

        self.logger.info(
            "[CCTV-13] 解析新闻：%s",
            title[:80]
        )

        if not body:

            self.logger.warning(
                "[CCTV-13] 正文为空：%s",
                link
            )

        yield {
            "title": title,
            "link": link,
            "body": body,
            "source": source,
            "crawl_time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

    def extract_body(self, response):

        selectors = [

            '//div[contains(@class,"cnt_bd")]//text()',

            '//div[contains(@class,"content_area")]//text()',

            '//div[contains(@class,"article")]//text()',

            '//div[contains(@class,"text_area")]//text()',

            '//div[contains(@class,"content")]//p//text()',

            '//article//p//text()',

            '//div[contains(@class,"brief")]//text()',

            '//div[contains(@class,"video_brief")]//text()',

            '//p//text()',
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

            body = "\n".join(cleaned)

            if len(body) >= 50:
                return body

        return ""

    @staticmethod
    def is_news_url(url):

        if not (
            url.startswith(
                "https://tv.cctv.com/"
            )
            or url.startswith(
                "http://tv.cctv.com/"
            )
        ):
            return False

        parts = url.split("/")

        # 例如：
        # https://tv.cctv.com/2026/09/11/VIDExxxx.shtml

        if len(parts) < 7:
            return False

        year = parts[3]
        month = parts[4]
        day = parts[5]

        if not year.isdigit():
            return False

        if len(year) != 4:
            return False

        if not month.isdigit():
            return False

        if len(month) != 2:
            return False

        if not day.isdigit():
            return False

        if len(day) != 2:
            return False

        if "/lm/" in url:
            return False

        if not url.endswith(".shtml"):
            return False

        return True

    @staticmethod
    def is_valid_title(title):

        if not title:
            return False

        title = title.strip()

        if len(title) < 4:
            return False

        exclude_words = [
            "首页",
            "节目官网",
            "登录",
            "注册",
            "更多",
            "查看",
            "返回顶部",
            "热门栏目",
            "看更多栏目",
            "节目单",
            "往期查询",
            "央视影音",
            "官方微博",
            "微信公众号",
            "扫一扫",
            "下载",
        ]

        if title in exclude_words:
            return False

        return True
