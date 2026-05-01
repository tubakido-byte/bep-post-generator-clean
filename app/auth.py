import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
from app.db import db


def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """パスワードを検証"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def register_user(email: str, password: str) -> Tuple[bool, str]:
    """新規ユーザーを登録"""
    if not email or not password:
        return False, "メールアドレスとパスワードを入力してください"

    if len(password) < 8:
        return False, "パスワードは8文字以上である必要があります"

    # 既存ユーザーを確認
    existing = db.fetch_one("SELECT user_id FROM users WHERE email = ?", (email,))
    if existing:
        return False, "このメールアドレスは既に登録されています"

    # パスワードをハッシュ化
    password_hash = hash_password(password)

    # ユーザーを登録
    success = db.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash)
    )

    if success:
        return True, "ユーザー登録が完了しました"
    else:
        return False, "ユーザー登録に失敗しました"


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """ユーザーをログイン"""
    if not email or not password:
        return False, "メールアドレスとパスワードを入力してください", None

    # ユーザーを取得
    user = db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user:
        return False, "メールアドレスまたはパスワードが間違っています", None

    # パスワードを検証
    if not verify_password(password, user['password_hash']):
        return False, "メールアドレスまたはパスワードが間違っています", None

    # ロック状態を確認
    if user['is_locked']:
        return False, f"アカウントがロックされています: {user['locked_reason']}", None

    # セッションとトークンを作成
    session_id = secrets.token_urlsafe(32)
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()

    db.execute(
        "INSERT INTO user_sessions (session_id, user_id, token, expires_at) VALUES (?, ?, ?, ?)",
        (session_id, user['user_id'], token, expires_at)
    )

    # last_login を更新
    db.execute(
        "UPDATE users SET last_login = ? WHERE user_id = ?",
        (datetime.now().isoformat(), user['user_id'])
    )

    return True, "ログインしました", {
        "user_id": user['user_id'],
        "email": user['email'],
        "token": token,
        "session_id": session_id
    }


def verify_token(token: str) -> Optional[int]:
    """トークンを検証して user_id を返す"""
    session = db.fetch_one(
        "SELECT * FROM user_sessions WHERE token = ? AND expires_at > ?",
        (token, datetime.now().isoformat())
    )

    if session:
        return session['user_id']
    return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """ユーザーを ID で取得"""
    return db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))


def get_user_by_email(email: str) -> Optional[Dict]:
    """ユーザーをメールアドレスで取得"""
    return db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))


def logout_user(session_id: str) -> bool:
    """ユーザーをログアウト"""
    return db.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
