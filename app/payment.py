import qrcode
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from io import BytesIO
from app.db import db


def generate_paypay_qr(user_id: int, amount: int = 3000) -> BytesIO:
    """
    PayPay QRコードを動的生成
    ユーザーID、金額、説明文を含める
    """
    paypay_id = os.getenv("PAYPAY_ID", "")
    if not paypay_id:
        return None

    # PayPay URL（金額・説明文を埋め込み）
    description = f"BEP Post Generator 月額料金（ユーザーID: {user_id}）"
    url = f"https://qr.paypay.ne.jp/{paypay_id}?amount={amount}&description={description}"

    # QRコード生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # BytesIO に変換して返す
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes


def get_payment_status(user_id: int) -> Dict:
    """
    ユーザーの支払い状態を確認
    """
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
            "is_active": False,
            "valid_until": None,
            "days_remaining": 0,
            "status": "unpaid",
            "payment_date": None
        }

    valid_until = datetime.fromisoformat(payment['valid_until'])
    today = datetime.now().date()

    if today > valid_until.date():
        return {
            "is_active": False,
            "valid_until": valid_until,
            "days_remaining": 0,
            "status": "expired",
            "payment_date": payment['payment_date']
        }

    days_remaining = (valid_until.date() - today).days

    return {
        "is_active": True,
        "valid_until": valid_until,
        "days_remaining": days_remaining,
        "status": "active",
        "payment_date": payment['payment_date']
    }


def record_payment(user_id: int, payment_date: str, amount: int = 3000) -> bool:
    """
    支払い記録を SQLite に追加
    """
    # payment_date の月末を計算
    payment_dt = datetime.fromisoformat(payment_date)

    # 次月の1日を取得
    if payment_dt.month == 12:
        next_month_first = payment_dt.replace(year=payment_dt.year + 1, month=1, day=1)
    else:
        next_month_first = payment_dt.replace(month=payment_dt.month + 1, day=1)

    # その前日の 23:59:59 を valid_until とする
    valid_until = (next_month_first - timedelta(seconds=1)).isoformat()

    success = db.execute(
        """
        INSERT INTO payment_records
        (user_id, payment_date, amount, status, valid_until, payment_method, confirmed_at)
        VALUES (?, ?, ?, 'confirmed', ?, 'paypay', ?)
        """,
        (user_id, payment_date, amount, valid_until, datetime.now().isoformat())
    )

    return success


def mark_payment_pending(user_id: int) -> bool:
    """
    支払い予定を記録（ステータス = pending）
    """
    success = db.execute(
        """
        INSERT INTO payment_records
        (user_id, payment_date, amount, status, payment_method)
        VALUES (?, ?, 3000, 'pending', 'paypay')
        """,
        (user_id, datetime.now().date().isoformat())
    )

    return success
