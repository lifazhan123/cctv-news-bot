import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from collections import defaultdict

# 你关心的关键词
KEYWORDS = ['股票', '股市', 'A股', '战争', '冲突', '伊朗', '美国', '生活',
            '消费', '人口', 'CPI', 'PPI', '经济', '民生', '油价', '房价']


def filter_news(news_list):
    filtered = []
    for news in news_list:
        content = news['title'] + news['body']
        if any(kw in content for kw in KEYWORDS):
            filtered.append(news)
    return filtered


def send_email(news_list, sender, password, receiver):
    if not news_list:
        print("没有符合条件的新闻")
        return

    grouped = defaultdict(list)
    for news in news_list:
        grouped[news['source']].append(news)

    html_content = f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        h2 {{ color: #c00; border-bottom: 2px solid #c00; padding-bottom: 5px; }}
        .news-item {{ margin-bottom: 25px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .news-title {{ font-size: 16px; font-weight: bold; color: #333; }}
        .news-body {{ color: #555; margin-top: 10px; }}
        .news-link {{ color: #0066cc; text-decoration: none; }}
    </style></head><body>
    <h1>每日新闻推送</h1>
    <p>抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    for source, items in grouped.items():
        html_content += f"<h2>{source}（{len(items)}条）</h2>"
        for news in items:
            body_preview = news['body'][:500] + '...' if len(news['body']) > 500 else news['body']
            html_content += f"""
            <div class="news-item">
                <div class="news-title">{news['title']}</div>
                <div class="news-body">{body_preview}</div>
                <a class="news-link" href="{news['link']}">查看详情 →</a>
            </div>
            """

    html_content += "</body></html>"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = Header(f"每日新闻推送 - {datetime.now().strftime('%Y-%m-%d')}", 'utf-8')
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.163.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [receiver], msg.as_string())
    print(f"邮件发送成功，共 {len(news_list)} 条新闻")
