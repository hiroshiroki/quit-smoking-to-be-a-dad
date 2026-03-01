"""
禁煙トラッカー画面 - 衝動ログ入力・マイルストーン一覧
"""
from datetime import date, datetime

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from utils.supabase_client import (
    get_user_settings,
    add_craving_log,
    get_craving_logs,
    restart_quit,
    get_quit_attempts,
    get_coping_strategies,
)
from utils.calculations import get_smoke_free_days, to_jst_str
from utils.milestones import MILESTONES, get_achieved_milestones, get_next_milestone

st.set_page_config(page_title="禁煙トラッカー", page_icon="🚭", layout="centered")

st.title("🚭 禁煙トラッカー")

# 再スタートUIの表示フラグを初期化
if "show_restart_ui" not in st.session_state:
    st.session_state["show_restart_ui"] = False
if "restart_smoke_free_days" not in st.session_state:
    st.session_state["restart_smoke_free_days"] = 0

settings = get_user_settings()
if not settings:
    st.warning("設定画面から禁煙開始日を入力してください。")
    st.page_link("pages/4_設定.py", label="設定画面へ →", icon="⚙️")
    st.stop()

quit_date = date.fromisoformat(settings["quit_date"])
smoke_free_days = get_smoke_free_days(quit_date)

# ─── 緊急回避モード ───────────────────────────────────────────────────────────
with st.expander("🆘 今すぐ衝動をかわす", expanded=False):
    st.markdown("**衝動のピークは約5分で過ぎます。一緒に乗り越えましょう！**")

    st.markdown("##### ⏱️ 5分タイマー")
    components.html("""
    <div style="text-align:center; font-family:sans-serif;">
      <div id="timer" style="font-size:3rem; font-weight:bold; color:#e74c3c; letter-spacing:2px;">05:00</div>
      <div style="margin-top:8px; display:flex; gap:8px; justify-content:center;">
        <button onclick="startTimer()" style="padding:6px 16px; font-size:1rem; border-radius:6px; border:none; background:#e74c3c; color:white; cursor:pointer;">スタート</button>
        <button onclick="resetTimer()" style="padding:6px 16px; font-size:1rem; border-radius:6px; border:none; background:#95a5a6; color:white; cursor:pointer;">リセット</button>
      </div>
      <p style="color:#666; margin-top:8px; font-size:0.9rem;">「衝動のピークは5分で過ぎます。この時間を乗り切れば大丈夫！」</p>
    </div>
    <script>
      let remaining = 300;
      let interval = null;
      function updateDisplay() {
        const m = Math.floor(remaining / 60).toString().padStart(2, '0');
        const s = (remaining % 60).toString().padStart(2, '0');
        document.getElementById('timer').textContent = m + ':' + s;
      }
      function startTimer() {
        if (interval) return;
        interval = setInterval(() => {
          remaining--;
          updateDisplay();
          if (remaining <= 0) {
            clearInterval(interval);
            interval = null;
            document.getElementById('timer').textContent = '✅ 乗り越えました！';
          }
        }, 1000);
      }
      function resetTimer() {
        clearInterval(interval);
        interval = null;
        remaining = 300;
        updateDisplay();
      }
    </script>
    """, height=160)

    st.markdown("##### 🧘 深呼吸ガイド（ボックス呼吸）")
    components.html("""
    <div style="text-align:center; font-family:sans-serif; padding:8px 0;">
      <div id="breath-text" style="font-size:1.6rem; font-weight:bold; color:#2980b9; min-height:2.5rem;">準備完了</div>
      <div id="breath-bar-wrap" style="width:200px; height:12px; background:#ecf0f1; border-radius:6px; margin:10px auto;">
        <div id="breath-bar" style="height:100%; width:0%; background:#3498db; border-radius:6px; transition:width linear;"></div>
      </div>
      <button onclick="startBreath()" style="padding:6px 16px; font-size:1rem; border-radius:6px; border:none; background:#2980b9; color:white; cursor:pointer; margin-top:4px;">開始</button>
      <p style="color:#666; margin-top:6px; font-size:0.85rem;">4秒吸う → 4秒止める → 4秒吐く → 4秒止める</p>
    </div>
    <script>
      const phases = [
        {label:'吸う（4秒）', duration:4},
        {label:'止める（4秒）', duration:4},
        {label:'吐く（4秒）', duration:4},
        {label:'止める（4秒）', duration:4},
      ];
      let running = false;
      async function startBreath() {
        if (running) return;
        running = true;
        for (let cycle = 0; cycle < 3; cycle++) {
          for (const phase of phases) {
            document.getElementById('breath-text').textContent = phase.label;
            const bar = document.getElementById('breath-bar');
            bar.style.transition = 'none';
            bar.style.width = '0%';
            setTimeout(() => {
              bar.style.transition = 'width ' + phase.duration + 's linear';
              bar.style.width = '100%';
            }, 50);
            await new Promise(r => setTimeout(r, phase.duration * 1000));
          }
        }
        document.getElementById('breath-text').textContent = '✅ お疲れ様でした';
        document.getElementById('breath-bar').style.width = '100%';
        running = false;
      }
    </script>
    """, height=180)

    st.markdown("##### ✅ 今すぐできる行動")
    st.markdown("""
- 💧 冷たい水を1杯飲む
- 🦷 歯磨きをする
- 🚶 外を5分間歩く
- ✉️ 未来の子どもへ手紙を書く
- 📞 家族や友人に電話する
- 🧊 氷を口に含む
- 🤲 手を温かい水で洗う
""")

st.markdown("---")

# ─── コーピング戦略をロード ───────────────────────────────────────────────────
coping_strategies = get_coping_strategies()

