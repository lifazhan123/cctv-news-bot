# analyzer/score.py

def calculate_score(news):

    title = news.get("title", "")
    body = news.get("body", "")

    content = title + " " + body

    score = 0
    reasons = []

    # =========================
    # 公司公告/重大事件
    # =========================

    high_keywords = [
        "公告",
        "重大合同",
        "重大订单",
        "中标",
        "签署合同",
        "业绩预告",
        "年度报告",
        "半年度报告",
        "季度报告",
        "定增",
        "回购",
        "增持",
        "减持",
        "并购",
        "重组",
    ]

    for keyword in high_keywords:

        if keyword in content:
            score += 10
            reasons.append(keyword)

    # =========================
    # 行业重大消息
    # =========================

    industry_keywords = [
        "政策",
        "规划",
        "国家战略",
        "重大突破",
        "首次",
        "创新",
        "产能",
        "价格上涨",
        "价格下跌",
        "需求增长",
        "出口增长",
    ]

    for keyword in industry_keywords:

        if keyword in content:
            score += 6
            reasons.append(keyword)

    # =========================
    # 公司直接出现
    # =========================

    if news.get("matched_stocks"):
        score += 8
        reasons.append("涉及关注股票")

    # =========================
    # 行业匹配
    # =========================

    if news.get("matched_industries"):
        score += 3
        reasons.append("涉及相关行业")

    # =========================
    # 判断等级
    # =========================

    if score >= 20:
        level = "🔥 重点关注"

    elif score >= 12:
        level = "⭐ 值得关注"

    elif score >= 6:
        level = "📌 一般关注"

    else:
        level = "普通信息"

    news["score"] = score
    news["level"] = level
    news["score_reasons"] = list(set(reasons))

    return news
