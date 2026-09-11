import scrapy
from datetime import datetime
from urllib.parse import urljoin


class Cctv1Spider(scrapy.Spider):
    name = 'cctv1'

    allowed_domains = [
        'tv.cctv.com',
        'tv.cctv.cn'
    ]

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

        # 不再使用 li.items 选择器。
        # 直接获取页面中的所有 a 标签。
        anchors = response.css('a[href]')

        self.logger.info(
            '[CCTV-1] 页面共发现 %d 个链接',
            len(anchors)
        )

        seen_links = set()
        news_count = 0

        for anchor in anchors:

            href = anchor.attrib.get('href')

            if not href:
                continue

            href = href.strip()

            # 将相对 URL 转换成绝对 URL
            link = urljoin(response.url, href)

            # 判断是否为新闻详情页
            if not self.is_news_url(link):
                continue

            # URL 去重
            if link in seen_links:
                continue

            seen_links.add(link)

            # 直接从当前 a 标签获取标题
            title_nodes = anchor.xpath('.//text()').getall()

            title = ''.join(
                text.strip()
                for text in title_nodes
                if text.strip()
            )

            title = title.strip()

            # 没有标题时使用默认标题
            if not title:
                title = 'CCTV-1新闻'

            # 过滤明显不是新闻的链接
            if not self.is_valid_title(title):
                continue

            news_count += 1

            self.logger.info(
                '[CCTV-1] 发现新闻 %d: %s',
                news_count,
                title[:80]
            )

            # 请求新闻详情页
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

        央视页面结构可能发生变化，
        因此使用多个候选区域依次尝试。
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

            # 新闻页面简介
            '//div[contains(@class, "brief")]//text()',

            '//div[contains(@class, "video_brief")]//text()',

            # 最后使用普通 p 标签
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

            # 正文达到一定长度才认为提取成功
            if len(body) >= 50:
                return body

        return ''

    @staticmethod
    def is_news_url(url):
        """
        判断 URL 是否属于央视新闻详情页。

        典型形式：

        https://tv.cctv.com/2026/09/11/VIDExxxxxxxxx.shtml
        """

        # 必须是央视电视台域名
        if not (
            url.startswith('https://tv.cctv.com/')
            or url.startswith('http://tv.cctv.com/')
        ):
            return False

        parts = url.split('/')

        # 例如：
        #
        # https:
        # //
        # tv.cctv.com
        # 2026
        # 09
        # 11
        # VIDExxxxx.shtml
        #
        # 所以至少需要 7 个部分
        if len(parts) < 7:
            return False

        # 年份
        year_part = parts[3]

        if not year_part.isdigit():
            return False

        if len(year_part) != 4:
            return False

        # 月份
        month_part = parts[4]

        if not month_part.isdigit():
            return False

        if len(month_part) != 2:
            return False

        # 日期
        day_part = parts[5]

        if not day_part.isdigit():
            return False

        if len(day_part) != 2:
            return False

        # 排除栏目页
        if '/lm/' in url:
            return False

        # 新闻详情页通常以 .shtml 结尾
        if not url.endswith('.shtml'):
            return False

        return True

    @staticmethod
    def is_valid_title(title):
        """
        过滤导航、菜单等无效标题。
        """

        if not title:
            return False

        title = title.strip()

        # 标题太短
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
            '节目单',
            '往期查询',
            '央视影音',
            '官方微博',
            '微信公众号',
            '扫一扫',
            '下载',
        ]

        for word in exclude_words:

            if title == word:
                return False

        return True
