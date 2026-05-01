#!/bin/bash

echo "🚀 BEP Post Generator - 完全自動デプロイスクリプト開始"
echo "=================================================="

# GitHub ユーザー情報
GITHUB_EMAIL="tubakido@gmail.com"
REPO_NAME="bep-post-generator"
GITHUB_REMOTE="https://github.com/tubakido/${REPO_NAME}.git"

# ローカルディレクトリ
PROJECT_DIR="C:\Users\htate\pr_meeting"

echo "📋 ステップ 1: GitHub リポジトリ初期化"
cd "$PROJECT_DIR"

# .git が存在する場合は削除
if [ -d ".git" ]; then
    echo "既存の git リポジトリを初期化..."
    rm -rf .git
fi

# Git 初期化
git init
git config user.email "$GITHUB_EMAIL"
git config user.name "BEP Post Generator"

echo "✅ Git 初期化完了"

echo ""
echo "📋 ステップ 2: .gitignore 作成"

cat > .gitignore << 'GITIGNORE'
# 環境変数（セキュリティ）
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# ログ
*.log
debug.log

# キャッシュ
.cache/
*.cache

# その他
.streamlit/secrets.toml
dist/
build/
*.egg-info/
GITIGNORE

echo "✅ .gitignore 作成完了"

echo ""
echo "📋 ステップ 3: ファイルをステージング"
git add .

echo "✅ ステージング完了"

echo ""
echo "📋 ステップ 4: 初期コミット"
git commit -m "Initial commit: BEP Post Generator - Streamlit Cloud Ready"

echo "✅ コミット完了"

echo ""
echo "📋 ステップ 5: リモートブランチ設定"
git branch -M main
git remote add origin "$GITHUB_REMOTE"

echo "✅ リモート設定完了"

echo ""
echo "📋 ステップ 6: GitHub に push（認証が必要な場合はプロンプトに従ってください）"
git push -u origin main

echo ""
echo "✅ デプロイ完了！"
echo ""
echo "次のステップ："
echo "1. https://streamlit.io/cloud にアクセス"
echo "2. GitHub でサインアップ（上記アカウント tubakido@gmail.com を使用）"
echo "3. 「New app」をクリック"
echo "4. Repository: tubakido/bep-post-generator"
echo "5. Main file path: x_post_generator_v2.py"
echo "6. Deploy をクリック"
echo ""
echo "デプロイ後、Streamlit Cloud の Settings → Secrets に以下を追加："
echo "GEMINI_API_KEY = AIzaSyA4QYvNmc66oO3Iq42xaNvTt7Vq_tEV4PE"
echo "X_OAUTH2_ACCESS_TOKEN = cUk2QWVjSlk3YXdNMUwwZjNUSTZBN3djcGtHWWM5eUtERGd3dl9TNXU1Vmt4OjE3Nzc0Njk4MjI0MjU6MToxOmF0OjE"
echo ""
echo "=================================================="
echo "🎉 完全自動デプロイ準備完了"
