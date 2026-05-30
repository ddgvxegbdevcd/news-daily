#!/usr/bin/env python3
"""
每日抓取路透社、彭博社、华尔街日报头条
通过 Google News RSS 聚合（从 GitHub Actions 美国服）
"""
import feedparser
import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
import trafilatura
import requests
from bs4 import BeautifulSoup

# ========== 新闻源配置 ==========
SOURCES = {
    "reuters": {
        "name": "Reuters",
        "name_cn": "路透社",
        "rss": "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en",
    },
    "bloomberg": {
        "name": "Bloomberg",
        "name_cn": "彭博社",
        "rss": "https://news.google.com/rss/search?q=site:bloomberg.com&hl=en-US&gl=US&ceid=US:en",
    },
    "wsj": {
        "name": "Wall Street Journal",
        "name_cn": "华尔街日报",
        "rss": "https://news.google.com/rss/search?q=site:wsj.com&hl=en-US&gl=US&ceid=US:en",
    },
    "ft": {
        "name": "Financial Times",
        "name_cn": "金融时报",
        "rss": "https://news.google.com/rss/search?q=site:ft.com&hl=en-US&gl=US&ceid=US:en",
    },
    "cnbc": {
        "name": "CNBC",
        "name_cn": "消费者新闻与商业频道",
        "rss": "https://news.google.com/rss/search?q=site:cnbc.com&hl=en-US&gl=US&ceid=US:en",
    }
}

# ========== 正文抓取函数 ==========
def fetch_article_content(url):
    """从文章URL提取完整正文"""
    try:
        print(f"📄 正在提取正文: {url}")
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded, include_links=False, include_images=False)
            return content if content else "无法提取正文"
        return "无法访问文章页面"
    except Exception as e:
        print(f"❌ 提取正文失败: {e}")
        return "提取正文时出错"

# ========== 主函数 ==========
def main():
    all_news = []
    
    for source_id, source_info in SOURCES.items():
        print(f"\n🔍 正在抓取 {source_info['name_cn']} 的新闻...")
        
        try:
            # 解析RSS源
            feed = feedparser.parse(source_info['rss'])
            
            for entry in feed.entries[:5]:  # 每个新闻源取前5条
                news_item = {
                    "source": source_info['name'],
                    "source_cn": source_info['name_cn'],
                    "title": entry.title,
                    "url": entry.link,
                    "publish_time": entry.published,
                    "summary": entry.summary if hasattr(entry, 'summary') else "",
                    "content": fetch_article_content(entry.link)  # 新增：抓取完整正文
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"❌ 抓取 {source_info['name_cn']} 失败: {e}")
            continue
    
    # 保存为JSON文件
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump({
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "news_count": len(all_news),
            "news": all_news
        }, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown文件
    md_content = f"# 每日财经新闻\n\n**更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n"
    
    for source_id, source_info in SOURCES.items():
        source_news = [n for n in all_news if n['source'] == source_info['name']]
        if not source_news:
            continue
            
        md_content += f"## {source_info['name_cn']}\n\n"
        
        for i, news in enumerate(source_news, 1):
            md_content += f"### {i}. [{news['title']}]({news['url']})\n\n"
            md_content += f"**发布时间：** {news['publish_time']}\n\n"
            
            if news['summary']:
                md_content += f"**摘要：** {news['summary']}\n\n"
            
            if news['content'] and news['content'] not in ["无法提取正文", "无法访问文章页面", "提取正文时出错"]:
                md_content += f"**正文：**\n\n{news['content']}\n\n"
            
            md_content += "---\n\n"
    
    with open('news.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ 抓取完成！共获取 {len(all_news)} 条新闻")

if __name__ == "__main__":
    main()