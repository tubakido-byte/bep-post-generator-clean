# BEP Post Generator - テストチェックリスト

## 🎯 完全なテストフロー

---

## 📋 Phase 1：環境確認

### ✅ 前提条件チェック
```
□ WordPress 5.0 以上がインストールされている
□ WP Simple Pay プラグイン が有効化されている
□ PHP 7.4 以上
□ データベース接続 OK
□ メール機能が有効（SMTP または WordPress メール）
```

### ✅ プラグインインストール確認
```
□ bep-webhook-plugin.php が wp-content/plugins/ に配置されている
□ プラグイン一覧に「BEP Post Generator - Webhook & Dashboard」が表示されている
□ プラグインが「有効」になっている
□ 管理画面に成功通知が表示されている
```

---

## 📋 Phase 2：設定確認

### ✅ WP Simple Pay Webhook 設定
```
□ WP Simple Pay → 設定 → Webhook を開く
□ 「新規追加」をクリック
□ 以下を入力：
  • イベントタイプ：payment_intent.succeeded
  • エンドポイント：https://www.ins-japan.com/wp-admin/admin-ajax.php?action=bep_simpay_webhook
  • ステータス：有効化
□ 「保存」をクリック
□ Webhook が一覧に表示される
```

### ✅ 会員ページ設定
```
□ WordPress 管理画面 → ページ → 新規追加
□ タイトル：「ダッシュボード」など
□ 本文に以下を追加：
  [membership_dashboard]
□ 「公開」をクリック
□ ページ URL を確認：
  https://www.ins-japan.com/members-site/dashboard/
□ 未ログイン時にアクセス → ログインページにリダイレクトされることを確認
```

---

## 📋 Phase 3：テスト決済実行

### ✅ テスト決済フロー
```
1. 販売ページ（支払いフォーム）にアクセス：
   https://www.ins-japan.com/members-site/

2. 以下を入力：
   • メールアドレス：test-user-001@example.com（テスト用）
   • その他の必要項目

3. テストカード情報を入力：
   • カード番号：4242 4242 4242 4242
   • 有効期限：12/25（任意の未来の月/年）
   • CVC：123
   • 名前：Test User

4. 「¥3,000で購入する」をクリック
   □ フォームが送信される
   □ 「決済成功」メッセージが表示される（または成功ページにリダイレクト）
```

---

## 📋 Phase 4：自動処理確認

### ✅ WordPress ユーザー作成確認
```
□ 管理画面 → ユーザー
□ 新しいユーザーが作成されているか確認：
  • ユーザー名：user_XXXX（4桁数字）
  • メール：test-user-001@example.com
  • ロール：購読者
  • ステータス：確認

□ ユーザーを編集して、メタデータを確認：
  「ユーザー情報」セクション下部に：
  • bep_payment_date：現在の日時
  • bep_plan：BEP Post Generator - ¥3,000/月
  • bep_payment_amount：3000
  • bep_payment_id：pi_で始まる ID
```

### ✅ ウェルカムメール確認
```
□ test-user-001@example.com にメールが届いているか確認

メール内容：
□ 件名：「🎉 BEP Post Generator へようこそ！」
□ 本文に以下が含まれている：
  • ツール URL：https://www.ins-japan.com/members-site/
  • ユーザーID：user_XXXX
  • パスワード：（ランダム20文字）
  • セットアップ手順
  • サポート情報（@Insjapan119）

□ HTML 形式で表示されている（整形されている）
□ リンクが正しく機能している
```

### ✅ ログ確認
```
□ wp-content/debug.log を確認（FTP または管理画面）
□ 以下のログが記録されているか確認：
  [BEP Webhook] ✅ ユーザー作成成功 | User ID: [ID] | Email: test-user-001@example.com | Username: user_XXXX

□ エラーログがない（[BEP Webhook] Error... がない）
```

### ✅ カスタムテーブル確認
```
□ phpMyAdmin またはデータベースクライアントで確認
□ テーブル：wp_bep_customers
□ レコードが挿入されている：
  • user_id：作成されたユーザー ID
  • email：test-user-001@example.com
  • payment_intent_id：Stripe の ID
  • amount：3000
  • status：active
  • created_at：現在の日時
```

---

## 📋 Phase 5：会員ページ動作確認

### ✅ 認証済みユーザーでアクセス

