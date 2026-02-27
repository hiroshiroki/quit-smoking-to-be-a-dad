"""
パパになるための禁煙 - ホーム（ダッシュボード）画面
"""
from datetime import date

import streamlit as st

from utils.supabase_client import get_user_settings, get_today_fertility_log, achieve_milestone, get_achieved_milestones
from utils.calculations import (
    get_smoke_free_days,
    get_saved_money,
    get_cigarettes_not_smoked,
    format_money,
    format_days_hours,
)
from utils.milestones import (
    get_achieved_milestones as calc_achieved_milestones,
    get_next_milestone,
)

# ─── ページ設定 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="パパになるための禁煙",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="auto",
)

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

# ─── マイルストーン ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 マイルストーン")

# 達成チェック＆DB保存
achieved_locally = calc_achieved_milestones(smoke_free_days)
achieved_in_db = get_achieved_milestones()
for m in achieved_locally:
    if m.key not in achieved_in_db:
        achieve_milestone(m.key)
        st.balloons()
        st.success(f"🎉 **{m.title}** を達成しました！")

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

# ─── フッター ────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"禁煙開始日：{quit_date.strftime('%Y年%m月%d日')}")
