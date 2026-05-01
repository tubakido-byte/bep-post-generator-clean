from datetime import datetime
from typing import Dict, Optional
from app.db import db


def check_license_status(user_id: int) -> Dict:
    """
    ユーザーのライセンス状態を確認
    returns: {
        "status": "active" | "locked" | "unpaid",
        "can_access": bool,
        "valid_until": datetime or None,
        "days_remaining": int,
        "locked_reason": str or None
    }
    """
    # ユーザー情報を取得
    user = db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    if not user:
        return {
            "status": "error",
            "can_access": False,
            "valid_until": None,
            "days_remaining": 0,
            "locked_reason": "ユーザーが見つかりません"
        }

    # ユーザーがロックされている場合
    if user['is_locked']:
        return {
            "status": "locked",
            "can_access": False,
            "valid_until": None,
            "days_remaining": 0,
            "locked_reason": user['locked_reason'] or "管理者によりロック"
        }

    # 最新の confirmed 支払いを取得
    payment = db.fetch_one(
        """
        SELECT * FROM payment_records
        WHERE user_id = ? AND status = 'confirmed'
        ORDER BY payment_date DESC
        LIMIT 1
        """,
        (user_id,)
    )

    if not payment:
        return {
            "status": "unpaid",
            "can_access": False,
            "valid_until": None,
            "days_remaining": 0,
            "locked_reason": "支払いが確認されていません"
        }

    # 有効期限を確認
    valid_until = datetime.fromisoformat(payment['valid_until'])
    today = datetime.now().date()

    if today > valid_until.date():
        return {
            "status": "expired",
            "can_access": False,
            "valid_until": valid_until,
            "days_remaining": 0,
            "locked_reason": "サブスクリプション期限切れ"
        }

    # アクティブ
    days_remaining = (valid_until.date() - today).days

    return {
        "status": "active",
        "can_access": True,
        "valid_until": valid_until,
        "days_remaining": days_remaining,
        "locked_reason": None
    }


def lock_user(user_id: int, reason: str = "unpaid") -> bool:
    """ユーザーをロック"""
    success = db.execute(
        "UPDATE users SET is_locked = 1, locked_reason = ? WHERE user_id = ?",
        (reason, user_id)
    )
    return success


def unlock_user(user_id: int) -> bool:
    """ユーザーのロックを解除"""
    success = db.execute(
        "UPDATE users SET is_locked = 0, locked_reason = NULL WHERE user_id = ?",
        (user_id,)
    )
    return success


def auto_lock_expired_users() -> Dict:
    """
    期限切れのユーザーを自動ロック
    Cron スクリプトから毎日実行
    """
    # 有効期限切れで、かつロックされていないユーザーを取得
    expired_users = db.fetch_all(
        """
        SELECT DISTINCT u.user_id, u.email
        FROM users u
        JOIN payment_records p ON u.user_id = p.user_id
        WHERE p.status = 'confirmed'
        AND DATE(p.valid_until) < DATE('now')
        AND u.is_locked = 0
        """
    )

    locked_count = 0
    locked_user_ids = []

    for user in expired_users:
        if lock_user(user['user_id'], "expired"):
            locked_count += 1
            locked_user_ids.append(user['user_id'])

    return {
        "locked_count": locked_count,
        "locked_user_ids": locked_user_ids
    }
