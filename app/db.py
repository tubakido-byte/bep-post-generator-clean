import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """SQLite データベース操作の抽象化層"""

    def __init__(self, db_path: str = "bep_data/users.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """テーブルを作成"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # users テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                subscription_plan VARCHAR(50) DEFAULT 'inactive',
                is_locked BOOLEAN DEFAULT 0,
                locked_reason VARCHAR(255)
            )
        """)

        # user_sessions テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id VARCHAR(128) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token VARCHAR(255) UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # payment_records テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_records (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                amount INTEGER DEFAULT 3000,
                status VARCHAR(50) DEFAULT 'pending',
                valid_until DATE,
                payment_method VARCHAR(50) DEFAULT 'paypay',
                paypay_transaction_id VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                confirmed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def execute(self, sql: str, params: tuple = ()) -> bool:
        """SQL を実行（INSERT/UPDATE/DELETE）"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        """1行を取得"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict]:
        """全行を取得"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []

    def close(self):
        """接続を閉じる"""
        pass


# グローバルインスタンス
db = DatabaseManager()
