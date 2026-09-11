from config import STOCKS, INDUSTRIES


def get_content(news):
    title = news.get("title", "")
    body = news.get("body", "")

    return f"{title} {body}"


def match_stocks(news):
    """
    股票精准匹配。

    只有出现：
    1. 公司名称
    2. 股票代码

    才认为是该股票相关新闻。

    行业关键词不再用于匹配股票，
    避免“人工智能”把达实智能误匹配出来。
    """

    title = news.get("title", "")
    body = news.get("body", "")

    # 标题权重更高
    title_content = title
    content = get_content(news)

    matched_stocks = []

    for stock_name, stock_info in STOCKS.items():

        stock_code = stock_info["code"]

        if stock_name in title_content:
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
    行业匹配。

    只负责判断新闻涉及哪些行业，
    不直接将新闻归属于某只股票。
    """

    content = get_content(news)

    matched = []

    for industry, keywords in INDUSTRIES.items():

        for keyword in keywords:

            if keyword in content:
                matched.append(industry)
                break

    return matched


def count_keyword_hits(news, keywords):
    """
    统计一组关键词实际出现了多少种。
    """

    content = get_content(news)

    hits = []

    for keyword in keywords:
        if keyword in content:
            hits.append(keyword)

    return list(dict.fromkeys(hits))


def analyze_news(news):

    stocks = match_stocks(news)
    industries = match_industries(news)

    news["matched_stocks"] = stocks
    news["matched_industries"] = industries

    return news
