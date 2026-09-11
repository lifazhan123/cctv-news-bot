from config import STOCKS, INDUSTRIES


def get_content(news):
    title = news.get("title", "")
    body = news.get("body", "")

    return f"{title} {body}"


def match_stocks(news):
    """
    精准匹配股票。

    只有公司名称或股票代码明确出现，
    才认为新闻直接涉及该股票。
    """

    title = news.get("title", "")
    content = get_content(news)

    matched_stocks = []

    for stock_name, stock_info in STOCKS.items():

        stock_code = stock_info["code"]

        if stock_name in title:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": stock_name,
                "match_type": "标题"
            })

        elif stock_name in content:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": stock_name,
                "match_type": "正文"
            })

        elif stock_code in content:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": stock_code,
                "match_type": "股票代码"
            })

    return matched_stocks


def match_industries(news):
    """
    判断新闻涉及哪些行业。
    """

    content = get_content(news)

    matched = []

    for industry, keywords in INDUSTRIES.items():

        for keyword in keywords:

            if keyword in content:

                matched.append(industry)
                break

    return matched


def match_important_industry(news):
    """
    判断是否是真正具有投资价值的行业新闻。

    不能因为正文顺带出现“农业”“能源”等词，
    就认为是重要行业新闻。
    """

    content = get_content(news)

    important_keywords = [

        # 政策
        "行业政策",
        "产业政策",
        "发展规划",
        "指导意见",
        "实施方案",
        "专项行动",
        "监管政策",
        "政策调整",

        # 价格
        "价格上涨",
        "价格下跌",
        "价格大涨",
        "价格大跌",
        "价格调整",

        # 供需
        "供需",
        "供需紧张",
        "产能过剩",
        "产能退出",
        "库存下降",
        "库存上升",

        # 市场
        "市场规模",
        "市场需求",
        "需求增长",
        "需求下降",
        "投资增长",
        "投资下降",

        # 产业
        "产业链",
        "供应链",
        "产能扩张",
        "产能提升",
        "新增产能",
        "重大项目",
        "重大工程",

        # 技术
        "重大突破",
        "技术突破",
        "首次实现",
        "实现量产",
        "商业化",

        # 新能源
        "新能源装机",
        "新增装机",
        "储能",
        "充电基础设施",
        "数字电网",
    ]

    hits = []

    for keyword in important_keywords:

        if keyword in content:
            hits.append(keyword)

    return list(dict.fromkeys(hits))


def is_macro_noise(news):
    """
    判断是否属于宏观/外交类低价值新闻。
    """

    title = news.get("title", "")
    content = get_content(news)

    noise_keywords = [

        "会谈",
        "会见",
        "致辞",
        "访问",
        "外交",
        "友好交流",
        "两国",
        "双方表示",
        "国际社会",
        "全球发展",
        "人文交流",
        "国际合作",
        "共同发展",
    ]

    # 如果标题本身就属于新闻事件，
    # 只有出现明显行业投资关键词时才保留。
    for keyword in noise_keywords:

        if keyword in title:

            important_hits = match_important_industry(news)

            if not important_hits:
                return True

    return False


def count_keyword_hits(news, keywords):

    content = get_content(news)

    hits = []

    for keyword in keywords:

        if keyword in content:
            hits.append(keyword)

    return list(dict.fromkeys(hits))


def analyze_news(news):

    stocks = match_stocks(news)

    industries = match_industries(news)

    important_industry_hits = match_important_industry(news)

    macro_noise = is_macro_noise(news)

    news["matched_stocks"] = stocks

    news["matched_industries"] = industries

    news["important_industry_hits"] = important_industry_hits

    news["is_macro_noise"] = macro_noise

    return news
