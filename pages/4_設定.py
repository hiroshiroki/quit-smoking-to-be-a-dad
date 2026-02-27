"""
設定画面 - 禁煙開始日・タバコ情報の入力
"""
from datetime import date

import streamlit as st

from utils.supabase_client import get_user_settings, upsert_user_settings

st.set_page_config(page_title="設定", page_icon="⚙️", layout="centered")

st.title("⚙️ 設定")

# ─── 既存設定の読み込み ───────────────────────────────────────────────────────
settings = get_user_settings()

default_quit_date = date.fromisoformat(settings["quit_date"]) if settings else date.today()
default_cigarettes_per_day = settings["cigarettes_per_day"] if settings else 20
default_price_per_pack = settings["price_per_pack"] if settings else 600
default_cigarettes_per_pack = settings.get("cigarettes_per_pack", 20) if settings else 20

# ─── 設定フォーム ────────────────────────────────────────────────────────────
st.subheader("🚭 禁煙設定")

with st.form("settings_form"):
    quit_date = st.date_input(
        "禁煙開始日",
        value=default_quit_date,
        max_value=date.today(),
        help="タバコをやめた日を選択してください",
    )

    st.markdown("#### タバコ情報")
    col1, col2 = st.columns(2)
    with col1:
        cigarettes_per_day = st.number_input(
            "1日の本数",
            min_value=1,
            max_value=100,
            value=default_cigarettes_per_day,
            step=1,
            help="禁煙前に1日に吸っていた本数",
        )
    with col2:
        price_per_pack = st.number_input(
            "1箱の価格（円）",
            min_value=100,
            max_value=5000,
            value=default_price_per_pack,
            step=10,
            help="よく購入していたタバコの1箱の価格",
        )

    cigarettes_per_pack = st.number_input(
        "1箱の本数",
        min_value=1,
        max_value=50,
        value=default_cigarettes_per_pack,
        step=1,
        help="1箱に入っているタバコの本数（通常20本）",
    )

    submitted = st.form_submit_button("設定を保存する", type="primary", use_container_width=True)

if submitted:
    upsert_user_settings(
        quit_date=quit_date,
        cigarettes_per_day=cigarettes_per_day,
        price_per_pack=price_per_pack,
        cigarettes_per_pack=cigarettes_per_pack,
    )
    st.success("✅ 設定を保存しました！")

# ─── 現在の設定プレビュー ────────────────────────────────────────────────────
current = get_user_settings()
if current:
    st.markdown("---")
    st.subheader("📋 現在の設定")

    price_per_cigarette = current["price_per_pack"] / current.get("cigarettes_per_pack", 20)
    price_per_day = price_per_cigarette * current["cigarettes_per_day"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("禁煙開始日", current["quit_date"])
        st.metric("1日の本数", f'{current["cigarettes_per_day"]} 本')
    with col2:
        st.metric("1箱の価格", f'¥{current["price_per_pack"]:,}')
        st.metric("1日の節約額", f"¥{int(price_per_day):,}")

# ─── アプリ情報 ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("ℹ️ このアプリについて")
st.markdown("""
**パパになるための禁煙** は、男性妊活と禁煙サポートを組み合わせた Webアプリです。

禁煙の動機を「赤ちゃんのため」に紐づけることで、長期継続をサポートします。

**主な機能：**
- 🏠 ダッシュボード：禁煙日数・節約金額をリアルタイム表示
- 🚭 禁煙トラッカー：衝動ログ・マイルストーン管理
- 🌿 妊活チェック：栄養・生活習慣の日次記録
- 💌 日記：未来の子どもへのメッセージ
""")
