# analyzer/filter.py

from config import STOCKS, INDUSTRIES


def match_stocks(news):
    """
    判断新闻涉及哪些股票
    """

    title = news.get("title", "")
    body = news.get("body", "")

    content = title + " " + body

    matched_stocks = []

    for stock_name, stock_info in STOCKS.items():

        for keyword in stock_info["keywords"]:

            if keyword in content:
                matched_stocks.append({
                    "name": stock_name,
                    "code": stock_info["code"],
                    "industry": stock_info["industry"],
                    "keyword": keyword
                })

                break

    return matched_stocks


def match_industries(news):
    """
    判断新闻属于哪些行业
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
