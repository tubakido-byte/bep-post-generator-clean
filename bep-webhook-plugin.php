<?php
/**
 * Plugin Name: BEP Post Generator - Webhook & Dashboard
 * Plugin URI: https://www.ins-japan.com/
 * Description: WP Simple Pay 連携で決済完了後、自動的に WordPress ユーザーを作成し、ID/パスワードをメール送信
 * Version: 1.0.0
 * Author: ペンギンホームページ制作会社
 * Author URI: https://www.ins-japan.com/
 * License: GPL2
 * Text Domain: bep-webhook
 * Domain Path: /languages
 */

// プラグイン有効化時の初期化
register_activation_hook(__FILE__, 'bep_webhook_activate');

function bep_webhook_activate() {
    // テーブル作成
    create_bep_customers_table();

    // キャッシュクリア
    wp_cache_flush();
}

// テーブル作成
function create_bep_customers_table() {
    global $wpdb;

    $table_name = $wpdb->prefix . 'bep_customers';
    $charset_collate = $wpdb->get_charset_collate();

    $sql = "CREATE TABLE IF NOT EXISTS $table_name (
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

// ========== Webhook ハンドラー ==========

add_action('wp_ajax_nopriv_bep_simpay_webhook', 'bep_simpay_webhook_handler');
add_action('wp_ajax_bep_simpay_webhook', 'bep_simpay_webhook_handler');

function bep_simpay_webhook_handler() {
    $input = file_get_contents('php://input');
    $event = json_decode($input);

    if (!isset($event->type) || $event->type !== 'payment_intent.succeeded') {
        http_response_code(200);
        exit;
    }

    $payment_intent = $event->data->object;

    try {
        $customer_email = $payment_intent->receipt_email ?? null;
        $amount = ($payment_intent->amount / 100);

        if (empty($customer_email)) {
            error_log('[BEP Webhook] メールアドレスが見つかりません');
            http_response_code(400);
            exit;
        }

        // ユーザーが既に存在するかチェック
        if (email_exists($customer_email)) {
            error_log("[BEP Webhook] ユーザー既存 - {$customer_email}");
            http_response_code(200);
            exit;
        }

        // ユーザー名を自動生成
        $username = bep_generate_unique_username($customer_email);

        // パスワードを自動生成
        $password = wp_generate_password(20, true);

        // WordPress ユーザーを作成
        $user_id = wp_create_user($username, $password, $customer_email);

        if (is_wp_error($user_id)) {
            error_log('[BEP Webhook] ユーザー作成エラー - ' . $user_id->get_error_message());
            http_response_code(500);
            exit;
        }

        // ユーザーロールを設定
        $user = new WP_User($user_id);
        $user->set_role('subscriber');

        // ユーザーメタデータに決済情報を保存
        update_user_meta($user_id, 'bep_payment_date', current_time('mysql'));
        update_user_meta($user_id, 'bep_plan', 'BEP Post Generator - ¥3,000/月');
        update_user_meta($user_id, 'bep_payment_amount', $amount);
        update_user_meta($user_id, 'bep_payment_id', $payment_intent->id);

        // ウェルカムメール送信
        bep_send_welcome_email($customer_email, $username, $password);

        // 顧客情報をDB保存
        bep_save_customer_data($user_id, $customer_email, $payment_intent);

        error_log(sprintf(
            '[BEP Webhook] ✅ ユーザー作成成功 | User ID: %d | Email: %s | Username: %s',
            $user_id,
            $customer_email,
            $username
        ));

        http_response_code(200);

    } catch (Exception $e) {
        error_log('[BEP Webhook] Error: ' . $e->getMessage());
        http_response_code(500);
    }

    exit;
}

// ========== ユーティリティ関数 ==========

function bep_generate_unique_username($email) {
    $base_username = 'user_' . wp_rand(1000, 9999);

    if (!username_exists($base_username)) {
        return $base_username;
    }

    $email_parts = explode('@', $email);
    $username = sanitize_user($email_parts[0], true);

    if (username_exists($username)) {
        $username = $username . '_' . wp_rand(100, 999);
    }

    return $username;
}

function bep_send_welcome_email($customer_email, $username, $password) {
    $to = $customer_email;
    $subject = '🎉 BEP Post Generator へようこそ！';

    $message = '
        <h2 style="color: #333;">ご登録ありがとうございました</h2>

        <p>BEP Post Generator のご購入ありがとうございます。</p>

        <h3 style="color: #667eea;">📱 アクセス情報</h3>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
            <p><strong>ツール URL：</strong> https://tubakido-byte-bep-post-generator-clean.streamlit.app/</p>
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

function bep_save_customer_data($user_id, $customer_email, $payment_intent) {
    global $wpdb;

    $table_name = $wpdb->prefix . 'bep_customers';

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

// ========== 会員ダッシュボード ショートコード ==========

add_shortcode('membership_dashboard', 'render_bep_membership_dashboard');

function render_bep_membership_dashboard() {
    if (!is_user_logged_in()) {
        return '<div style="text-align: center; padding: 40px; color: #999;">
                    <p>ログインが必要です。</p>
                    <p><a href="' . wp_login_url(get_permalink()) . '">ログインする</a></p>
                </div>';
    }

    $user = wp_get_current_user();
    $user_id = $user->ID;
    $username = $user->user_login;
    $email = $user->user_email;
    $user_nicename = $user->user_nicename;

    $payment_date = get_user_meta($user_id, 'bep_payment_date', true);
    $plan = get_user_meta($user_id, 'bep_plan', true);

    ob_start();
    ?>

    <div class="membership-dashboard" style="max-width: 800px; margin: 40px auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 40px;">
            <h2 style="margin: 0 0 10px 0; font-size: 32px;">🎉 ようこそ、<?php echo esc_html($user_nicename); ?>さん</h2>
            <p style="margin: 0; opacity: 0.9;">BEP Post Generator へのアクセスは準備完了です</p>
        </div>

        <div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px;">
            <h3 style="color: #333; font-size: 24px; margin-top: 0;">📱 BEP Post Generator アクセス情報</h3>

            <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 20px;">
                <p style="margin: 15px 0;">
                    <strong style="color: #667eea;">ツール URL：</strong><br/>
                    <a href="https://www.ins-japan.com/members-site/" target="_blank" style="color: #667eea; text-decoration: none; word-break: break-all;">
                        https://www.ins-japan.com/members-site/
                    </a>
                </p>

                <p style="margin: 15px 0;">
                    <strong style="color: #667eea;">ユーザーID：</strong><br/>
                    <code style="background: white; padding: 10px; border-radius: 5px; display: inline-block; font-family: monospace;">
                        <?php echo esc_html($username); ?>
                    </code>
                </p>

                <p style="margin: 15px 0;">
                    <strong style="color: #667eea;">パスワード：</strong><br/>
                    <div style="position: relative;">
                        <input type="password" id="password-field" value="••••••••" readonly
                               style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; width: 200px;">
                        <button id="toggle-password" onclick="togglePassword()"
                                style="padding: 8px 15px; margin-left: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            表示
                        </button>
                    </div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">
                        ※ パスワードは送信メール内でご確認ください
                    </p>
                </p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 10px 0;"><strong>登録メールアドレス：</strong> <?php echo esc_html($email); ?></p>
                <p style="margin: 10px 0;"><strong>プラン：</strong> <?php echo esc_html($plan ?: '月額 ¥3,000'); ?></p>
                <?php if (!empty($payment_date)): ?>
                    <p style="margin: 10px 0;"><strong>登録日：</strong> <?php echo esc_html(date('Y年m月d日', strtotime($payment_date))); ?></p>
                <?php endif; ?>
            </div>
        </div>

        <div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px;">
            <h3 style="color: #333; font-size: 24px; margin-top: 0;">⚡ セットアップ手順（5分で完了）</h3>
            <ol style="line-height: 2; color: #666;">
                <li>上記のツール URL にアクセス</li>
                <li>ユーザーID・パスワードでログイン</li>
                <li>X のアカウント連携（OAuth 2.0）を許可</li>
                <li>✨ 完了 → AI が投稿案を自動生成開始</li>
            </ol>
        </div>

        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; border-radius: 15px; text-align: center;">
            <h3 style="margin-top: 0; font-size: 24px;">💬 サポート</h3>
            <p style="margin: 15px 0; font-size: 16px;">ご質問やトラブルは、X DM でサポートします</p>
            <p style="margin: 15px 0;">
                <a href="https://twitter.com/Insjapan119" target="_blank"
                   style="color: white; text-decoration: none; font-weight: bold;">
                    X: @Insjapan119
                </a>
            </p>
        </div>

    </div>

    <script>
        function togglePassword() {
            const field = document.getElementById('password-field');
            const btn = document.getElementById('toggle-password');

            if (field.type === 'password') {
                field.type = 'text';
                btn.textContent = '非表示';
            } else {
                field.type = 'password';
                btn.textContent = '表示';
            }
        }
    </script>

    <style>
        .membership-dashboard { color: #333; line-height: 1.6; }
        .membership-dashboard a { color: #667eea; text-decoration: none; }
        .membership-dashboard a:hover { text-decoration: underline; }
        .membership-dashboard button:hover { opacity: 0.9; }
    </style>

    <?php
    return ob_get_clean();
}

// ========== WP Simple Pay 統合 ==========

add_filter('simpay_form_settings_fields_keys', 'bep_simpay_form_settings');

function bep_simpay_form_settings($settings) {
    // WP Simple Pay が正しく設定されていることを確認
    if (function_exists('simpay_payment_form')) {
        error_log('[BEP] WP Simple Pay 統合 OK');
    }
    return $settings;
}

// ========== 管理画面通知 ==========

add_action('admin_notices', 'bep_webhook_admin_notice');

function bep_webhook_admin_notice() {
    if (current_user_can('manage_options')) {
        ?>
        <div class="notice notice-success is-dismissible">
            <p>
                <strong>✅ BEP Post Generator プラグイン</strong> が有効化されました。<br/>
                <strong>Webhook エンドポイント:</strong> <code><?php echo admin_url('admin-ajax.php') . '?action=bep_simpay_webhook'; ?></code><br/>
                <strong>ダッシュボードショートコード:</strong> <code>[membership_dashboard]</code>
            </p>
        </div>
        <?php
    }
}

?>
