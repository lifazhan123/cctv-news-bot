from analyzer.filter import count_keyword_hits


COMPANY_MAJOR_KEYWORDS = [
    "重大合同",
    "重大订单",
    "中标",
    "签署重大合同",
    "签订重大合同",
    "重大项目",
    "重大投资",
    "收购",
    "并购",
    "重组",
    "资产重组",
    "定增",
    "回购",
    "增持",
    "减持",
]


COMPANY_OPERATION_KEYWORDS = [
    "业绩预告",
    "业绩快报",
    "年度报告",
    "半年度报告",
    "季度报告",
    "营收增长",
    "收入增长",
    "净利润增长",
    "利润增长",
    "订单增长",
    "销量增长",
    "产能提升",
    "产能扩张",
    "项目投产",
]


COMPANY_TECH_KEYWORDS = [
    "技术突破",
    "研发成功",
    "新产品",
    "新技术",
    "产品发布",
    "首次",
    "量产",
    "国产替代",
]


POLICY_KEYWORDS = [
    "国务院",
    "国家发展改革委",
    "国家能源局",
    "工业和信息化部",
    "财政部",
    "商务部",
    "科技部",
    "农业农村部",
    "证监会",
    "中国人民银行",
]


def calculate_score(news):

    matched_stocks = news.get("matched_stocks", [])
    matched_industries = news.get("matched_industries", [])

    important_industry_hits = news.get(
        "important_industry_hits",
        []
    )

    is_macro_noise = news.get(
        "is_macro_noise",
        False
    )

    score = 0
    reasons = []

    # ==================================================
    # 一、直接涉及股票
    # ==================================================

    if matched_stocks:

        # 股票基础分
        score += 15
        reasons.append("涉及关注股票")

        # 标题出现公司名称
        for stock in matched_stocks:

            if stock.get("match_type") == "标题":

                score += 10
                reasons.append("标题涉及公司")
                break

        # 重大事项
        major_hits = count_keyword_hits(
            news,
            COMPANY_MAJOR_KEYWORDS
        )

        if major_hits:

            score += min(
                len(major_hits) * 10,
                30
            )

            reasons.extend(major_hits)

        # 经营信息
        operation_hits = count_keyword_hits(
            news,
            COMPANY_OPERATION_KEYWORDS
        )

        if operation_hits:

            score += min(
                len(operation_hits) * 6,
                18
            )

            reasons.extend(operation_hits)

        # 技术信息
        tech_hits = count_keyword_hits(
            news,
            COMPANY_TECH_KEYWORDS
        )

        if tech_hits:

            score += min(
                len(tech_hits) * 5,
                15
            )

            reasons.extend(tech_hits)

    # ==================================================
    # 二、行业新闻
    # ==================================================

    elif matched_industries:

        # 如果只是宏观/外交新闻
        if is_macro_noise:

            score = 0
            reasons.append("宏观信息")

        else:

            # 有明确行业重大变化
            if important_industry_hits:

                score += 8

                reasons.extend(
                    important_industry_hits[:3]
                )

            else:

                # 只是普通行业提及
                score += 2
                reasons.append("一般行业信息")

            # 政策信息
            policy_hits = count_keyword_hits(
                news,
                POLICY_KEYWORDS
            )

            if policy_hits and important_industry_hits:

                score += 5
                reasons.append("政策信息")

    # ==================================================
    # 三、宏观新闻强制降权
    # ==================================================

    if is_macro_noise and not matched_stocks:

        score = min(score, 3)

    # ==================================================
    # 四、没有明确股票时，限制最高分
    # ==================================================

    if not matched_stocks:

        score = min(score, 15)

    # ==================================================
    # 五、关注等级
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

    news["score_reasons"] = list(
        dict.fromkeys(reasons)
    )

    return news
