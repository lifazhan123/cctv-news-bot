import html
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(
    news_list,
    sender,
    password,
    receiver
):

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    subject = (
        f"📈 每日股票情报 - {today}"
    )

    # =====================================
    # 去重
    # =====================================

    unique_news = {}

    for news in news_list:

        key = (
            news.get("title", ""),
            news.get("link", "")
        )

        if key not in unique_news:

            unique_news[key] = news

    news_list = list(
        unique_news.values()
    )

    # =====================================
    # 排序
    # =====================================

    news_list.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True
    )

    # =====================================
    # 分类
    # =====================================

    important_news = []

    stock_news = []

    military_news = []

    industry_news = []

    for news in news_list:

        if news.get("score", 0) >= 15:

            important_news.append(
                news
            )

        if news.get(
            "matched_stocks"
        ):

            stock_news.append(
                news
            )

        if news.get(
            "matched_military_keywords"
        ):

            military_news.append(
                news
            )

        if (
            news.get(
                "matched_industries"
            )
            and not news.get(
                "matched_stocks"
            )
            and not news.get(
                "matched_military_keywords"
            )
        ):

            industry_news.append(
                news
            )

    # =====================================
    # HTML
    # =====================================

    html_content = f"""
    <html>
    <body>

    <h2>📈 每日股票情报</h2>

    <p>
        日期：{today}
    </p>

    <hr>

    """

    # =====================================
    # 今日重点
    # =====================================

    html_content += """
    <h3>🔥 今日重点</h3>
    """

    if important_news:

        for index, news in enumerate(
            important_news[:10],
            1
        ):

            title = html.escape(
                news.get(
                    "title",
                    ""
                )
            )

            link = html.escape(
                news.get(
                    "link",
                    ""
                ),
                quote=True
            )

            level = html.escape(
                news.get(
                    "level",
                    ""
                )
            )

            score = news.get(
                "score",
                0
            )

            html_content += f"""
            <p>
            <b>
            {index}. {level}
            </b>
            【{score}分】
            <br>
            <a href="{link}">
            {title}
            </a>
            </p>
            """

    else:

        html_content += """
        <p>暂无重点信息</p>
        """

    # =====================================
    # 我的关注股票
    # =====================================

    html_content += """
    <hr>
    <h3>📌 我的关注股票</h3>
    """

    if stock_news:

        for index, news in enumerate(
            stock_news[:20],
            1
        ):

            title = html.escape(
                news.get(
                    "title",
                    ""
                )
            )

            link = html.escape(
                news.get(
                    "link",
                    ""
                ),
                quote=True
            )

            score = news.get(
                "score",
                0
            )

            names = [
                item["name"]
                for item in news.get(
                    "matched_stocks",
                    []
                )
            ]

            names_text = "、".join(
                names
            )

            reasons = "、".join(
                news.get(
                    "score_reasons",
                    []
                )
            )

            html_content += f"""
            <p>
            <b>
            {index}. {names_text}
            【{score}分】
            </b>
            <br>
            <a href="{link}">
            {title}
            </a>
            <br>
            关注原因：{html.escape(reasons)}
            </p>
            """

    else:

        html_content += """
        <p>暂无直接涉及关注股票的信息</p>
        """

    # =====================================
    # 军事情报
    # =====================================

    html_content += """
    <hr>
    <h3>🪖 军事 / 战争 / 军工情报</h3>
    """

    if military_news:

        for index, news in enumerate(
            military_news[:20],
            1
        ):

            title = html.escape(
                news.get(
                    "title",
                    ""
                )
            )

            link = html.escape(
                news.get(
                    "link",
                    ""
                ),
                quote=True
            )

            score = news.get(
                "score",
                0
            )

            level = html.escape(
                news.get(
                    "level",
                    ""
                )
            )

            keywords = "、".join(
                news.get(
                    "matched_military_keywords",
                    []
                )
            )

            reasons = "、".join(
                news.get(
                    "score_reasons",
                    []
                )
            )

            html_content += f"""
            <p>
            <b>
            {index}. {level}
            【{score}分】
            </b>
            <br>
            <a href="{link}">
            {title}
            </a>
            <br>
            军事关键词：
            {html.escape(keywords)}
            <br>
            关注原因：
            {html.escape(reasons)}
            </p>
            """

    else:

        html_content += """
        <p>暂无军事 / 战争 / 军工相关信息</p>
        """

    # =====================================
    # 行业动态
    # =====================================

    html_content += """
    <hr>
    <h3>🏭 行业动态</h3>
    """

    if industry_news:

        for index, news in enumerate(
            industry_news[:20],
            1
        ):

            title = html.escape(
                news.get(
                    "title",
                    ""
                )
            )

            link = html.escape(
                news.get(
                    "link",
                    ""
                ),
                quote=True
            )

            score = news.get(
                "score",
                0
            )

            industries = "、".join(
                news.get(
                    "matched_industries",
                    []
                )
            )

            html_content += f"""
            <p>
            <b>
            {index}. {industries}
            【{score}分】
            </b>
            <br>
            <a href="{link}">
            {title}
            </a>
            </p>
            """

    else:

        html_content += """
        <p>暂无行业动态</p>
        """

    # =====================================
    # 页脚
    # =====================================

    html_content += """
    <hr>

    <p style="color:gray;">
    本邮件为个人信息整理工具自动生成，
    仅用于新闻及行业信息跟踪，
    不构成任何投资建议。
    </p>

    </body>
    </html>
    """

    # =====================================
    # 创建邮件
    # =====================================

    message = MIMEMultipart(
        "alternative"
    )

    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver

    message.attach(
        MIMEText(
            html_content,
            "html",
            "utf-8"
        )
    )

    # =====================================
    # 163 SMTP
    # =====================================

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
            receiver,
            message.as_string()
        )

    print(
        f"邮件发送成功，共 "
        f"{len(news_list)} 条股票/行业/军事信息"
    )
