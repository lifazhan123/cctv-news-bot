from config import STOCKS, INDUSTRIES


def get_content(news):
    title = news.get("title", "")
    body = news.get("body", "")

    return f"{title} {body}"


def match_stocks(news):
    """
    精准匹配关注股票。

    只有出现：
    1. 公司名称
    2. 股票代码

    才认为新闻属于该股票。
    """

    title = news.get("title", "")
    content = get_content(news)

    matched_stocks = []

    for stock_name, stock_info in STOCKS.items():

        stock_code = stock_info["code"]

        # 标题出现公司名称
        if stock_name in title:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": stock_name,
                "match_type": "标题"
            })

        # 正文出现公司名称
        elif stock_name in content:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": stock_name,
                "match_type": "正文"
            })

        # 股票代码出现
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

    content = get_content(news)

    matched = []

    for industry, keywords in INDUSTRIES.items():

        for keyword in keywords:

            if keyword in content:

                matched.append(industry)
                break

    return matched


def count_keyword_hits(news, keywords):

    content = get_content(news)

    hits = []

    for keyword in keywords:

        if keyword in content:
            hits.append(keyword)

    return list(
        dict.fromkeys(hits)
    )


def analyze_news(news):

    stocks = match_stocks(news)

    industries = match_industries(news)

    news["matched_stocks"] = stocks

    news["matched_industries"] = industries

    # 军事新闻
    if news.get("source") == "央视军事":

        news["matched_military_keywords"] = (
            news.get(
                "matched_military_keywords",
                []
            )
        )

    return news
