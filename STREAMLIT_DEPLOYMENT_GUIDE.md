# 🚀 BEP Post Generator - Streamlit Cloud デプロイガイド

## 概要

BEP Post Generator をカップリングなしで **Streamlit Cloud に無料デプロイ** します。

**所要時間：** 5～10分  
**コスト：** 無料（Streamlit Community Cloud）

---

## 📋 ステップ 1：GitHub リポジトリ作成

### 1-1. GitHub アカウント作成（未保有の場合）
```
https://github.com → Sign Up
```

### 1-2. 新規リポジトリ作成
```
1. GitHub にログイン
2. 「+」ボタン → New repository
3. リポジトリ名：bep-post-generator
4. 説明：BEP Post Generator - X 投稿自動化ツール
5. Public にチェック
6. Create repository
```

### 1-3. ローカルファイルをアップロード

**以下のファイルを GitHub にアップロード：**

```
bep-post-generator/
├── x_post_generator_v2.py       ← メインファイル
├── requirements.txt             ← 依存関係
├── .streamlit/
│   └── config.toml             ← Streamlit 設定
├── .env.example                ← 環境変数テンプレート
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── payment.py
│   ├── license_manager.py
│   └── db.py
└── README.md
```

**アップロード方法（最も簡単）：**

```bash
# ターミナルで実行（Git インストール必須）

cd C:\Users\htate\pr_meeting

# Git リポジトリ初期化
git init

# GitHub リモートを設定（YOUR_USERNAME と YOUR_REPO に置き換え）
git remote add origin https://github.com/YOUR_USERNAME/bep-post-generator.git

# ブランチをメインに変更
git branch -M main

# すべてのファイルをステージング
git add .

# コミット
git commit -m "Initial commit: BEP Post Generator"

# GitHub に push
git push -u origin main
```

---

## 🔑 ステップ 2：環境変数設定

### 2-1. .env ファイル作成（ローカル用）

**`C:\Users\htate\pr_meeting\.env` を作成：**

```
GEMINI_API_KEY=AIzaSyA4QYvNmc66oO3Iq42xaNvTt7Vq_tEV4PE
X_OAUTH2_ACCESS_TOKEN=cUk2QWVjSlk3YXdNMUwwZjNUSTZBN3djcGtHWWM5eUtERGd3dl9TNXU1Vmt4OjE3Nzc0Njk4MjI0MjU6MToxOmF0OjE
```

**⚠️ GitHub にはアップロード厳禁！**

### 2-2. .env.example を GitHub にアップロード

**`C:\Users\htate\pr_meeting\.env.example` を作成：**

```
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# X OAuth2 Access Token
X_OAUTH2_ACCESS_TOKEN=your_x_oauth2_token_here
```

これを GitHub にアップロード（`.env` は `.gitignore` に追加してアップロード厳禁）。

---

## 🌐 ステップ 3：Streamlit Cloud デプロイ

### 3-1. Streamlit アカウント作成

```
https://streamlit.io/cloud
→ GitHub でサインアップ
```

### 3-2. アプリをデプロイ

```
Streamlit Cloud ダッシュボード
→ 「New app」をクリック
→ Repository：bep-post-generator を選択
→ Branch：main
→ Main file path：x_post_generator_v2.py
→ Deploy をクリック
```

### 3-3. 環境変数設定

デプロイ後、Streamlit Cloud で環境変数を設定：

```
Streamlit Cloud アプリ設定
→ Settings
→ Secrets
→ 以下を入力：

GEMINI_API_KEY = AIzaSyA4QYvNmc66oO3Iq42xaNvTt7Vq_tEV4PE
X_OAUTH2_ACCESS_TOKEN = cUk2QWVjSlk3YXdNMUwwZjNUSTZBN3djcGtHWWM5eUtERGd3dl9TNXU1Vmt4OjE3Nzc0Njk4MjI0MjU6MToxOmF0OjE

→ Save
```

---

## ✅ ステップ 4：デプロイ確認

### 4-1. アプリ URL を確認

```
Streamlit Cloud ダッシュボード
→ アプリをクリック
→ URL を確認：

https://[username]-bep-post-generator.streamlit.app/
```

### 4-2. アプリにアクセス

```
URL にアクセス：
https://[username]-bep-post-generator.streamlit.app/
```

**表示内容を確認：**
- ✅ アプリが起動している
- ✅ X 投稿フォームが表示されている
- ✅ エラーメッセージがない（または、API キー設定のメッセージのみ）

---

## 📝 ステップ 5：会員ページに URL を設定

デプロイが完了したら、会員ページのダッシュボードにこの URL を設定します。

**会員ページダッシュボード（`membership-dashboard.php` または `bep-webhook-plugin.php`）内の以下を置き換え：**

```php
// 現在：
<a href="https://www.ins-japan.com/members-site/" target="_blank">
    https://www.ins-japan.com/members-site/
</a>

// 変更後：
<a href="https://[username]-bep-post-generator.streamlit.app/" target="_blank">
    https://[username]-bep-post-generator.streamlit.app/
</a>
```

---

## 🔄 デプロイ後の更新

ローカルで変更を加えた場合：

```bash
cd C:\Users\htate\pr_meeting

# 変更をコミット
git add .
git commit -m "Update: [変更内容]"

# GitHub に push
git push

# Streamlit Cloud が自動的に再デプロイ（1～2分で反映）
```

---

## 🐛 トラブルシューティング

### デプロイに失敗する場合

**確認項目：**
```
1. GitHub リポジトリが Public か確認
2. requirements.txt が正しいか確認
3. x_post_generator_v2.py がメインファイルか確認
4. 環境変数（Secrets）が設定されているか確認
```

### アプリが起動しない場合

```
1. Streamlit Cloud のログを確認
2. requirements.txt の パッケージ版を確認
3. Python 3.9+ が必要（Streamlit の要件）
```

### API エラーが出る場合

```
1. 環境変数（Secrets）が正しく設定されているか確認
2. Gemini API キーが有効か確認
3. X OAuth2 トークンが有効か確認
```

---

## 📌 重要なポイント

```
✅ .env ファイルは GitHub にアップロート厳禁
✅ .env.example は GitHub にアップロード（テンプレート用）
✅ 環境変数は Streamlit Cloud の Secrets で設定
✅ 自動デプロイ：GitHub に push → Streamlit 自動更新
✅ URL：https://[username]-bep-post-generator.streamlit.app/
```

---

## 🎯 最終確認チェックリスト

```
[ ] GitHub アカウント作成
[ ] リポジトリ作成（bep-post-generator）
[ ] ローカルファイルをアップロード（git push）
[ ] Streamlit アカウント作成
[ ] Streamlit Cloud でアプリ作成
[ ] 環境変数を Secrets で設定
[ ] アプリ URL で起動確認
[ ] 会員ページダッシュボードに URL を設定
```

---

## 📞 サポート

デプロイがうまくいかない場合：

- Streamlit ドキュメント：https://docs.streamlit.io/
- GitHub ドキュメント：https://docs.github.com/
- サポート：X DM @Insjapan119

---

**デプロイ完了後、ツール URL を会員ページに設定すれば、完全な自動化システムが完成します！** 🎉
