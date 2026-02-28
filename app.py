"""
パパになるための禁煙 - ホーム（ダッシュボード）画面
"""
from datetime import date

import plotly.graph_objects as go
import streamlit as st

from utils.supabase_client import (
    get_user_settings,
    get_today_fertility_log,
    achieve_milestone,
    get_achieved_milestones,
    get_partner_share_by_code,
    add_partner_message,
    get_partner_messages,
)
from utils.calculations import (
    get_smoke_free_days,
    get_saved_money,
    get_cigarettes_not_smoked,
    format_money,
    format_days_hours,
    get_daily_savings_data,
)
from utils.milestones import (
    get_achieved_milestones as calc_achieved_milestones,
    get_next_milestone,
)
from utils.discord_notifier import (
    is_discord_configured,
    send_milestone_notification,
    send_daily_reminder,
)

# ─── ページ設定 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="パパになるための禁煙",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="auto",
)

# ─── PWAメタタグ（iOSホーム画面追加対応）────────────────────────────────────
st.markdown("""
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="パパ禁煙">
<meta name="theme-color" content="#FF69B4">
""", unsafe_allow_html=True)

# ─── パートナービュー分岐 ─────────────────────────────────────────────────────
share_code = st.query_params.get("share")

if share_code:
    # パートナー閲覧ビュー
    share = get_partner_share_by_code(share_code)
    if not share:
        st.error("❌ 共有コードが無効または共有が停止されています。")
        st.stop()

    settings = get_user_settings()
    if not settings:
        st.warning("まだ設定が完了していません。")
        st.stop()

    quit_date = date.fromisoformat(settings["quit_date"])
    cigarettes_per_day = settings["cigarettes_per_day"]
    price_per_pack = settings["price_per_pack"]
    cigarettes_per_pack = settings.get("cigarettes_per_pack", 20)

    smoke_free_days = get_smoke_free_days(quit_date)
    saved_money = get_saved_money(quit_date, cigarettes_per_day, price_per_pack, cigarettes_per_pack)
    cigarettes_not_smoked = get_cigarettes_not_smoked(quit_date, cigarettes_per_day)

    st.title("👶 パパになるための禁煙")
    st.caption("パートナーの禁煙進捗を応援しよう！")

    st.markdown("---")
    st.subheader("⏱️ 禁煙継続中")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("禁煙期間", format_days_hours(quit_date))
    with col2:
        st.metric("赤ちゃん貯金", format_money(saved_money))
    with col3:
        st.metric("吸わなかった本数", f"{cigarettes_not_smoked:,} 本")

    # マイルストーン
    st.markdown("---")
    st.subheader("🏆 達成マイルストーン")
    achieved_locally = calc_achieved_milestones(smoke_free_days)
    if achieved_locally:
        for m in reversed(achieved_locally[-5:]):
            st.write(f"{m.emoji} **{m.title}** — {m.description}")
    else:
        st.info("まだマイルストーンは達成されていません。一緒に応援しよう！")

    next_ms = get_next_milestone(smoke_free_days)
    if next_ms:
        remaining = next_ms.days - smoke_free_days
        st.info(f"{next_ms.emoji} **次の目標：{next_ms.title}** — あと {remaining}日！")

    # 本日の妊活チェック状況
    st.markdown("---")
    st.subheader("📋 本日の妊活チェック状況")
    today_log = get_today_fertility_log()
    if today_log:
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("亜鉛", "✅" if today_log.get("zinc") else "⬜")
        with col_b:
            st.metric("葉酸", "✅" if today_log.get("folate") else "⬜")
        with col_c:
            st.metric("運動", "✅" if today_log.get("exercise") else "⬜")
        with col_d:
            sleep = today_log.get("sleep_hours")
            st.metric("睡眠", f"{sleep}h" if sleep else "未記録")
    else:
        st.warning("今日の妊活チェックはまだ未入力です。")

    # パートナーからの応援メッセージ送信
    st.markdown("---")
    st.subheader("💌 応援メッセージを送る")

    with st.form("partner_message_form", clear_on_submit=True):
        partner_message = st.text_area(
            "応援メッセージ",
            placeholder="一緒に頑張ろう！応援しているよ！",
            max_chars=500,
        )
        send_btn = st.form_submit_button("応援メッセージを送る 💪", use_container_width=True, type="primary")

    if send_btn and partner_message.strip():
        add_partner_message(share_code, "partner", partner_message.strip())
        st.success("✅ 応援メッセージを送りました！")
        st.rerun()
    elif send_btn:
        st.warning("メッセージを入力してください。")

    # メッセージ履歴（パートナービューでも確認可能）
    messages = get_partner_messages(share_code)
    if messages:
        st.markdown("---")
        st.subheader("📩 メッセージ履歴")
        for msg in messages:
            sent_at = msg["sent_at"][:16].replace("T", " ")
            if msg["sender"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["message"])
                    st.caption(f"本人 · {sent_at}")
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg["message"])
                    st.caption(f"パートナー · {sent_at}")

    st.stop()  # パートナービュー表示後は通常画面をスキップ

