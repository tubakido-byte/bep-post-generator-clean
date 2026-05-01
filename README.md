# 🚀 BEP Post Generator

AI × X投稿自動化ツール - Streamlit Cloud 対応版

## 機能

- ✨ **短文投稿機能** - あなたの主張を入力 → AI が 3パターン生成 → ワンクリック投稿
- 📰 **ニュース投稿機能** - ニュース記事 + あなたの意見 → 3パターン自動生成
- 🌍 **日本語翻訳対応** - 英語ニュースを自動翻訳して投稿

## セットアップ

### 前提条件

- Python 3.9+
- Streamlit
- Gemini API キー
- X OAuth2 トークン

### ローカル実行

```bash
# 依存関係をインストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集して API キーを設定

# Streamlit で実行
streamlit run x_post_generator_v2.py
```

### Streamlit Cloud でデプロイ

1. GitHub リポジトリにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
3. 「New app」 → このリポジトリを選択
4. Settings → Secrets で環境変数を設定

```
GEMINI_API_KEY = your_api_key
X_OAUTH2_ACCESS_TOKEN = your_token
```

## 環境変数

```
GEMINI_API_KEY          # Google Gemini API キー
X_OAUTH2_ACCESS_TOKEN   # X OAuth2 トークン
```

## ニュースソース

- 産経新聞（日本語 RSS）
- Axios（英語 → 自動翻訳）
- Fox News（英語 → 自動翻訳）

## 使用方法

### 短文投稿

1. 「あなたの主張」を入力
2. 「3パターン生成」をクリック
3. 気に入った案を選択
4. 「X に投稿」をクリック

### ニュース投稿

1. 「ニュースソース」から記事を選択
2. 「あなたの意見」を入力
3. 「3パターン生成」をクリック
4. 「X に投稿」をクリック

## トラブルシューティング

### API キーエラー

```
❌ API キーが設定されていません
```

→ Streamlit Cloud の Secrets で環境変数を設定してください

### ニュースフィード取得失敗

→ RSS フィードが利用不可の場合、別のソースが自動的に使用されます

## 開発

```bash
# ローカルテスト
streamlit run x_post_generator_v2.py

# 依存関係の更新
pip freeze > requirements.txt
```

## ライセンス

GPL2

## サポート

X: @Insjapan119

---

**BEP Post Generator - 毎日の X 投稿を AI が自動生成**
