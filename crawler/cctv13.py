import scrapy
from datetime import datetime


class Cctv13Spider(scrapy.Spider):
    name = 'cctv13'
    allowed_domains = ['tv.cctv.com', 'tv.cctv.cn']
    start_urls = ['https://tv.cctv.com/lm/xwzhibojian/index.shtml']

    def parse(self, response):
        news_items = response.xpath('//li[contains(@class, "items")]')
        for item in news_items:
            title = item.xpath('.//a/text()').get()
            link = item.xpath('.//a/@href').get()
            if not title or not link:
                continue
            if not link.startswith('http'):
                link = response.urljoin(link)
            yield scrapy.Request(
                url=link,
                callback=self.parse_detail,
                meta={'title': title.strip(), 'link': link, 'source': 'CCTV-13新闻直播间'}
            )

    def parse_detail(self, response):
        title = response.meta['title']
        link = response.meta['link']
        source = response.meta['source']
        content_div = response.xpath('//div[contains(@class, "cnt_bd")]')
        if content_div:
            all_text = content_div.xpath('.//text()').getall()
            body = '\n'.join([t.strip() for t in all_text if t.strip()])
        else:
            paragraphs = response.xpath('//p/text()').getall()
            body = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        yield {
            'title': title,
            'link': link,
            'body': body,
            'source': source,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
