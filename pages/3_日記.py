"""
日記画面 - 未来の子どもへのメッセージ
"""
import streamlit as st

from utils.supabase_client import add_diary_entry, get_diary_entries

st.set_page_config(page_title="日記", page_icon="💌", layout="centered")

st.title("💌 未来の子どもへのメッセージ")
st.caption("禁煙を頑張るあなたの気持ちを、未来の赤ちゃんへ残しておきましょう")

# ─── メッセージ投稿フォーム ───────────────────────────────────────────────────
with st.form("diary_form", clear_on_submit=True):
    mood_options = {
        "happy": "😄 うれしい・前向き",
        "neutral": "😐 普通・まあまあ",
        "tough": "😔 つらい・しんどい",
    }
    mood = st.radio(
        "今日の気分",
        options=list(mood_options.keys()),
        format_func=lambda x: mood_options[x],
        horizontal=True,
    )

    message = st.text_area(
        "メッセージ",
        placeholder=(
            "例：\n"
            "今日もタバコを吸わずに頑張れたよ。\n"
            "○○が生まれてきたとき、健康なパパでいたいから。\n"
            "早く会いたいな。"
        ),
        height=150,
        max_chars=1000,
    )

    submitted = st.form_submit_button("保存する 💌", type="primary", use_container_width=True)

if submitted:
    if message.strip():
        add_diary_entry(message=message.strip(), mood=mood)
        st.success("💌 メッセージを保存しました！")
        st.balloons()
    else:
        st.warning("メッセージを入力してください。")

# ─── メッセージ一覧 ──────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📖 これまでのメッセージ")

entries = get_diary_entries()
if entries:
    mood_icons = {"happy": "😄", "neutral": "😐", "tough": "😔"}
    for entry in entries:
        entry_date = entry.get("date", "")
        mood_val = entry.get("mood", "neutral")
        message_val = entry.get("message", "")

        mood_icon = mood_icons.get(mood_val, "😐")

        with st.container():
            st.markdown(f"**{entry_date}** {mood_icon}")
            st.markdown(f"> {message_val}")
        st.divider()
else:
    st.info("メッセージはまだありません。上のフォームから最初のメッセージを書いてみましょう！")
