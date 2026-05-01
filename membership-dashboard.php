<?php
/**
 * 会員ダッシュボード - ショートコード実装
 * [membership_dashboard] で表示
 */

// ショートコード登録
add_shortcode('membership_dashboard', 'render_membership_dashboard');

function render_membership_dashboard() {
    // ログイン確認
    if (!is_user_logged_in()) {
        return '<div style="text-align: center; padding: 40px; color: #999;">
                    <p>ログインが必要です。</p>
                    <p><a href="' . wp_login_url(get_permalink()) . '">ログインする</a></p>
                </div>';
    }

    // 現在のユーザー情報を取得
    $user = wp_get_current_user();
    $user_id = $user->ID;
    $username = $user->user_login;
    $email = $user->user_email;
    $user_nicename = $user->user_nicename;

    // メタデータを取得
    $payment_date = get_user_meta($user_id, 'bep_payment_date', true);
    $plan = get_user_meta($user_id, 'bep_plan', true);

    // ダッシュボード HTML
    ob_start();
    ?>

    <div class="membership-dashboard" style="max-width: 800px; margin: 40px auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

        <!-- ウェルカムメッセージ -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 40px;">
            <h2 style="margin: 0 0 10px 0; font-size: 32px;">🎉 ようこそ、<?php echo esc_html($user_nicename); ?>さん</h2>
            <p style="margin: 0; opacity: 0.9;">BEP Post Generator へのアクセスは準備完了です</p>
        </div>

        <!-- アクセス情報セクション -->
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
                </div>
            </div>

            <!-- 登録情報 -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 10px 0;"><strong>登録メールアドレス：</strong> <?php echo esc_html($email); ?></p>
                <p style="margin: 10px 0;"><strong>プラン：</strong> <?php echo esc_html($plan ?: '月額 ¥3,000'); ?></p>
                <?php if (!empty($payment_date)): ?>
                    <p style="margin: 10px 0;"><strong>登録日：</strong> <?php echo esc_html(date('Y年m月d日', strtotime($payment_date))); ?></p>
                <?php endif; ?>
            </div>
        </div>

        <!-- セットアップガイド -->
        <div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px;">
            <h3 style="color: #333; font-size: 24px; margin-top: 0;">⚡ セットアップ手順（5分で完了）</h3>
            <ol style="line-height: 2; color: #666;">
                <li>上記のツール URL にアクセス</li>
                <li>ユーザーID・パスワードでログイン</li>
                <li>X のアカウント連携（OAuth 2.0）を許可</li>
                <li>✨ 完了 → AI が投稿案を自動生成開始</li>
            </ol>
        </div>

        <!-- サポート -->
        <div style="background: #f093fb; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; border-radius: 15px; text-align: center;">
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
        .membership-dashboard {
            color: #333;
            line-height: 1.6;
        }

        .membership-dashboard a {
            color: #667eea;
            text-decoration: none;
        }

        .membership-dashboard a:hover {
            text-decoration: underline;
        }

        .membership-dashboard button:hover {
            opacity: 0.9;
        }
    </style>

    <?php
    return ob_get_clean();
}

?>
