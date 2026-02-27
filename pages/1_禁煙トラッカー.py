"""
禁煙トラッカー画面 - 衝動ログ入力・マイルストーン一覧
"""
from datetime import date

import streamlit as st

from utils.supabase_client import (
    get_user_settings,
    add_craving_log,
    get_craving_logs,
)
from utils.calculations import get_smoke_free_days
from utils.milestones import MILESTONES, get_achieved_milestones, get_next_milestone

st.set_page_config(page_title="禁煙トラッカー", page_icon="🚭", layout="centered")

st.title("🚭 禁煙トラッカー")

settings = get_user_settings()
if not settings:
    st.warning("設定画面から禁煙開始日を入力してください。")
    st.page_link("pages/4_設定.py", label="設定画面へ →", icon="⚙️")
    st.stop()

quit_date = date.fromisoformat(settings["quit_date"])
smoke_free_days = get_smoke_free_days(quit_date)

# ─── 衝動ログ入力フォーム ────────────────────────────────────────────────────
st.subheader("😤 「吸いたい」衝動を記録する")
st.caption("衝動を記録することで、トリガーのパターンを把握できます。")

with st.form("craving_form", clear_on_submit=True):
    intensity = st.slider(
        "衝動の強さ",
        min_value=1,
        max_value=5,
        value=3,
        help="1=軽い気持ち / 5=かなり強い衝動",
    )
    intensity_labels = {1: "😌 ちょっとだけ", 2: "😐 やや気になる", 3: "😟 かなり気になる", 4: "😣 強い衝動", 5: "😰 我慢が限界"}
    st.caption(intensity_labels.get(intensity, ""))

    trigger_options = [
        "食後",
        "ストレス・イライラ",
        "仕事の合間",
        "お酒を飲んでいる",
        "友人が吸っているのを見た",
        "手持ち無沙汰",
        "眠い・疲れた",
        "その他",
    ]
    trigger = st.selectbox("きっかけ（トリガー）", trigger_options)

    resisted = st.radio(
        "結果",
        options=[True, False],
        format_func=lambda x: "💪 我慢できた" if x else "😔 吸ってしまった",
        horizontal=True,
    )

    message = st.text_area(
        "未来の子どもへひとこと（気を紛らわせましょう）",
        placeholder="例：○○ちゃん、パパ今日も頑張ったよ。早く会いたいな。",
        max_chars=200,
    )

    submitted = st.form_submit_button("記録する", type="primary", use_container_width=True)

if submitted:
    add_craving_log(
        intensity=intensity,
        trigger=trigger,
        resisted=resisted,
        message=message,
    )
    if resisted:
        st.success("💪 よく我慢しました！記録しました。")
    else:
        st.info("記録しました。次は絶対に乗り越えられます！")

# ─── 衝動ログ一覧 ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 衝動ログ履歴")

logs = get_craving_logs()
if logs:
    # 我慢成功率の計算
    total = len(logs)
    resisted_count = sum(1 for l in logs if l.get("resisted"))
    success_rate = int(resisted_count / total * 100) if total > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("記録回数", f"{total} 回")
    col2.metric("我慢成功", f"{resisted_count} 回")
    col3.metric("成功率", f"{success_rate}%")

    st.markdown("---")
    # 最近のログを表示（最大10件）
    for log in logs[:10]:
        logged_at = log.get("logged_at", "")[:16].replace("T", " ")
        intensity_val = log.get("intensity", 0)
        trigger_val = log.get("trigger", "")
        resisted_val = log.get("resisted", True)
        message_val = log.get("message", "")

        result_icon = "💪" if resisted_val else "😔"
        stars = "⭐" * intensity_val + "☆" * (5 - intensity_val)

        with st.container():
            st.markdown(
                f"**{logged_at}** {result_icon} 強さ：{stars}  |  きっかけ：{trigger_val}"
            )
            if message_val:
                st.caption(f"💌 {message_val}")
        st.divider()
else:
    st.info("衝動ログはまだありません。上のフォームから記録してみましょう。")

# ─── マイルストーン一覧 ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 マイルストーン一覧")

achieved_keys = {m.key for m in get_achieved_milestones(smoke_free_days)}

for milestone in MILESTONES:
    is_achieved = milestone.key in achieved_keys
    if is_achieved:
        with st.container():
            st.success(f"{milestone.emoji} **{milestone.title}** ✅\n\n{milestone.description}")
    else:
        remaining = milestone.days - smoke_free_days
        with st.container():
            st.markdown(
                f"🔒 **{milestone.title}** — あと{remaining}日\n\n"
                f"<span style='color:gray'>{milestone.description}</span>",
                unsafe_allow_html=True,
            )
