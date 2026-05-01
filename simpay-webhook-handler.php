<?php
/**
 * WP Simple Pay Webhook ハンドラー
 * 決済完了時に WordPress ユーザーを自動作成し、ID/パスワードをメール送信
 */

// AJAX エンドポイント（認証なしで実行）
add_action('wp_ajax_nopriv_simpay_webhook', 'simpay_webhook_handler');
add_action('wp_ajax_simpay_webhook', 'simpay_webhook_handler');

function simpay_webhook_handler() {
    // Webhook リクエストボディを取得
    $input = file_get_contents('php://input');
    $event = json_decode($input);

    // イベントタイプをチェック
    if (!isset($event->type) || $event->type !== 'payment_intent.succeeded') {
        http_response_code(200);
        exit;
    }

    $payment_intent = $event->data->object;

    try {
        // 顧客メールアドレスを取得
        $customer_email = $payment_intent->receipt_email ?? null;
        $amount = ($payment_intent->amount / 100); // セント → 円に変換

        if (empty($customer_email)) {
            error_log('Webhook: メールアドレスが見つかりません');
            http_response_code(400);
            exit;
        }

        // WordPress ユーザーが既に存在するかチェック
        if (email_exists($customer_email)) {
            error_log("Webhook: ユーザー既存 - {$customer_email}");
            http_response_code(200);
            exit;
        }

        // ユーザー名を自動生成
        $username = generate_unique_username($customer_email);

        // パスワードを自動生成
        $password = wp_generate_password(20, true);

        // WordPress ユーザーを作成
        $user_id = wp_create_user($username, $password, $customer_email);

        if (is_wp_error($user_id)) {
            error_log('Webhook: ユーザー作成エラー - ' . $user_id->get_error_message());
            http_response_code(500);
            exit;
        }

        // ユーザーロールを「subscriber」に設定
        $user = new WP_User($user_id);
        $user->set_role('subscriber');

        // ユーザーメタデータに決済情報を保存
        update_user_meta($user_id, 'bep_payment_date', current_time('mysql'));
        update_user_meta($user_id, 'bep_plan', 'BEP Post Generator - ¥3,000/月');
        update_user_meta($user_id, 'bep_payment_amount', $amount);
        update_user_meta($user_id, 'bep_payment_id', $payment_intent->id);

        // メール送信
        send_welcome_email($customer_email, $username, $password);

        // 顧客情報をデータベースに保存
        save_customer_data($user_id, $customer_email, $payment_intent);

        // ログに記録
        error_log(sprintf(
            'Webhook: ユーザー作成成功 | User ID: %d | Email: %s | Username: %s',
            $user_id,
            $customer_email,
            $username
        ));

        http_response_code(200);

    } catch (Exception $e) {
        error_log('Webhook Error: ' . $e->getMessage());
        http_response_code(500);
    }

    exit;
}

/**
 * ユーザー名を自動生成（重複なし）
 */
function generate_unique_username($email) {
    $base_username = 'user_' . wp_rand(1000, 9999);

    if (!username_exists($base_username)) {
        return $base_username;
    }

    // 重複が多い場合は、メールアドレスの前半を使用
    $email_parts = explode('@', $email);
    $username = sanitize_user($email_parts[0], true);

    if (username_exists($username)) {
        $username = $username . '_' . wp_rand(100, 999);
    }

    return $username;
}

/**
 * ウェルカムメール送信
 */
function send_welcome_email($customer_email, $username, $password) {
    $to = $customer_email;
    $subject = '🎉 BEP Post Generator へようこそ！';

    $message = '
        <h2 style="color: #333;">ご登録ありがとうございました</h2>

        <p>BEP Post Generator のご購入ありがとうございます。</p>

        <h3 style="color: #667eea;">📱 アクセス情報</h3>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
            <p><strong>ツール URL：</strong> https://www.ins-japan.com/members-site/</p>
            <p><strong>ユーザーID：</strong> ' . esc_html($username) . '</p>
            <p><strong>パスワード：</strong> ' . esc_html($password) . '</p>
        </div>

        <h3 style="color: #667eea;">⚡ セットアップ手順（5分で完了）</h3>
        <ol>
            <li>上記のツール URL にアクセス</li>
            <li>ユーザーID・パスワードでログイン</li>
            <li>X のアカウント連携（OAuth 2.0）を許可</li>
            <li>完了 → AI が投稿案を自動生成開始</li>
        </ol>

        <h3 style="color: #667eea;">💬 サポート</h3>
        <p>ご質問やトラブルは、X DM（<strong>@Insjapan119</strong>）にてサポートします。</p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

        <p>よろしくお願いいたします。</p>
        <p style="color: #999; font-size: 12px;">
            —<br/>
            🐧 ペンギンホームページ制作会社<br/>
            BEP Post Generator チーム
        </p>
    ';

    $headers = array(
        'Content-Type: text/html; charset=UTF-8',
        'From: BEP Post Generator <noreply@ins-japan.com>'
    );

    wp_mail($to, $subject, $message, $headers);
}

/**
 * 顧客情報をデータベースに保存
 */
function save_customer_data($user_id, $customer_email, $payment_intent) {
    global $wpdb;

    $table_name = $wpdb->prefix . 'bep_customers';

    // テーブルが存在しない場合は作成
    if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") != $table_name) {
        $charset_collate = $wpdb->get_charset_collate();
        $sql = "CREATE TABLE $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id mediumint(9) NOT NULL,
            email varchar(100) NOT NULL,
            payment_intent_id varchar(100) NOT NULL,
            amount decimal(10, 2) NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'active',
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY email (email),
            KEY user_id (user_id)
        ) $charset_collate;";

        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }

    // 顧客データを挿入
    $wpdb->insert(
        $table_name,
        array(
            'user_id' => $user_id,
            'email' => $customer_email,
            'payment_intent_id' => $payment_intent->id,
            'amount' => ($payment_intent->amount / 100),
            'status' => 'active'
        ),
        array('%d', '%s', '%s', '%f', '%s')
    );
}

?>
