import scrapy
from datetime import datetime


class MilitaryNewsSpider(scrapy.Spider):
    name = "military_news"
    allowed_domains = [
        "cntv.cn",
        "cctv.com",
        "tv.cctv.com",
    ]

    start_urls = [
        "https://www.cntv.cn/cctv7/",
    ]

    # 军事、战争、军工关键词
    MILITARY_KEYWORDS = [
        # 战争 / 冲突
        "战争",
        "冲突",
        "军事冲突",
        "武装冲突",
        "战事",
        "战场",
        "军事行动",
        "空袭",
        "袭击",
        "炮击",
        "停火",
        "交火",

        # 军事行动 / 演习
        "军演",
        "军事演习",
        "联合军演",
        "实弹演习",
        "军事训练",
        "作战演练",
        "战备",
        "战备警巡",

        # 国防 / 军工
        "军工",
        "国防",
        "武器装备",
        "国防工业",
        "国防科技",
        "国防建设",
        "军工企业",
        "军工集团",
        "军民融合",
        "军品",
        "军方",
        "军队",

        # 导弹 / 无人装备
        "导弹",
        "弹道导弹",
        "巡航导弹",
        "高超音速",
        "火箭弹",
        "无人机",
        "无人作战",
        "无人系统",
        "无人艇",
        "无人潜航器",

        # 航空
        "战斗机",
        "歼击机",
        "轰炸机",
        "预警机",
        "直升机",
        "航空发动机",

        # 雷达 / 红外 / 光电
        "雷达",
        "红外",
        "红外探测",
        "热成像",
        "光电",
        "电子战",
        "电子对抗",

        # 海军
        "航母",
        "航空母舰",
        "军舰",
        "舰艇",
        "驱逐舰",
        "护卫舰",
        "潜艇",

        # 卫星 / 导航
        "军用卫星",
        "卫星导航",
        "北斗",
        "卫星互联网",

        # 军工产业链
        "军工订单",
        "军品订单",
        "装备采购",
        "装备列装",
        "批量生产",
        "量产",
        "装备研发",
        "装备试验",
        "装备定型",
        "装备采购",
        "军事采购",

        # 军费
        "军费",
        "国防预算",
        "国防支出",
    ]

    # 重点关注栏目
    MILITARY_PROGRAMS = [
        "军事报道",
        "国防军事早报",
        "正午国防军事",
        "防务新观察",
        "军事制高点",
        "军事科技",
        "军武零距离",
        "兵器面面观",
        "军迷行天下",
        "军事纪实",
    ]

    def clean_text(self, text):
        if not text:
            return ""

        return " ".join(
            text.replace("\n", " ")
                .replace("\r", " ")
                .split()
        ).strip()

    def is_valid_url(self, url):
        if not url:
            return False

        return (
            "cctv.com" in url
            or "cntv.cn" in url
        )

    def match_keywords(self, title, body):
        content = f"{title} {body}"

        matched = []

        for keyword in self.MILITARY_KEYWORDS:
            if keyword in content:
                matched.append(keyword)

        return list(dict.fromkeys(matched))

    def match_program(self, title, body):
        content = f"{title} {body}"

        matched = []

        for program in self.MILITARY_PROGRAMS:
            if program in content:
                matched.append(program)

        return list(dict.fromkeys(matched))

    def extract_title(self, response):
        candidates = [
            response.css("h1::text").get(),
            response.css(".title::text").get(),
            response.css(".tit::text").get(),
            response.css("title::text").get(),
        ]

        for title in candidates:
            title = self.clean_text(title)

            if title and len(title) >= 4:
                return title

        return ""

    def extract_body(self, response):
        selectors = [
            ".content_area ::text",
            ".content ::text",
            ".article ::text",
            ".article-content ::text",
            ".text_area ::text",
            ".video_desc ::text",
            "article ::text",
        ]

        texts = []

        for selector in selectors:
            values = response.css(selector).getall()

            if values:
                texts.extend(values)

        if not texts:
            texts = response.css("body ::text").getall()

        body = " ".join(
            self.clean_text(text)
            for text in texts
            if self.clean_text(text)
        )

        return body[:10000]

    def parse(self, response):

        self.logger.info(
            "正在分析军事页面：%s",
            response.url
        )

        # 当前页面所有链接
        links = response.css("a::attr(href)").getall()

        seen = set()

        for href in links:

            if not href:
                continue

            href = response.urljoin(href)

            if href in seen:
                continue

            seen.add(href)

            if not self.is_valid_url(href):
                continue

            # 避免首页、频道导航等链接
            if href.rstrip("/") == response.url.rstrip("/"):
                continue

            yield scrapy.Request(
                href,
                callback=self.parse_detail,
                dont_filter=True,
            )

    def parse_detail(self, response):

        title = self.extract_title(response)

        if not title:
            return

        body = self.extract_body(response)

        matched_keywords = self.match_keywords(
            title,
            body
        )

        matched_programs = self.match_program(
            title,
            body
        )

        # 标题或正文没有军事相关关键词，直接忽略
        if not matched_keywords:
            return

        # 过滤明显的栏目导航、广告等
        invalid_titles = [
            "首页",
            "频道",
            "节目单",
            "直播",
            "回看",
            "登录",
            "注册",
            "下载",
        ]

        if title in invalid_titles:
            return

        yield {
            "title": title,
            "body": body,
            "source": "央视军事",
            "link": response.url,
            "matched_military_keywords": matched_keywords,
            "matched_military_programs": matched_programs,
            "publish_date": datetime.now().strftime(
                "%Y-%m-%d"
            ),
        }