```
1. test-user-001@example.com でログイン：
   • ユーザー名：user_XXXX
   • パスワード：ウェルカムメールに記載されているもの

2. 会員ページにアクセス：
   https://www.ins-japan.com/members-site/dashboard/

3. ダッシュボードが表示される：
   □ ウェルカムメッセージが表示されている
     「🎉 ようこそ、[user_nicename]さん」
   
   □ アクセス情報セクション：
     • ツール URL：https://www.ins-japan.com/members-site/
     • ユーザーID：user_XXXX
     • パスワード：••••••••（マスク状態）
     • 「表示」ボタンがある
   
   □ ユーザー情報が表示されている：
     • メールアドレス：test-user-001@example.com
     • プラン：月額 ¥3,000
     • 登録日：[日付]
   
   □ セットアップガイドが表示されている
   □ サポート情報（X: @Insjapan119）が表示されている
```

### ✅ パスワード表示/非表示機能

```
□ 「表示」ボタンをクリック
  • パスワードフィールドがテキストに変わる
  • 実際のパスワードが表示される
  • ボタンが「非表示」に変わる

□ 「非表示」ボタンをクリック
  • パスワードが再度マスクされる（••••••••）
  • ボタンが「表示」に戻る
```

### ✅ 未ログイン時のアクセス確認

```
□ ログアウト
□ 会員ページにアクセス：
  https://www.ins-japan.com/members-site/dashboard/

□ 以下のいずれかが発生する：
  • ログインページにリダイレクト
  • 「ログインが必要です」メッセージ表示
  • ダッシュボードが表示されない
```

---

## 📋 Phase 6：複数ユーザーテスト

### ✅ 2番目のテスト決済

```
1. 異なるメールアドレスで決済：
   test-user-002@example.com

2. 同じ手順で決済を完了

3. 確認項目：
   □ 新しいユーザーが作成される（user_YYYY）
   □ メールが送信される
   □ 2番目のユーザーでログイン可能
   □ ダッシュボードが正しく表示される
```

### ✅ 同じメールアドレスで再決済

```
1. 同じメール（test-user-001@example.com）で決済を試みる

2. 確認項目：
   □ ユーザーが重複作成されない（既存ユーザーを検知）
   □ ログに「ユーザー既存」メッセージが記録される
   □ エラーが発生しない
```

---

## 📋 Phase 7：エッジケーステスト

### ✅ 無効なメールアドレス

```
□ メールアドレスなし（空白）での決済
  → ユーザー作成されない、エラーログ記録

□ 不正なメール形式
  → メール送信失敗、エラーログ記録
```

### ✅ ネットワークエラー

```
□ Webhook リクエスト時のタイムアウト
  → エラーハンドリング（HTTP 500）

□ メール送信失敗
  → ユーザーは作成されるが、メール送信なし（ログ記録）
```

---

## 📋 Summary Checklist

```
【Phase 1 - 環境確認】
□ WordPress OK
□ WP Simple Pay OK
□ PHP バージョン OK
□ プラグイン有効化 OK

【Phase 2 - 設定確認】
□ Webhook 設定 OK
□ 会員ページ作成 OK
□ [membership_dashboard] 貼り付け OK

【Phase 3 - テスト決済】
□ 決済フロー OK
□ メール入力 OK
□ テストカード OK
□ 決済成功 OK

【Phase 4 - 自動処理】
□ ユーザー作成 OK
□ メール送信 OK
□ ログ記録 OK
□ DB 保存 OK

【Phase 5 - 会員ページ】
□ ダッシュボード表示 OK
□ アクセス情報 OK
□ パスワード表示/非表示 OK
□ ログイン確認 OK

【Phase 6 - 複数ユーザー】
□ 2番目のユーザー OK
□ 重複メール確認 OK

【Phase 7 - エッジケース】
□ エラーハンドリング OK
□ ログ記録 OK
```

---

## ✨ 完了条件

すべてのチェックボックスが ✅ になったら、システムは本番環境に対応可能です！

---

**テスト実施日：** ___________  
**実施者：** ___________  
**結果：** ✅ PASS / ❌ FAIL

---

エラーが発生した場合は、以下を確認：
1. debug.log を確認
2. このガイドの「トラブルシューティング」セクションを参照
3. サポート（X: @Insjapan119）に連絡
