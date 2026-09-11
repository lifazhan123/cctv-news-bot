def calculate_score(news):
    title = news.get("title", "")
    body = news.get("body", "")

    content = title + " " + body

    score = 0
    reasons = []

    matched_stocks = news.get("matched_stocks", [])
    matched_industries = news.get("matched_industries", [])

    # ==================================================
    # 一、股票直接相关
    # ==================================================

    if matched_stocks:
        score += 15
        reasons.append("涉及关注股票")

        # 公司重大事项
        company_keywords = [
            "重大合同",
            "重大订单",
            "中标",
            "签署合同",
            "业绩预告",
            "年度报告",
            "半年度报告",
            "季度报告",
            "回购",
            "增持",
            "减持",
            "并购",
            "重组",
            "定增",
        ]

        for keyword in company_keywords:
            if keyword in content:
                score += 15
                reasons.append(keyword)

        # 公司经营、项目、技术等
        company_positive_keywords = [
            "新产品",
            "新项目",
            "重大项目",
            "产能提升",
            "产能扩张",
            "技术突破",
            "研发成功",
            "订单增长",
            "收入增长",
            "利润增长",
        ]

        for keyword in company_positive_keywords:
            if keyword in content:
                score += 8
                reasons.append(keyword)

    # ==================================================
    # 二、行业相关
    # ==================================================

    if matched_industries:

        industry_keywords = [
            "行业政策",
            "产业政策",
            "发展规划",
            "国家战略",
            "价格上涨",
            "价格下跌",
            "价格变化",
            "需求增长",
            "需求下降",
            "产能",
            "产量",
            "出口增长",
            "出口下降",
            "投资增长",
            "装机容量",
            "市场规模",
            "供需",
        ]

        industry_hit = False

        for keyword in industry_keywords:
            if keyword in content:
                score += 8
                reasons.append(keyword)
                industry_hit = True

        # 如果只是泛泛提到“能源、农业、军工”等行业，
        # 不直接给予很高评分
        if not industry_hit:
            score += 2
            reasons.append("涉及相关行业")

    # ==================================================
    # 三、宏观政策
    # ==================================================

    macro_keywords = [
        "国务院",
        "国务院办公厅",
        "国家发展改革委",
        "财政部",
        "工业和信息化部",
        "国家能源局",
        "证监会",
        "央行",
        "中国人民银行",
        "政策发布",
        "政策出台",
        "实施方案",
        "指导意见",
    ]

    for keyword in macro_keywords:
        if keyword in content:
            score += 5
            reasons.append("政策信息")

    # ==================================================
    # 四、限制普通新闻的最高评分
    # ==================================================

    # 如果没有明确涉及关注股票，
    # 行业新闻最高按照一般行业信息处理
    if not matched_stocks and score > 12:
        score = 12

    # ==================================================
    # 五、确定关注等级
    # ==================================================

    if score >= 30:
        level = "🔥 重点关注"
    elif score >= 15:
        level = "⭐ 值得关注"
    elif score >= 6:
        level = "📌 一般关注"
    else:
        level = "普通信息"

    news["score"] = score
    news["level"] = level

    # 去重，同时保持原顺序
    news["score_reasons"] = list(dict.fromkeys(reasons))

    return news
