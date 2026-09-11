from config import STOCKS, INDUSTRIES


def match_stocks(news):
    """
    精准匹配关注股票。

    只有新闻中明确出现：
    1. 股票名称
    2. 股票代码

    才认为新闻属于该股票。
    """

    title = news.get("title", "")
    body = news.get("body", "")
    content = title + " " + body

    matched_stocks = []

    for stock_name, stock_info in STOCKS.items():

        stock_code = stock_info["code"]

        # 只允许公司名称或股票代码进行股票匹配
        if stock_name in content or stock_code in content:

            matched_stocks.append({
                "name": stock_name,
                "code": stock_code,
                "industry": stock_info["industry"],
                "keyword": (
                    stock_name
                    if stock_name in content
                    else stock_code
                )
            })

    return matched_stocks


def match_industries(news):
    """
    匹配行业信息。

    行业关键词只用于识别行业，
    不直接归属于某一只股票。
    """

    title = news.get("title", "")
    body = news.get("body", "")
    content = title + " " + body

    matched = []

    for industry, keywords in INDUSTRIES.items():

        for keyword in keywords:

            if keyword in content:
                matched.append(industry)
                break

    return matched


def analyze_news(news):

    stocks = match_stocks(news)

    industries = match_industries(news)

    news["matched_stocks"] = stocks
    news["matched_industries"] = industries

    return news