# ─── 通常ビュー（本人） ──────────────────────────────────────────────────────
st.title("👶 パパになるための禁煙")
st.caption("男性妊活 × 禁煙サポート")

# ─── 設定チェック ────────────────────────────────────────────────────────────
settings = get_user_settings()

if not settings:
    st.warning("まず **設定** 画面から禁煙開始日・タバコ情報を入力してください。")
    st.page_link("pages/4_設定.py", label="設定画面へ →", icon="⚙️")
    st.stop()

quit_date = date.fromisoformat(settings["quit_date"])
cigarettes_per_day = settings["cigarettes_per_day"]
price_per_pack = settings["price_per_pack"]
cigarettes_per_pack = settings.get("cigarettes_per_pack", 20)

# ─── 禁煙カウンター ───────────────────────────────────────────────────────────
smoke_free_days = get_smoke_free_days(quit_date)
saved_money = get_saved_money(quit_date, cigarettes_per_day, price_per_pack, cigarettes_per_pack)
cigarettes_not_smoked = get_cigarettes_not_smoked(quit_date, cigarettes_per_day)

st.markdown("---")
st.subheader("⏱️ 禁煙継続中")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="禁煙期間",
        value=format_days_hours(quit_date),
    )
with col2:
    st.metric(
        label="節約金額（赤ちゃん貯金）",
        value=format_money(saved_money),
    )
with col3:
    st.metric(
        label="吸わなかった本数",
        value=f"{cigarettes_not_smoked:,} 本",
    )

# ─── 節約金額累積グラフ ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💰 赤ちゃん貯金の推移")

savings_data = get_daily_savings_data(
    quit_date, cigarettes_per_day, price_per_pack, cigarettes_per_pack
)

if len(savings_data) >= 2:
    dates = [row["date"] for row in savings_data]
    cumulative = [row["cumulative"] for row in savings_data]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=cumulative,
            mode="lines",
            fill="tozeroy",
            line=dict(color="#FF69B4", width=2),
            fillcolor="rgba(255, 105, 180, 0.15)",
            name="累積節約金額",
            hovertemplate="%{x}<br>¥%{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="日付",
        yaxis_title="節約金額（円）",
        yaxis_tickformat=",",
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("2日以上経過するとグラフが表示されます。")

# ─── マイルストーン ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 マイルストーン")

# 達成チェック＆DB保存・Discord通知
achieved_locally = calc_achieved_milestones(smoke_free_days)
achieved_in_db = get_achieved_milestones()
notify_enabled = st.session_state.get("discord_notify_enabled", True)

for m in achieved_locally:
    if m.key not in achieved_in_db:
        achieve_milestone(m.key)
        st.balloons()
        st.success(f"🎉 **{m.title}** を達成しました！")
        # Discord通知（有効かつ設定済みの場合のみ）
        if notify_enabled and is_discord_configured():
            send_milestone_notification(m.title, m.description)

# 次のマイルストーン表示
next_ms = get_next_milestone(smoke_free_days)
if next_ms:
    remaining = next_ms.days - smoke_free_days
    st.info(
        f"{next_ms.emoji} **次のマイルストーン：{next_ms.title}**\n\n"
        f"あと **{remaining}日** で達成！\n\n"
        f"{next_ms.description}"
    )
else:
    st.success("🥇 全マイルストーンを達成しました！おめでとうございます！")

# 最近の達成マイルストーン表示（最大3件）
if achieved_locally:
    with st.expander("達成済みマイルストーンを見る"):
        for m in reversed(achieved_locally[-3:]):
            st.write(f"{m.emoji} **{m.title}** — {m.description}")

# ─── 本日のチェック状況 ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 本日のチェック状況")

today_log = get_today_fertility_log()
if today_log:
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        icon = "✅" if today_log.get("zinc") else "⬜"
        st.metric("亜鉛", icon)
    with col_b:
        icon = "✅" if today_log.get("folate") else "⬜"
        st.metric("葉酸", icon)
    with col_c:
        icon = "✅" if today_log.get("exercise") else "⬜"
        st.metric("運動", icon)
    with col_d:
        sleep = today_log.get("sleep_hours")
        st.metric("睡眠", f"{sleep}h" if sleep else "未記録")
else:
    st.warning("本日の妊活チェックをまだ入力していません。")
    st.page_link("pages/2_妊活チェック.py", label="妊活チェックへ →", icon="🌿")

    # 妊活チェック未入力リマインダー（1セッション1回のみ）
    if (
        not st.session_state.get("reminder_sent")
        and notify_enabled
        and is_discord_configured()
    ):
        send_daily_reminder(smoke_free_days, saved_money)
        st.session_state["reminder_sent"] = True

# ─── フッター ────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"禁煙開始日：{quit_date.strftime('%Y年%m月%d日')}")
