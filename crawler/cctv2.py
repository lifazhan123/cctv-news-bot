import scrapy
from datetime import datetime
from urllib.parse import urljoin


class Cctv2Spider(scrapy.Spider):
    name = 'cctv2'
    allowed_domains = ['tv.cctv.com', 'tv.cctv.cn']

    start_urls = [
        'https://tv.cctv.com/lm/zdcj/index.shtml'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 2,
    }

    def parse(self, response):
        """
        解析 CCTV-2《正点财经》栏目页
        """

        self.logger.info(
            '[CCTV-2] 栏目页访问成功: status=%s, url=%s',
            response.status,
            response.url
        )

        # 不再使用原来的 li.items 选择器，
        # 直接从页面所有 a 标签中寻找央视新闻详情链接。
        links = response.css('a::attr(href)').getall()

        self.logger.info(
            '[CCTV-2] 页面共发现 %d 个链接',
            len(links)
        )

        seen_links = set()
        news_count = 0

        for href in links:

            if not href:
                continue

            href = href.strip()

            # 将相对地址转换成绝对地址
            link = urljoin(response.url, href)

            # 判断是否为央视新闻详情页
            if not self.is_news_url(link):
                continue

            # URL 去重
            if link in seen_links:
                continue

            seen_links.add(link)

            # 获取标题
            title = None

            # 第一种方式：获取 a 标签直接文本
            title_nodes = response.xpath(
                '//a[@href=$href]/string()',
                href=href
            ).getall()

            if title_nodes:
                title = ''.join(
                    text.strip()
                    for text in title_nodes
                    if text.strip()
                )

            # 第二种方式：获取 a 标签内部所有文本
            if not title:
                title_nodes = response.xpath(
                    '//a[@href=$href]//text()',
                    href=href
                ).getall()

                title = ''.join(
                    text.strip()
                    for text in title_nodes
                    if text.strip()
                )

            if not title:
                title = 'CCTV-2新闻'

            title = title.strip()

            # 过滤导航类链接
            if not self.is_valid_title(title):
                continue

            news_count += 1

            self.logger.info(
                '[CCTV-2] 发现新闻 %d: %s',
                news_count,
                title[:80]
            )

            yield scrapy.Request(
                url=link,
                callback=self.parse_detail,
                meta={
                    'title': title,
                    'link': link,
                    'source': 'CCTV-2正点财经'
                },
                dont_filter=True
            )

        self.logger.info(
            '[CCTV-2] 本次共发现 %d 条新闻链接',
            news_count
        )

        if news_count == 0:
            self.logger.warning(
                '[CCTV-2] 没有找到新闻链接，请检查央视页面结构是否发生变化'
            )

    def parse_detail(self, response):
        """
        解析 CCTV-2 新闻详情页
        """

        title = response.meta['title']
        link = response.meta['link']
        source = response.meta['source']

        self.logger.info(
            '[CCTV-2] 正在解析详情页: %s',
            title[:80]
        )

        body = self.extract_body(response)

        if not body:
            self.logger.warning(
                '[CCTV-2] 新闻正文为空: %s',
                link
            )

        yield {
            'title': title,
            'link': link,
            'body': body,
            'source': source,
            'crawl_time': datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'
            )
        }

    def extract_body(self, response):
        """
        提取新闻正文。

        央视页面结构可能变化，
        因此准备多个候选正文区域。
        """

        selectors = [

            # 原来的正文区域
            '//div[contains(@class, "cnt_bd")]//text()',

            # 常见正文区域
            '//div[contains(@class, "content_area")]//text()',

            '//div[contains(@class, "article")]//text()',

            '//div[contains(@class, "text_area")]//text()',

            '//div[contains(@class, "content")]//p//text()',

            # HTML5 article
            '//article//p//text()',

            # 最后的通用方案
            '//p//text()',
        ]

        for selector in selectors:

            texts = response.xpath(selector).getall()

            cleaned = []

            for text in texts:

                text = text.strip()

                if text:
                    cleaned.append(text)

            body = '\n'.join(cleaned)

            # 正文至少达到一定长度
            if len(body) >= 50:
                return body

        return ''

    @staticmethod
    def is_news_url(url):
        """
        判断 URL 是否属于央视新闻详情页。

        典型形式：

        https://tv.cctv.com/2026/09/11/xxxxx.shtml
        """

        # 必须是央视 tv.cctv.com
        if not (
            url.startswith('https://tv.cctv.com/')
            or url.startswith('http://tv.cctv.com/')
        ):
            return False

        parts = url.split('/')

        if len(parts) < 6:
            return False

        # URL 第4部分应该是年份
        year_part = parts[3]

        if not year_part.isdigit():
            return False

        if len(year_part) != 4:
            return False

        # 排除栏目页
        if '/lm/' in url:
            return False

        # 新闻详情页一般为 shtml
        if not url.endswith('.shtml'):
            return False

        return True

    @staticmethod
    def is_valid_title(title):
        """
        过滤导航、菜单等非新闻标题。
        """

        if not title:
            return False

        title = title.strip()

        # 标题过短，一般不是新闻
        if len(title) < 4:
            return False

        exclude_words = [
            '首页',
            '节目官网',
            '登录',
            '注册',
            '更多',
            '查看',
            '返回顶部',
            '热门栏目',
            '看更多栏目',
        ]

        for word in exclude_words:

            if title == word:
                return False

        return True
