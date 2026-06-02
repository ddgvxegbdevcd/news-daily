#!/usr/bin/env python3

import feedparser
import json
import requests
import trafilatura

from datetime import datetime

# =========================
# RSS源
# =========================

SOURCES = {
    "bloomberg": {
        "name": "Bloomberg",
        "name_cn": "彭博社",
        "rss": "https://feeds.bloomberg.com/markets/news.rss",
    },
    "cnbc": {
        "name": "CNBC",
        "name_cn": "CNBC",
        "rss": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    },
    "ft": {
        "name": "Financial Times",
        "name_cn": "金融时报",
        "rss": "https://news.google.com/rss/search?q=site:ft.com&hl=en-US&gl=US&ceid=US:en",
    },
    "reuters": {
        "name": "Reuters",
        "name_cn": "路透社",
        "rss": "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en",
    },
}

# =========================
# 解析真实链接
# =========================

def get_real_url(url):

    try:

        r = requests.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        return r.url

    except Exception:

        return url


# =========================
# 抓正文
# =========================

def fetch_article_content(url):

    try:

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:

            return ""

        content = trafilatura.extract(
            downloaded,
            include_links=False,
            include_images=False,
            include_tables=False
        )

        return content if content else ""

    except Exception as e:

        print("正文抓取失败:", e)

        return ""


# =========================
# 主程序
# =========================

def main():

    all_news = []

    for source_id, source_info in SOURCES.items():

        print(f"\n开始抓取 {source_info['name_cn']}")

        try:

            feed = feedparser.parse(
                source_info["rss"]
            )

            count = 0

            for entry in feed.entries:

                if count >= 5:
                    break

                title = getattr(
                    entry,
                    "title",
                    ""
                )

                link = getattr(
                    entry,
                    "link",
                    ""
                )

                publish_time = getattr(
                    entry,
                    "published",
                    ""
                )

                summary = getattr(
                    entry,
                    "summary",
                    ""
                )

                real_url = get_real_url(link)

                print(
                    "抓取:",
                    title[:50]
                )

                content = fetch_article_content(
                    real_url
                )

                news_item = {

                    "source":
                    source_info["name"],

                    "source_cn":
                    source_info["name_cn"],

                    "title":
                    title,

                    "url":
                    real_url,

                    "publish_time":
                    publish_time,

                    "summary":
                    summary,

                    "content":
                    content,

                    "content_length":
                    len(content)
                }

                all_news.append(
                    news_item
                )

                count += 1

        except Exception as e:

            print(
                f"抓取失败 {source_info['name_cn']}:",
                e
            )

    # =========================
    # news.json
    # =========================

    with open(
        "news.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "update_time":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "news_count":
                len(all_news),

                "news":
                all_news
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    # =========================
    # news.md
    # =========================

    md = []

    md.append("# 每日财经新闻\n")

    md.append(
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    for news in all_news:

        md.append(
            f"## {news['title']}\n"
        )

        md.append(
            f"来源：{news['source_cn']}\n"
        )

        md.append(
            f"链接：{news['url']}\n"
        )

        md.append(
            f"正文长度：{news['content_length']}\n"
        )

        if news["summary"]:

            md.append(
                f"摘要：{news['summary']}\n"
            )

        if news["content"]:
            # 这里的正文会自带折叠效果
            md.append("<details>")
            md.append("<summary><b>👉 点击展开 / 收起正文</b></summary>\n")
            md.append(f"> {news['content']}\n")
            md.append("</details>\n")

        md.append("\n---\n")

    with open(
        "news.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(md)
        )

    # =========================
    # 额外保存一份按日期归档的历史文件
    # =========================
    today_date = datetime.now().strftime("%Y-%m-%d")
    archive_filename = f"news_{today_date}.md"
    
    with open(
        archive_filename,
        "w",
        encoding="utf-8"
    ) as f:
        f.write("\n".join(md))


    print(
        f"\n完成，共抓取 {len(all_news)} 条新闻"
    )


if __name__ == "__main__":

    main()