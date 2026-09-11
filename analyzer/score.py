from analyzer.filter import count_keyword_hits


# ==========================================================
# 公司重大事件
# ==========================================================

COMPANY_MAJOR_KEYWORDS = [
    "重大合同",
    "重大订单",
    "中标",
    "签署重大合同",
    "签订重大合同",
    "战略合作",
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


# ==========================================================
# 公司经营信息
# ==========================================================

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


# ==========================================================
# 公司技术信息
# ==========================================================

COMPANY_TECH_KEYWORDS = [
    "技术突破",
    "研发成功",
    "新产品",
    "新技术",
    "产品发布",
    "首批",
    "首次",
    "量产",
    "国产替代",
]


# ==========================================================
# 行业重大变化
# ==========================================================

INDUSTRY_MAJOR_KEYWORDS = [
    "行业政策",
    "产业政策",
    "发展规划",
    "指导意见",
    "实施方案",
    "专项行动",
    "国家战略",
    "重大改革",
    "价格上涨",
    "价格下跌",
    "价格大涨",
    "价格大跌",
    "供需变化",
    "供需紧张",
    "产能过剩",
    "产能退出",
]


# ==========================================================
# 行业重要信息
# ==========================================================

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
]


# ==========================================================
# 政策机构
# ==========================================================

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


# ==========================================================
# 宏观新闻降权关键词
# ==========================================================

MACRO_NEWS_KEYWORDS = [
    "会谈",
    "致辞",
    "访问",
    "外交",
    "国际合作",
    "友好交流",
    "两国",
    "国际社会",
    "全球发展",
    "人文交流",
]


def calculate_score(news):

    title = news.get("title", "")
    body = news.get("body", "")

    content = f"{title} {body}"

    matched_stocks = news.get("matched_stocks", [])
    matched_industries = news.get("matched_industries", [])

    score = 0
    reasons = []

    # ======================================================
    # 一、明确涉及关注股票
    # ======================================================

    if matched_stocks:

        # 基础分
        score += 15
        reasons.append("涉及关注股票")

        # 标题直接出现股票
        title_stock = False

        for stock in matched_stocks:

            if stock.get("match_type") == "标题":
                title_stock = True
                break

        if title_stock:
            score += 10
            reasons.append("标题涉及公司")

        # 公司重大事件
        major_hits = count_keyword_hits(
            news,
            COMPANY_MAJOR_KEYWORDS
        )

        if major_hits:
            score += min(len(major_hits) * 10, 30)

            reasons.extend(major_hits)

        # 公司经营
        operation_hits = count_keyword_hits(
            news,
            COMPANY_OPERATION_KEYWORDS
        )

        if operation_hits:
            score += min(len(operation_hits) * 6, 18)

            reasons.extend(operation_hits)

        # 公司技术
        tech_hits = count_keyword_hits(
            news,
            COMPANY_TECH_KEYWORDS
        )

        if tech_hits:
            score += min(len(tech_hits) * 5, 15)

            reasons.extend(tech_hits)

    # ======================================================
    # 二、没有明确股票，但涉及行业
    # ======================================================

    elif matched_industries:

        # 行业基础分很低
        score += 2

        # 行业重大变化
        major_hits = count_keyword_hits(
            news,
            INDUSTRY_MAJOR_KEYWORDS
        )

        if major_hits:

            score += min(len(major_hits) * 6, 18)

            reasons.extend(major_hits)

        # 行业重要变化
        important_hits = count_keyword_hits(
            news,
            INDUSTRY_IMPORTANT_KEYWORDS
        )

        if important_hits:

            score += min(len(important_hits) * 4, 12)

            reasons.extend(important_hits)

        # 国家部委等政策信息
        policy_hits = count_keyword_hits(
            news,
            POLICY_KEYWORDS
        )

        if policy_hits:

            score += 5

            reasons.append("政策信息")

    # ======================================================
    # 三、宏观新闻降权
    # ======================================================

    macro_hits = count_keyword_hits(
        news,
        MACRO_NEWS_KEYWORDS
    )

    if macro_hits:

        # 没有股票直接关联时，
        # 宏观新闻不能获得很高分
        if not matched_stocks:

            score = min(score, 8)

        reasons.append("宏观信息")

    # ======================================================
    # 四、新闻联播标题异常处理
    # ======================================================

    if title in [
        "CCTV-1新闻",
        "CCTV-2新闻",
        "CCTV-13新闻",
    ]:

        # 标题提取异常时，
        # 不允许仅凭正文获得高分
        if not matched_stocks:

            score = min(score, 8)

    # ======================================================
    # 五、限制行业新闻最高评分
    # ======================================================

    if not matched_stocks:

        score = min(score, 15)

    # ======================================================
    # 六、确定等级
    # ======================================================

    if score >= 30:

        level = "🔥 重点关注"

    elif score >= 15:

        level = "⭐ 值得关注"

    elif score >= 6:

        level = "📌 一般关注"

    else:

        level = "普通信息"

    # ======================================================
    # 七、整理原因
    # ======================================================

    reasons = list(dict.fromkeys(reasons))

    news["score"] = score
    news["level"] = level
    news["score_reasons"] = reasons

    return news
