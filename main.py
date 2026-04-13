import os
import feedparser
import google.generativeai as genai
import json
from datetime import datetime
import re

# 設定：収集したいサブレディット
SUBS = ["Prompt", "GPT", "Claude","gemini","grok","xAI"]

def fetch_reddit_rss():
    print("[*] Redditからデータを取得中...")
    all_posts = []
    for sub in SUBS:
        url = f"https://www.reddit.com/r/{sub}/hot.rss"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                all_posts.append({
                    "sub": sub,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary[:1000] # 要約を抽出（長すぎ防止）
                })
        except Exception as e:
            print(f"[-] {sub} のRSS取得に失敗しました: {e}")
    return all_posts

def analyze_with_gemini(posts, api_key):
    print("[*] Geminiで解析中...")
    genai.configure(api_key=api_key)
    # 最新SDKに対応したモデル名を指定
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    あなたはプロンプトエンジニアリングの専門家です。
    以下のReddit投稿リストから、実用的な「プロンプトのテクニック（ハック）」を抽出し、日本語で整理してください。
    雑談は無視し、具体的な手法があるものだけを残してください。

    出力形式は必ず以下のJSON配列のみにしてください：
    [ {{"name": "技法名", "desc": "解説", "example": "例", "url": "URL"}} ]

    データ: {json.dumps(posts, ensure_ascii=False)}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # エラー対策：不要なMarkdown記法 (```json など) を削除
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        
        # 配列のカッコ [...] の中身だけを抽出
        json_text = text[text.find("["):text.rfind("]")+1]
        
        return json.loads(json_text)
    except Exception as e:
        print(f"[-] AIの回答パースに失敗しました: {e}")
        # デバッグ用に生の回答を出力
        if 'response' in locals():
            print(f"[-] Geminiの生の回答: {response.text}")
        return []

def save_to_markdown(hacks):
    if not hacks:
        print("[!] 有益なハックが見つからなかったため、ファイルの保存をスキップします。")
        return
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/hacks_{date_str}.md"
    
    # フォルダがなければ作成
    os.makedirs("reports", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Prompt Hacks - {date_str}\n\n")
        for h in hacks:
            f.write(f"## {h['name']}\n")
            f.write(f"- **解説**: {h['desc']}\n")
            f.write(f"- **例**:\n```text\n{h['example']}\n```\n")
            f.write(f"- **ソース**: [Reddit]({h['url']})\n\n---\n")
    print(f"[+] {filename} に保存しました。")

if __name__ == "__main__":
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[!] GEMINI_API_KEY が設定されていません。")
    else:
        posts = fetch_reddit_rss()
        print(f"[*] {len(posts)} 件の投稿を取得しました。")
        
        if posts:
            hacks = analyze_with_gemini(posts, gemini_key)
            print(f"[*] AIが {len(hacks)} 件のハックを抽出しました。")
            save_to_markdown(hacks)
        else:
            print("[!] Redditからデータを取得できなかったため終了します。")
    [ {{"name": "技法名", "desc": "解説", "example": "例", "url": "URL"}} ]

    データ: {json.dumps(posts, ensure_ascii=False)}
    """
    
    response = model.generate_content(prompt)
    # JSON部分を抽出
    try:
        json_text = response.text[response.text.find("["):response.text.rfind("]")+1]
        return json.loads(json_text)
    except:
        print("[-] AIの回答パースに失敗しました。")
        return []

def save_to_markdown(hacks):
    if not hacks:
        print("[!] 有益なハックが見つかりませんでした。")
        return
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/hacks_{date_str}.md"
    os.makedirs("reports", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Prompt Hacks - {date_str}\n\n")
        for h in hacks:
            f.write(f"## {h['name']}\n")
            f.write(f"- **解説**: {h['desc']}\n")
            f.write(f"- **例**:\n```text\n{h['example']}\n```\n")
            f.write(f"- **ソース**: [Reddit]({h['url']})\n\n---\n")
    print(f"[+] {filename} に保存しました。")

if __name__ == "__main__":
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[!] GEMINI_API_KEY が設定されていません。")
    else:
        posts = fetch_reddit_rss()
        hacks = analyze_with_gemini(posts, gemini_key)
        save_to_markdown(hacks)
