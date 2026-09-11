import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from collections import defaultdict
from html import escape


# ============================================================
# 邮件发送
# ============================================================

def send_email(news_list, sender, password, receiver):

    if not news_list:
        print("没有符合条件的股票/行业新闻")
        return


    # ========================================================
    # 1. 去重
    # ========================================================

    unique_news = []

    seen = set()

    for news in news_list:

        title = news.get("title", "").strip()
        link = news.get("link", "").strip()

        key = title + link

        if key in seen:
            continue

        seen.add(key)

        unique_news.append(news)


    # ========================================================
    # 2. 按重要程度排序
    # ========================================================

    unique_news.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )


    # ========================================================
    # 3. 按股票分类
    # ========================================================

    stock_groups = defaultdict(list)

    industry_groups = defaultdict(list)

    other_news = []


    for news in unique_news:

        matched_stocks = news.get(
            "matched_stocks",
            []
        )

        matched_industries = news.get(
            "matched_industries",
            []
        )


        # -----------------------------------------------
        # 股票分类
        # -----------------------------------------------

        if matched_stocks:

            for stock in matched_stocks:

                stock_key = (
                    stock["name"],
                    stock["code"]
                )

                stock_groups[stock_key].append(news)


        # -----------------------------------------------
        # 行业分类
        # -----------------------------------------------

        if matched_industries:

            for industry in matched_industries:

                industry_groups[industry].append(news)


        # -----------------------------------------------
        # 没有明确股票，但是有行业信息
        # -----------------------------------------------

        if (
            not matched_stocks
            and matched_industries
        ):

            other_news.append(news)


    # ========================================================
    # 4. HTML 页面
    # ========================================================

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="utf-8">

        <style>

            body {{
                font-family:
                    "Microsoft YaHei",
                    Arial,
                    sans-serif;

                line-height: 1.7;

                color: #333;

                background-color: #f5f6f7;

                margin: 0;

                padding: 20px;
            }}


            .container {{
                max-width: 900px;

                margin: auto;

                background: white;

                padding: 25px;

                border-radius: 10px;
            }}


            h1 {{
                margin-top: 0;

                color: #222;

                border-bottom:
                    3px solid #333;

                padding-bottom: 12px;
            }}


            h2 {{
                margin-top: 30px;

                padding-bottom: 8px;

                border-bottom:
                    2px solid #ddd;

                color: #222;
            }}


            h3 {{
                margin-bottom: 10px;

                color: #333;
            }}


            .summary {{
                background: #f7f7f7;

                padding: 15px;

                border-radius: 8px;

                margin-bottom: 20px;
            }}


            .important {{
                border-left:
                    5px solid #d93025;

                background: #fff5f5;
            }}


            .normal {{
                border-left:
                    5px solid #777;

                background: #fafafa;
            }}


            .news-item {{
                margin: 12px 0;

                padding: 15px;

                border-radius: 7px;
            }}


            .news-title {{
                font-size: 16px;

                font-weight: bold;

                margin-bottom: 8px;
            }}


            .news-body {{
                color: #555;

                font-size: 14px;

                margin-top: 8px;
            }}


            .meta {{
                font-size: 13px;

                color: #777;

                margin-top: 8px;
            }}


            .score {{
                font-weight: bold;

                color: #c62828;
            }}


            .stock-tag {{
                display: inline-block;

                padding: 3px 8px;

                margin: 2px;

                background: #eee;

                border-radius: 4px;

                font-size: 13px;
            }}


            .industry-tag {{
                display: inline-block;

                padding: 3px 8px;

                margin: 2px;

                background: #f1f1f1;

                border-radius: 4px;

                font-size: 13px;
            }}


            .reason {{
                color: #b71c1c;

                font-size: 13px;
            }}


            .link {{
                display: inline-block;

                margin-top: 8px;

                color: #1565c0;

                text-decoration: none;
            }}


            .footer {{
                margin-top: 30px;

                padding-top: 15px;

                border-top: 1px solid #ddd;

                color: #888;

                font-size: 12px;
            }}

        </style>

    </head>


    <body>

    <div class="container">

        <h1>📈 每日股票情报</h1>

        <div class="summary">

            <strong>
                抓取时间：
            </strong>

            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            <br>

            <strong>
                相关信息：
            </strong>

            {len(unique_news)} 条

        </div>
    """


    # ========================================================
    # 5. 今日重点
    # ========================================================

    important_news = [
        news
        for news in unique_news
        if news.get("score", 0) >= 12
    ]


    html_content += f"""

        <h2>🔥 今日重点（{len(important_news)}条）</h2>

    """


    if important_news:

        for news in important_news[:20]:

            html_content += build_news_html(
                news,
                important=True
            )

    else:

        html_content += """

        <p>
            今日暂未发现高重要程度新闻。
        </p>

        """


    # ========================================================
    # 6. 按股票展示
    # ========================================================

    html_content += """

        <h2>📌 我的关注股票</h2>

    """


    for stock_key, items in stock_groups.items():

        stock_name, stock_code = stock_key

        # 去重

        items = unique_by_title(items)

        # 按评分排序

        items.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )


        html_content += f"""

        <h3>
            {escape(stock_name)}
            ({escape(stock_code)})
        </h3>

        """


        # 每只股票最多显示10条

        for news in items[:10]:

            html_content += build_news_html(
                news,
                important=(
                    news.get("score", 0) >= 12
                )
            )


    # ========================================================
    # 7. 行业动态
    # ========================================================

    html_content += """

        <h2>🏭 行业动态</h2>

    """


    for industry, items in industry_groups.items():

        items = unique_by_title(items)

        items.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )


        html_content += f"""

        <h3>
            {escape(industry)}
        </h3>

        """


        for news in items[:8]:

            html_content += build_news_html(
                news,
                important=(
                    news.get("score", 0) >= 12
                )
            )


    # ========================================================
    # 8. 邮件结尾
    # ========================================================

    html_content += """

        <div class="footer">

            本邮件由个人股票新闻监控程序自动生成。<br>

            新闻内容仅用于信息整理，
            不构成投资建议。

        </div>

    </div>

    </body>

    </html>

    """


    # ========================================================
    # 9. 创建邮件
    # ========================================================

    msg = MIMEMultipart()

    msg["From"] = sender

    msg["To"] = receiver

    msg["Subject"] = Header(
        f"📈 每日股票情报 - "
        f"{datetime.now().strftime('%Y-%m-%d')}",
        "utf-8"
    )


    msg.attach(
        MIMEText(
            html_content,
            "html",
            "utf-8"
        )
    )


    # ========================================================
    # 10. 通过163 SMTP发送
    # ========================================================

    with smtplib.SMTP_SSL(
        "smtp.163.com",
        465
    ) as server:

        server.login(
            sender,
            password
        )

        server.sendmail(
            sender,
            [receiver],
            msg.as_string()
        )


    print(
        f"邮件发送成功，"
        f"共 {len(unique_news)} 条股票/行业信息"
    )


# ============================================================
# 新闻HTML生成
# ============================================================

def build_news_html(news, important=False):

    title = escape(
        news.get("title", "")
    )

    body = news.get(
        "body",
        ""
    )

    body = escape(body)

    # 最多显示500字
    if len(body) > 500:

        body = body[:500] + "..."


    link = escape(
        news.get("link", "")
    )

    source = escape(
        news.get("source", "")
    )

    score = news.get(
        "score",
        0
    )

    level = escape(
        news.get(
            "level",
            "普通信息"
        )
    )


    # ========================================================
    # 股票标签
    # ========================================================

    stock_tags = ""

    for stock in news.get(
        "matched_stocks",
        []
    ):

        stock_tags += f"""
        <span class="stock-tag">
            {escape(stock["name"])}
            {escape(stock["code"])}
        </span>
        """


    # ========================================================
    # 行业标签
    # ========================================================

    industry_tags = ""

    for industry in news.get(
        "matched_industries",
        []
    ):

        industry_tags += f"""
        <span class="industry-tag">
            {escape(industry)}
        </span>
        """


    # ========================================================
    # 评分原因
    # ========================================================

    reasons = news.get(
        "score_reasons",
        []
    )


    reason_text = ""

    if reasons:

        reason_text = (
            "关注原因："
            + "、".join(
                escape(str(x))
                for x in reasons
            )
        )


    css_class = (
        "important"
        if important
        else "normal"
    )


    return f"""

    <div class="news-item {css_class}">

        <div class="news-title">

            {title}

        </div>


        <div>

            {stock_tags}

            {industry_tags}

        </div>


        <div class="meta">

            <span class="score">
                {level} · {score}分
            </span>

            &nbsp;&nbsp;

            来源：
            {source}

        </div>


        <div class="news-body">

            {body}

        </div>


        <div class="reason">

            {reason_text}

        </div>


        <a
            class="link"
            href="{link}"
            target="_blank"
        >
            查看原文 →
        </a>

    </div>

    """


# ============================================================
# 去重
# ============================================================

def unique_by_title(news_list):

    result = []

    seen = set()

    for news in news_list:

        title = news.get(
            "title",
            ""
        ).strip()

        if title in seen:
            continue

        seen.add(title)

        result.append(news)

    return result
