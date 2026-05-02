#!/usr/bin/env python3
"""
BEP Post Generator - ユーザー認証・支払い管理対応版
X 投稿自動化ツール
"""

import streamlit as st
import requests
import json
from datetime import datetime
import feedparser
import urllib.parse
import os
from dotenv import load_dotenv
from app.auth import register_user, login_user, logout_user
from app.license_manager import check_license_status

# 環境変数を読み込み
load_dotenv()

# ── API キー・トークン定義（環境変数から読み込み）──────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
X_OAUTH2_ACCESS_TOKEN = os.getenv("X_OAUTH2_TOKEN", "")
X_API_ENDPOINT = "https://api.twitter.com/2/tweets"

if not GEMINI_API_KEY or not X_OAUTH2_ACCESS_TOKEN:
    st.error("❌ API キーが .env で設定されていません")
    st.stop()

# ── ニュースソース定義（動作確認済み）──────────────────
NEWS_SOURCES = {
    "🏛️ 産経新聞": "https://news.google.com/rss/search?q=site:sankei.com&hl=ja&gl=JP&ceid=JP:ja",
    "🌍 Axios": "https://feeds.bloomberg.com/markets/news.rss",
    "🚀 Fox News": "https://feeds.foxnews.com/foxnews/latest"
}

# ── Streamlit 設定 ──────────────────────────────────
st.set_page_config(
    page_title="X Post Generator V2",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── カスタム CSS ──────────────────────────────────────
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .stContainer {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
    }

    h1, h2, h3 {
        color: #333333;
        font-weight: 700;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #667eea;
        font-size: 15px;
    }

    .stSelectbox {
        border-radius: 10px;
    }

    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .post-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ── 認証チェック ──────────────────────────────────────
def show_auth_page():
    """ログイン / 新規登録ページ"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("## ログイン")
        email = st.text_input("メールアドレス", key="login_email")
        password = st.text_input("パスワード", type="password", key="login_password")

        if st.button("ログイン", use_container_width=True, type="primary"):
            success, message, user_data = login_user(email, password)
            if success:
                st.session_state.user_id = user_data['user_id']
                st.session_state.email = user_data['email']
                st.session_state.token = user_data['token']
                st.success("✅ ログインしました")
                st.rerun()
            else:
                st.error(f"❌ {message}")

    with col2:
        st.markdown("## 新規登録")
        new_email = st.text_input("メールアドレス", key="register_email")
        new_password = st.text_input("パスワード（8文字以上）", type="password", key="register_password")

        if st.button("登録", use_container_width=True):
            success, message = register_user(new_email, new_password)
            if success:
                st.success(f"✅ {message}")
                st.info("ログインしてください")
            else:
                st.error(f"❌ {message}")

# ユーザーがログインしていなければ認証ページを表示
if "user_id" not in st.session_state:
    st.markdown("""
    <h1 style='text-align: center; color: #667eea;'>🚀 BEP Post Generator</h1>
    <p style='text-align: center; color: #666666;'>X 投稿自動化ツール</p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    show_auth_page()
    st.stop()

# ── ログイン済みの場合、メインアプリを表示 ──────────────
st.markdown("---")

# ユーザー情報とログアウトボタン
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"**ログイン中:** {st.session_state.email}")
with col2:
    if st.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

st.markdown("---")