# ─── 衝動ログ入力フォーム ────────────────────────────────────────────────────
st.subheader("😤 「吸いたい」衝動を記録する")
st.caption("衝動を記録することで、トリガーのパターンを把握できます。")

# トリガー選択（コーピング戦略をリアルタイム表示するためフォーム外に配置）
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
trigger_select = st.selectbox("きっかけ（トリガー）", trigger_options)
trigger_other = st.text_input(
    "その他のきっかけ（「その他」を選んだ場合に入力）",
    placeholder="例：会議のプレッシャー、コーヒーを飲んだ",
    max_chars=50,
)

# コーピング戦略をリアルタイム表示
_lookup_key = (trigger_other.strip() or "その他") if trigger_select == "その他" else trigger_select
_strategy = coping_strategies.get(_lookup_key) or coping_strategies.get(trigger_select)
if _strategy:
    st.info(f"💡 **対処法のヒント：** {_strategy}")

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

    submitted = st.form_submit_button("記録する", type="primary", width='stretch')

if submitted:
    # 「その他」が選ばれた場合は自由入力テキストを使用
    trigger = (trigger_other.strip() or "その他") if trigger_select == "その他" else trigger_select
    add_craving_log(
        intensity=intensity,
        trigger=trigger,
        resisted=resisted,
        message=message,
    )
    if resisted:
        st.success("💪 よく我慢しました！記録しました。")
        st.session_state["show_restart_ui"] = False
    else:
        st.warning("記録しました。次は絶対に乗り越えられます！")
        # session_stateで再スタートUIの表示フラグを立てる
        st.session_state["show_restart_ui"] = True
        st.session_state["restart_smoke_free_days"] = smoke_free_days

# ─── 再禁煙サポート（if submitted の外で描画することでボタンが機能する）────
if st.session_state.get("show_restart_ui"):
    st.markdown("---")
    st.info(
        f"**吸ってしまっても失敗ではありません。** 禁煙は挑戦の連続です。\n\n"
        f"あなたはここまで **{st.session_state['restart_smoke_free_days']}日間** 禁煙できていました。その頑張りは本物です。\n\n"
        "また今日から一緒に頑張りましょう！"
    )
    if st.button("🔄 今日から再スタートする", type="primary", width='stretch'):
        restart_quit()
        st.session_state["show_restart_ui"] = False
        st.rerun()

# ─── 衝動ヒートマップ ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗓️ 衝動ヒートマップ（時間帯別）")
st.caption("衝動が起きやすい時間帯・曜日のパターンを把握しましょう")

logs = get_craving_logs()

if len(logs) >= 3:
    # 曜日ラベル（月〜日）
    weekday_labels = ["月", "火", "水", "木", "金", "土", "日"]

    # 時間帯×曜日の件数マトリクスを初期化
    matrix = [[0] * 24 for _ in range(7)]

    from datetime import timezone, timedelta as _td
    _JST = timezone(_td(hours=9))

    for log in logs:
        logged_at_str = log.get("logged_at", "")
        if not logged_at_str:
            continue
        try:
            # UTCでパースしてJST（UTC+9）に変換
            logged_at = datetime.fromisoformat(logged_at_str.replace("Z", "+00:00"))
            logged_at = logged_at.astimezone(_JST)
            hour = logged_at.hour
            # 0=月曜、6=日曜（Python weekday）
            weekday = logged_at.weekday()
            matrix[weekday][hour] += 1
        except (ValueError, AttributeError):
            continue

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=list(range(24)),
            y=weekday_labels,
            colorscale="YlOrRd",
            hovertemplate="曜日: %{y}<br>時間: %{x}時<br>件数: %{z}件<extra></extra>",
            showscale=True,
            colorbar=dict(title="件数"),
        )
    )
    fig_heatmap.update_layout(
        xaxis=dict(
            title="時間帯",
            tickmode="linear",
            tick0=0,
            dtick=3,
            tickvals=list(range(0, 24, 3)),
            ticktext=[f"{h}時" for h in range(0, 24, 3)],
        ),
        yaxis=dict(title="曜日"),
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_heatmap, width='stretch')
else:
    st.info("3件以上記録するとヒートマップが表示されます。")

# ─── 衝動ログ一覧 ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 衝動ログ履歴")

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
        logged_at = to_jst_str(log.get("logged_at", ""))
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

# ─── 挑戦履歴 ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔄 挑戦履歴")

attempts = get_quit_attempts()

if attempts:
    total_attempts = len(attempts)

    # 過去最長記録（終了済み分）
    ended = [a for a in attempts if a.get("days_lasted") is not None]
    max_past_days = max((a["days_lasted"] for a in ended), default=0)

    col_a, col_b = st.columns(2)
    col_a.metric("総挑戦回数", f"{total_attempts} 回")
    col_b.metric("過去最長記録", f"{max_past_days} 日" if max_past_days > 0 else "—")

    st.markdown("---")
    for i, attempt in enumerate(attempts):
        attempt_num = i + 1
        start = attempt["start_date"]
        end = attempt.get("end_date")
        days = attempt.get("days_lasted")

        if end is None:
            # 継続中
            is_best = smoke_free_days >= max_past_days and max_past_days > 0
            label = f"**{attempt_num}回目** — {start} 〜 継続中（{smoke_free_days}日目）"
            st.success(label)
            if is_best:
                st.caption("🎉 今回で過去最長更新中！")
        else:
            label = f"**{attempt_num}回目** — {start} 〜 {end}（{days}日間）"
            st.info(label)
else:
    st.info("挑戦履歴はまだありません。再スタート機能を使うと記録が残ります。")
