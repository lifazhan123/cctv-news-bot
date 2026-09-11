from analyzer.filter import count_keyword_hits


# =========================================
# 公司重大信息
# =========================================

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


# =========================================
# 行业信息
# =========================================

INDUSTRY_MAJOR_KEYWORDS = [
    "行业政策",
    "产业政策",
    "发展规划",
    "指导意见",
    "实施方案",
    "专项行动",
    "监管政策",
    "政策调整",
    "价格上涨",
    "价格下跌",
    "价格大涨",
    "价格大跌",
    "价格调整",
    "供需",
    "供需紧张",
    "产能过剩",
    "产能退出",
]


INDUSTRY_IMPORTANT_KEYWORDS = [
    "需求增长",
    "需求下降",
    "市场规模",
    "投资增长",
    "投资下降",
    "出口增长",
    "出口下降",
    "装机容量",
    "新增装机",
    "产量增长",
    "产量下降",
    "成本下降",
    "成本上升",
    "产业链",
    "供应链",
    "产能扩张",
    "新增产能",
    "重大项目",
    "重大工程",
    "重大突破",
    "技术突破",
    "首次实现",
    "实现量产",
    "商业化",
    "新能源装机",
    "储能",
    "充电基础设施",
    "数字电网",
]


# =========================================
# 政策
# =========================================

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


# =========================================
# 军事 / 战争 / 军工
# =========================================

MILITARY_MAJOR_KEYWORDS = [
    "战争",
    "军事冲突",
    "武装冲突",
    "军事行动",
    "空袭",
    "导弹",
    "高超音速",
    "军费",
    "国防预算",
    "军工订单",
    "装备采购",
    "装备列装",
    "批量生产",
    "重大军演",
    "联合军演",
]


MILITARY_IMPORTANT_KEYWORDS = [
    "军工",
    "国防",
    "武器装备",
    "无人机",
    "无人作战",
    "无人系统",
    "雷达",
    "红外",
    "红外探测",
    "热成像",
    "光电",
    "电子战",
    "电子对抗",
    "战斗机",
    "歼击机",
    "轰炸机",
    "预警机",
    "航母",
    "军舰",
    "舰艇",
    "潜艇",
    "军品",
    "军工企业",
    "军工集团",
    "装备研发",
    "装备试验",
    "装备定型",
]


def calculate_score(news):

    matched_stocks = news.get(
        "matched_stocks",
        []
    )

    matched_industries = news.get(
        "matched_industries",
        []
    )

    military_keywords = news.get(
        "matched_military_keywords",
        []
    )

    score = 0

    reasons = []

    # =====================================
    # 关注股票
    # =====================================

    if matched_stocks:

        score += 15

        reasons.append(
            "涉及关注股票"
        )

        for stock in matched_stocks:

            if stock.get("match_type") == "标题":

                score += 10

                reasons.append(
                    "标题涉及公司"
                )

                break

        major_hits = count_keyword_hits(
            news,
            COMPANY_MAJOR_KEYWORDS
        )

        if major_hits:

            score += min(
                len(major_hits) * 10,
                30
            )

            reasons.extend(
                major_hits
            )

        operation_hits = count_keyword_hits(
            news,
            COMPANY_OPERATION_KEYWORDS
        )

        if operation_hits:

            score += min(
                len(operation_hits) * 6,
                18
            )

            reasons.extend(
                operation_hits
            )

        tech_hits = count_keyword_hits(
            news,
            COMPANY_TECH_KEYWORDS
        )

        if tech_hits:

            score += min(
                len(tech_hits) * 5,
                15
            )

            reasons.extend(
                tech_hits
            )

    # =====================================
    # 行业信息
    # =====================================

    elif matched_industries:

        score += 2

        reasons.append(
            "涉及相关行业"
        )

        major_hits = count_keyword_hits(
            news,
            INDUSTRY_MAJOR_KEYWORDS
        )

        if major_hits:

            score += min(
                len(major_hits) * 6,
                18
            )

            reasons.extend(
                major_hits
            )

        important_hits = count_keyword_hits(
            news,
            INDUSTRY_IMPORTANT_KEYWORDS
        )

        if important_hits:

            score += min(
                len(important_hits) * 4,
                12
            )

            reasons.extend(
                important_hits
            )

        policy_hits = count_keyword_hits(
            news,
            POLICY_KEYWORDS
        )

        if policy_hits:

            score += 5

            reasons.append(
                "政策信息"
            )

    # =====================================
    # 军事 / 战争 / 军工信息
    # =====================================

    if military_keywords:

        score += 5

        reasons.append(
            "央视军事信息"
        )

        # 重大军事关键词
        major_hits = [
            keyword
            for keyword in MILITARY_MAJOR_KEYWORDS
            if keyword in military_keywords
        ]

        if major_hits:

            score += min(
                len(major_hits) * 8,
                30
            )

            reasons.extend(
                major_hits
            )

        # 普通重要军事关键词
        important_hits = [
            keyword
            for keyword in MILITARY_IMPORTANT_KEYWORDS
            if keyword in military_keywords
        ]

        if important_hits:

            score += min(
                len(important_hits) * 4,
                20
            )

            reasons.extend(
                important_hits
            )

        # 军事新闻同时涉及关注股票
        if matched_stocks:

            score += 15

            reasons.append(
                "军事信息涉及关注股票"
            )

        # 标题命中重大军事关键词
        title = news.get(
            "title",
            ""
        )

        title_hits = [
            keyword
            for keyword in MILITARY_MAJOR_KEYWORDS
            if keyword in title
        ]

        if title_hits:

            score += 10

            reasons.append(
                "标题涉及重要军事信息"
            )

    # =====================================
    # 非股票信息最高20分
    # =====================================

    if not matched_stocks:

        score = min(
            score,
            20
        )

    # =====================================
    # 重要程度
    # =====================================

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