# ── タイトル ──────────────────────────────────────────
st.markdown("""
<h1 style='text-align: center; color: #667eea; margin-bottom: 10px;'>✨ X Post Generator V2</h1>
<p style='text-align: center; color: #666666; font-size: 15px;'>短文もニュースも、AI が最高の投稿を作成。ワンクリックで X へ。</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 関数定義 ──────────────────────────────────────────
def generate_posts_gemini(claim: str) -> list:
    """Gemini で投稿文を生成"""
    prompt = f"""あなたは X（旧 Twitter）の PRO ライターです。以下の主張をもとに、バズる投稿を 3 パターン作成してください。

条件：
- 各パターンは独立した投稿として完結すること
- 結論を最初に書く
- 一般人にも理解できる言葉を使う
- 攻撃的すぎず、洞察的に
- 最後に問いかけか強め
- マークダウン記号（#、*など）を使わない
- 絵文字は使わない
- 280 文字以内

【主張】
{claim}

以下の形式で出力してください：
【パターン①】
投稿文ここに書く

【パターン②】
投稿文ここに書く

【パターン③】
投稿文ここに書く"""

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            params={"key": GEMINI_API_KEY},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                posts = parse_posts(text)
                return posts if len(posts) == 3 else None
    except Exception as e:
        st.error(f"エラー: {str(e)}")
    return None


def parse_posts(text: str) -> list:
    """生成テキストから 3 つの投稿案を抽出"""
    posts = []
    lines = text.split('\n')
    current_post = ""

    for line in lines:
        if '【パターン' in line:
            if current_post.strip():
                posts.append(current_post.strip())
            current_post = ""
        else:
            current_post += line + "\n"

    if current_post.strip():
        posts.append(current_post.strip())

    return [p.strip() for p in posts[:3]]


def post_to_x(text: str) -> dict:
    """X API v2 で投稿"""
    headers = {
        "Authorization": f"Bearer {X_OAUTH2_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            X_API_ENDPOINT,
            headers=headers,
            json={"text": text},
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            return {
                "success": True,
                "tweet_id": data.get("data", {}).get("id", "")
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_x_compose_url(text: str) -> str:
    """X の公開投稿画面へのリンク"""
    encoded_text = urllib.parse.quote(text)
    return f"https://twitter.com/compose/tweet?text={encoded_text}"


def translate_to_japanese(text: str) -> str:
    """英語を日本語に翻訳（キャッシュ付き）"""
    if not text or len(text) == 0:
        return text

    # セッションにキャッシュがなければ作成
    if "translation_cache" not in st.session_state:
        st.session_state.translation_cache = {}

    # キャッシュをチェック
    if text in st.session_state.translation_cache:
        return st.session_state.translation_cache[text]

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": f"次のテキストを日本語に翻訳してください（翻訳結果のみ出力）:\n{text}"}]}]},
            params={"key": GEMINI_API_KEY},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            translated = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", text).strip()
            st.session_state.translation_cache[text] = translated
            return translated
        else:
            print(f"Translation API Error: {response.status_code} - {response.text}")
            return text
    except Exception as e:
        print(f"Translation Error: {str(e)}")
        return text


def fetch_news(source: str) -> list:
    """RSS フィードから最新ニュース取得"""
    feed_url = NEWS_SOURCES.get(source)
    if not feed_url:
        return []

    try:
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            st.error(f"⚠️ {source} からニュースを取得できません。\n\nURL: {feed_url}")
            return []

        articles = []
        for entry in feed.entries[:5]:
            title = entry.get("title", "")

            # Axios と Fox News の場合は日本語に翻訳
            if source in ["🌍 Axios", "🚀 Fox News"] and title:
                title = translate_to_japanese(title)

            articles.append({
                "title": title,
                "link": entry.get("link", ""),
                "source": source
            })

        return articles
    except Exception as e:
        st.error(f"❌ {source} エラー: {str(e)}")
        return []


# ── ライセンス状態をチェック ────────────────────────────
license_status = check_license_status(st.session_state.user_id)

if not license_status['can_access']:
    st.warning(f"⚠️ {license_status['locked_reason']}")

# ── タブ分け ──────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💭 短文投稿", "📰 ニュース投稿", "⚙️ プロフィール"])

# ════════════════════════════════════════════════════════
# TAB 1: 短文投稿（左右2カラム）
# ════════════════════════════════════════════════════════
with tab1:
    left_col, right_col = st.columns(2)

    # ── 左側：入力フォーム ────────────────────────────────
    with left_col:
        st.markdown("### 入力")

        claim = st.text_area(
            "あなたの主張・意見",
            placeholder="例：「AI 時代こそ、人間にしかできない創造力が重要だ」",
            height=150,
            max_chars=500,
            label_visibility="collapsed"
        )

        if st.button("✨ 投稿案を生成", use_container_width=True, type="primary"):
            if claim.strip():
                with st.spinner("AI が投稿案を作成中..."):
                    posts = generate_posts_gemini(claim)

                    if posts:
                        st.session_state.generated_posts = posts
                        st.session_state.post_type = "claim"
                        st.success("✅ 生成完了！")
                        st.rerun()
                    else:
                        st.error("❌ 生成に失敗しました")
            else:
                st.warning("⚠️ 主張を入力してください")

    # ── 右側：投稿案表示 ──────────────────────────────────
    with right_col:
        st.markdown("### 投稿案")

        if "generated_posts" in st.session_state and st.session_state.post_type == "claim":
            posts = st.session_state.generated_posts

            for idx, post in enumerate(posts, 1):
                st.markdown(f"""
                <div class='post-card'>
                    <strong>案 {idx}</strong><br>
                    <p style='margin: 10px 0; color: #333;'>{post}</p>
                    <small style='color: #999;'>{len(post)} 文字</small>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📤 投稿", key=f"btn_post_{idx}", use_container_width=True):
                        with st.spinner("投稿中..."):
                            result = post_to_x(post)
                            if result["success"]:
                                st.markdown(f"""
                                <div class='success-box'>
                                    <strong>✅ 投稿成功！</strong><br>
                                    ID: {result['tweet_id']}
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.generated_posts = None
                            else:
                                st.error(f"❌ 失敗: {result['error']}")

                with col2:
                    x_url = get_x_compose_url(post)
                    st.link_button("🖼️ 画像・予約", x_url, use_container_width=True, key=f"claim_link_{idx}")
        else:
            st.info("投稿案がまだ生成されていません")

# ════════════════════════════════════════════════════════
# TAB 2: ニュース投稿（左右2カラム）
# ════════════════════════════════════════════════════════
with tab2:
    left_col, right_col = st.columns(2)

    # ── 左側：入力フォーム ────────────────────────────────
    with left_col:
        st.markdown("### ニュース選択")

        news_source = st.selectbox(
            "📰 ニュースソース",
            list(NEWS_SOURCES.keys()),
            label_visibility="collapsed"
        )

        if st.button("📥 ニュース取得", use_container_width=True):
            with st.spinner("ニュースを取得中..."):
                articles = fetch_news(news_source)
                if articles:
                    st.session_state.news_articles = articles
                    st.session_state.selected_article = None
                    st.success(f"✅ {len(articles)} 件取得")
                else:
                    st.warning("⚠️ 取得できませんでした")

        # 記事選択
        if "news_articles" in st.session_state:
            st.markdown("---")
            st.markdown("### 記事を選択")

            articles = st.session_state.news_articles

            for idx, article in enumerate(articles):
                is_selected = st.session_state.get("selected_article") == idx
                button_label = f"{'✅ ' if is_selected else ''}{idx + 1}. {article['title'][:40]}..."

                if is_selected:
                    st.markdown(f"""
                    <div style='background-color: #667eea; padding: 10px; border-radius: 8px; border: 2px solid #ff6b6b; margin: 5px 0;'>
                        <p style='color: white; margin: 0;'>{button_label}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(button_label, use_container_width=True, key=f"news_article_{news_source}_{idx}"):
                        st.session_state.selected_article = idx
                        st.rerun()

        # 意見入力
        if "selected_article" in st.session_state and st.session_state.selected_article is not None:
            if "news_articles" in st.session_state and len(st.session_state.news_articles) > st.session_state.selected_article:
                st.markdown("---")
                article = st.session_state.news_articles[st.session_state.selected_article]

                st.markdown("### あなたの意見")

            opinion = st.text_area(
                "この記事についてどう思いますか？",
                placeholder="例：「この記事は重要なポイントを指摘している」",
                height=100,
                max_chars=300,
                label_visibility="collapsed"
            )

            if st.button("✨ 投稿案を生成", use_container_width=True, type="primary", key="news_generate_posts"):
                if opinion.strip():
                    prompt = f"""以下のニュース記事とユーザーの意見から、X 投稿を 3 パターン作成してください。

【ニュースタイトル】
{article['title']}

【ユーザーの意見】
{opinion}

条件：
- 記事と意見の両方を含める
- 結論を最初に書く
- 280 文字以内
- マークダウン記号、絵文字なし

以下の形式で出力してください：
【パターン①】
投稿文

【パターン②】
投稿文

【パターン③】
投稿文"""

                    with st.spinner("AI が投稿案を作成中..."):
                        response = requests.post(
                            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                            headers={"Content-Type": "application/json"},
                            json={"contents": [{"parts": [{"text": prompt}]}]},
                            params={"key": GEMINI_API_KEY},
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()
                            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            posts = parse_posts(text)

                            st.session_state.generated_posts = posts
                            st.session_state.post_type = "news"
                            st.success("✅ 生成完了！")
                            st.rerun()
                else:
                    st.warning("⚠️ 意見を入力してください")

    # ── 右側：投稿案表示 ──────────────────────────────────
    with right_col:
        st.markdown("### 投稿案")

        if "generated_posts" in st.session_state and st.session_state.post_type == "news":
            posts = st.session_state.generated_posts

            for idx, post in enumerate(posts, 1):
                st.markdown(f"""
                <div class='post-card'>
                    <strong>案 {idx}</strong><br>
                    <p style='margin: 10px 0; color: #333;'>{post}</p>
                    <small style='color: #999;'>{len(post)} 文字</small>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📤 投稿", key=f"btn_news_post_{idx}", use_container_width=True):
                        with st.spinner("投稿中..."):
                            result = post_to_x(post)
                            if result["success"]:
                                st.markdown(f"""
                                <div class='success-box'>
                                    <strong>✅ 投稿成功！</strong><br>
                                    ID: {result['tweet_id']}
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.generated_posts = None
                            else:
                                st.error(f"❌ 失敗: {result['error']}")

                with col2:
                    x_url = get_x_compose_url(post)
                    st.link_button("🖼️ 画像・予約", x_url, use_container_width=True, key=f"news_link_{idx}")
        else:
            st.info("投稿案がまだ生成されていません")

# ════════════════════════════════════════════════════════
# TAB 3: プロフィール
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ⚙️ プロフィール")

    st.markdown(f"**メールアドレス:** {st.session_state.email}")
    st.markdown(f"**ユーザーID:** {st.session_state.user_id}")
    st.markdown(f"**登録日:** {datetime.now().strftime('%Y年%m月%d日')}")

    st.markdown("---")

    st.markdown("### 💡 ヘルプ")
    with st.expander("使い方"):
        st.markdown("""
        **TAB 1: 短文投稿**
        - あなたの主張を入力
        - AI が 3 パターンの投稿案を生成
        - 気に入った案をワンクリックで X へ投稿

        **TAB 2: ニュース投稿**
        - ニュースソース（産経新聞、Axios、Fox News）を選択
        - 記事を選んで、あなたの意見を入力
        - AI が意見 + 記事をもとに 3 パターン生成

        **TAB 3: プロフィール**
        - アカウント情報の確認
        """)

    with st.expander("よくある質問"):
        st.markdown("""
        **Q: 投稿は実際に X に投稿される？**
        A: はい。「📤 投稿」ボタンをクリックすると、即座に X に投稿されます.

        **Q: 何度でも生成できる？**
        A: はい。生成回数に制限はありません。何度でも投稿案を生成して利用できます.
        """)

    st.markdown("---")
    st.markdown("**v2.1** — 2026年5月1日")

# ── フッター ──────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 12px; margin-top: 30px;'>
    <p>🔐 セキュリティ: OAuth 2.0 で安全に認証 | 🚀 Powered by Gemini AI</p>
    <p>v2.0 — 2026年4月29日</p>
</div>
""", unsafe_allow_html=True)
