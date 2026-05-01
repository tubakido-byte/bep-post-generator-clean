# BEP Post Generator - 決済自動化プラグイン インストールガイド

## 📋 前提条件

- WordPress 5.0 以上
- WP Simple Pay プラグイン（有効化済み）
- PHP 7.4 以上

---

## 🔧 インストール手順

### ステップ1：プラグインをアップロード

**方法A：FTP（推奨）**
```
1. FTP クライアントで以下にアクセス：
   wp-content/plugins/

2. 新しいフォルダを作成：
   bep-webhook-plugin

3. bep-webhook-plugin.php をアップロード
```

**方法B：WordPress 管理画面**
```
1. 管理画面 → プラグイン → 新規追加
2. 「プラグインのアップロード」をクリック
3. bep-webhook-plugin.php を選択 → アップロード
```

### ステップ2：プラグインを有効化

```
1. WordPress 管理画面 → プラグイン
2. 「BEP Post Generator - Webhook & Dashboard」を検索
3. 「有効化」をクリック
```

### ステップ3：WP Simple Pay の Webhook を設定

**WP Simple Pay Dashboard で以下を設定：**

```
設定 → Webhooks → 新規追加

• イベントタイプ：payment_intent.succeeded
• エンドポイント URL：
  https://www.ins-japan.com/wp-admin/admin-ajax.php?action=bep_simpay_webhook
• ステータス：有効化
• 保存
```

### ステップ4：会員ページを作成（またはページを編集）

```
1. WordPress 管理画面 → ページ → 新規追加
   （または既存の会員ページを編集）

2. タイトル：「ダッシュボード」または「会員ページ」

3. 本文に以下を追加：
   [membership_dashboard]

4. 公開
```

**ページ URL の例：**
```
https://www.ins-japan.com/members-site/dashboard/
```

---

## ✅ インストール確認

管理画面に以下の通知が表示されていることを確認：

```
✅ BEP Post Generator プラグイン が有効化されました。
Webhook エンドポイント: https://www.ins-japan.com/wp-admin/admin-ajax.php?action=bep_simpay_webhook
ダッシュボードショートコード: [membership_dashboard]
```

---

## 🧪 テスト実行

### テスト決済フロー

```
1. WP Simple Pay の テスト決済フォームにアクセス
   https://www.ins-japan.com/members-site/（支払いフォームのあるページ）

2. テストカード情報を入力：
   カード番号：4242 4242 4242 4242
   有効期限：12/25（任意の未来の月/年）
   CVC：123（任意の3桁数字）

3. メールアドレスを入力（例：test@example.com）

4. 「¥3,000で購入する」をクリック

5. 決済完了後の動作を確認：
   ✅ WordPress ユーザーが自動作成されたか
   ✅ メールが送信されたか
   ✅ 会員ページで ID/パスワードが表示されるか
```

### WordPress ユーザー確認

```
管理画面 → ユーザー

新しいユーザーが作成されていることを確認：
• ユーザー名：user_[4桁数字]
• メール：決済時に入力したメール
• ロール：購読者
```

### メール確認

```
WordPress メール送信テスト：

1. 管理画面 → ツール → サイトヘルス
2. 「メール機能」をテスト
   または
3. テストメール送信プラグインを使用
   https://wordpress.org/plugins/wp-mail-test/
```

### 会員ページの動作確認

```
1. 作成したテスト用ユーザーでログイン
   ユーザーID：user_XXXX
   パスワード：自動生成パスワード

2. 会員ページ（[membership_dashboard]）にアクセス
   表示内容を確認：
   ✅ ウェルカムメッセージ
   ✅ ツール URL
   ✅ ユーザーID
   ✅ セットアップガイド
   ✅ パスワード表示/非表示機能

3. 未ログイン時のアクセス
   ログアウト → 会員ページにアクセス
   ✅ ログインページにリダイレクト
```

---

## 📊 確認できるデータ

### ユーザーメタデータ

```
WordPress ユーザーに自動保存されるメタ：
• bep_payment_date：決済日時
• bep_plan：購入プラン（BEP Post Generator - ¥3,000/月）
• bep_payment_amount：金額（3000）
• bep_payment_id：Stripe Payment Intent ID
```

### カスタムテーブル

```
テーブル名：wp_bep_customers

カラム：
• id - 自動採番
• user_id - WordPress ユーザーID
• email - メールアドレス
• payment_intent_id - Stripe Payment Intent ID
• amount - 金額
• status - ステータス（active/inactive）
• created_at - 作成日時
```

**確認方法（phpMyAdmin）：**
```
1. phpMyAdmin にアクセス
2. データベース選択
3. wp_bep_customers テーブルを確認
4. レコードが挿入されていることを確認
```

---

## 🐛 トラブルシューティング

### Webhook が実行されていない

**原因：** WP Simple Pay の Webhook 設定が不正

**確認方法：**
```
1. WP Simple Pay → イベント / Webhook ログ を確認
2. エラーメッセージを確認
```

**解決方法：**
```
1. Webhook URL を再確認：
   https://www.ins-japan.com/wp-admin/admin-ajax.php?action=bep_simpay_webhook

2. イベントタイプが payment_intent.succeeded か確認

3. WP Simple Pay が有効化されているか確認
```

### ユーザーが作成されていない

**原因：** Plugin エラー

**確認方法：**
```
1. WordPress ログファイルを確認
   wp-content/debug.log

2. エラーメッセージを検索：
   [BEP Webhook]
```

**解決方法：**
```
1. プラグインを無効化 → 有効化
2. WordPress キャッシュをクリア
3. wp_cache_flush() を実行
```

### メールが送信されていない

**原因：** WordPress のメール設定

**確認方法：**
```
1. 管理画面 → ツール → サイトヘルス
2. 「メール機能」をテスト
```

**解決方法：**
```
1. SMTP プラグイン を導入：
   WP Mail SMTP
   https://wordpress.org/plugins/wp-mail-smtp/

2. noreply@ins-japan.com を From メールアドレスに設定

3. テスト送信
```

---

## 📝 ログ確認

プラグインがすべてのアクションを **debug.log** に記録します：

```
[BEP Webhook] ✅ ユーザー作成成功 | User ID: 123 | Email: user@example.com | Username: user_5678
[BEP Webhook] メールアドレスが見つかりません
[BEP Webhook] ユーザー既存 - user@example.com
[BEP Webhook] ユーザー作成エラー - ...
```

**ログファイル確認：**
```
wp-content/debug.log（FTP で確認）
または
管理画面 → ツール → サイトヘルス → ログ
```

---

## ✨ 全フロー確認チェックリスト

- [ ] プラグインが有効化されている
- [ ] WP Simple Pay Webhook が設定されている
- [ ] 会員ページが作成されている
- [ ] [membership_dashboard] ショートコードが貼り付けられている
- [ ] テスト決済を実行した
- [ ] WordPress ユーザーが自動作成された
- [ ] ウェルカムメールが送信された
- [ ] 会員ページでアクセス情報が表示された
- [ ] 未ログイン時はログインページにリダイレクトされた

---

## 📞 サポート

問題が発生した場合：

1. **debug.log** を確認
2. **WP Simple Pay ログ** を確認
3. **テストメール** を送信して、メール機能を確認
4. このガイドの **トラブルシューティング** を参照

---

**完了後：** 販売ページが完全に自動化されます！🎉
