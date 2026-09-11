```python
import scrapy
from datetime import datetime
from urllib.parse import urljoin


class Cctv1Spider(scrapy.Spider):
    name = 'cctv1'
    allowed_domains = ['tv.cctv.com', 'tv.cctv.cn']

    start_urls = [
        'https://tv.cctv.com/lm/xwlb/index.shtml'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 2,
    }

    def parse(self, response):
        """
        解析 CCTV-1《新闻联播》栏目页
        """

        self.logger.info(
            '[CCTV-1] 栏目页访问成功: status=%s, url=%s',
            response.status,
            response.url
        )

        # 当前央视页面不再稳定使用 li.items，
        # 因此直接从页面中的 a 标签寻找新闻详情链接。
        links = response.css('a::attr(href)').getall()

        self.logger.info(
            '[CCTV-1] 页面共发现 %d 个链接',
            len(links)
        )

        seen_links = set()
        news_count = 0

        for href in links:
            if not href:
                continue

            href = href.strip()
            link = urljoin(response.url, href)

            # 只处理央视 2026 年新闻详情页
            if not self.is_news_url(link):
                continue

            if link in seen_links:
                continue

            seen_links.add(link)

            # 从当前 a 标签获取标题
            title = None

            # 重新根据 href 找对应的 a 标签
            title_nodes = response.xpath(
                '//a[@href=$href]/string()',
                href=href
            ).getall()

            if title_nodes:
                title = ''.join(
                    text.strip() for text in title_nodes if text.strip()
                )

            # 如果没有直接拿到标题，再尝试从文本节点获取
            if not title:
                title_nodes = response.xpath(
                    '//a[@href=$href]//text()',
                    href=href
                ).getall()

                title = ''.join(
                    text.strip() for text in title_nodes if text.strip()
                )

            if not title:
                title = 'CCTV-1新闻'

            # 过滤明显不是新闻标题的链接
            if not self.is_valid_title(title):
                continue

            news_count += 1

            self.logger.info(
                '[CCTV-1] 发现新闻 %d: %s',
                news_count,
                title[:80]
            )

            yield scrapy.Request(
                url=link,
                callback=self.parse_detail,
                meta={
                    'title': title,
                    'link': link,
                    'source': '新闻联播'
                },
                dont_filter=True
            )

        self.logger.info(
            '[CCTV-1] 本次共发现 %d 条新闻链接',
            news_count
        )

        if news_count == 0:
            self.logger.warning(
                '[CCTV-1] 没有找到新闻链接，请检查央视页面结构是否发生变化'
            )

    def parse_detail(self, response):
        """
        解析新闻详情页
        """

        title = response.meta['title']
        link = response.meta['link']
        source = response.meta['source']

        self.logger.info(
            '[CCTV-1] 正在解析详情页: %s',
            title[:80]
        )

        body = self.extract_body(response)

        if not body:
            self.logger.warning(
                '[CCTV-1] 新闻正文为空: %s',
                link
            )

        yield {
            'title': title.strip(),
            'link': link,
            'body': body,
            'source': source,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def extract_body(self, response):
        """
        提取新闻正文。

        央视页面结构可能发生变化，因此按照多个候选区域依次尝试。
        """

        # 方案一：原来的 cnt_bd
        selectors = [
            '//div[contains(@class, "cnt_bd")]//text()',

            # 央视部分详情页正文区域
            '//div[contains(@class, "content_area")]//text()',

            '//div[contains(@class, "article")]//text()',

            '//div[contains(@class, "text_area")]//text()',

            '//div[contains(@class, "content")]//p//text()',

            '//article//p//text()',

            '//p//text()',
        ]

        for selector in selectors:
            texts = response.xpath(selector).getall()

            cleaned = []
            for text in texts:
                text = text.strip()

                if text:
                    cleaned.append(text)

            # 至少有一定长度才认为找到了正文
            if len(''.join(cleaned)) >= 50:
                return '\n'.join(cleaned)

        return ''

    @staticmethod
    def is_news_url(url):
        """
        判断是否为央视新闻详情页。

        当前央视新闻详情页通常类似：
        https://tv.cctv.com/2026/09/11/VIDExxxxx.shtml
        """

        if not (
            url.startswith('https://tv.cctv.com/')
            or url.startswith('http://tv.cctv.com/')
        ):
            return False

        # 新闻详情页通常包含 /2026/09/11/
        parts = url.split('/')

        if len(parts) < 6:
            return False

        # URL 中必须存在年份目录
        year_part = parts[3]

        if not year_part.isdigit():
            return False

        if len(year_part) != 4:
            return False

        # 排除明显的栏目页、首页等
        if '/lm/' in url:
            return False

        if not url.endswith('.shtml'):
            return False

        return True

    @staticmethod
    def is_valid_title(title):
        """
        过滤明显不是新闻标题的链接。
        """

        if not title:
            return False

        title = title.strip()

        # 标题太短，通常不是新闻
        if len(title) < 4:
            return False

        # 排除网站导航
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
```
