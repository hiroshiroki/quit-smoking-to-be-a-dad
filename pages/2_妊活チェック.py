"""
妊活チェックリスト画面 - デイリーチェックと生活習慣記録
"""
from datetime import date

import plotly.graph_objects as go
import streamlit as st

from utils.supabase_client import (
    get_today_fertility_log,
    upsert_fertility_log,
    get_fertility_logs,
)

st.set_page_config(page_title="妊活チェック", page_icon="🌿", layout="centered")

st.title("🌿 妊活チェックリスト")
st.caption("精子の質を高めるための日々の習慣を記録しましょう")

# ─── 今日のチェックリスト入力 ────────────────────────────────────────────────
st.subheader(f"📅 本日のチェック（{date.today().strftime('%Y年%m月%d日')}）")

today_log = get_today_fertility_log()

# 既存データがあればデフォルト値として使う
default_zinc = today_log.get("zinc", False) if today_log else False
default_folate = today_log.get("folate", False) if today_log else False
default_sleep = float(today_log.get("sleep_hours") or 7.0) if today_log else 7.0
default_exercise = today_log.get("exercise", False) if today_log else False
default_stress = int(today_log.get("stress") or 3) if today_log else 3
default_notes = today_log.get("notes", "") if today_log else ""

with st.form("fertility_form"):
    st.markdown("#### 栄養サプリメント")
    col1, col2 = st.columns(2)
    with col1:
        zinc = st.checkbox(
            "🦪 亜鉛を摂取した",
            value=default_zinc,
            help="亜鉛は精子形成に必須のミネラルです（推奨量：10mg/日）",
        )
    with col2:
        folate = st.checkbox(
            "🥬 葉酸を摂取した",
            value=default_folate,
            help="葉酸は精子のDNA品質改善に役立ちます（推奨量：400μg/日）",
        )

    st.markdown("#### 生活習慣")
    sleep_hours = st.number_input(
        "😴 睡眠時間（時間）",
        min_value=0.0,
        max_value=24.0,
        value=default_sleep,
        step=0.5,
        help="7〜8時間の睡眠が精子の質を保ちます",
    )

    exercise = st.checkbox(
        "🏃 運動した（20分以上）",
        value=default_exercise,
        help="適度な有酸素運動は精子の運動率を改善します",
    )

    st.markdown("#### ストレスレベル")
    stress_labels = {
        1: "1 - 非常にリラックス",
        2: "2 - 穏やか",
        3: "3 - 普通",
        4: "4 - やや疲弊",
        5: "5 - 非常にストレスフル",
    }
    stress = st.select_slider(
        "今日のストレスレベル",
        options=[1, 2, 3, 4, 5],
        value=default_stress,
        format_func=lambda x: stress_labels[x],
    )

    notes = st.text_area(
        "📝 メモ（任意）",
        value=default_notes,
        placeholder="今日の体調や気になったことを記録しましょう",
        max_chars=300,
    )

    submitted = st.form_submit_button("保存する", type="primary", width='stretch')

if submitted:
    upsert_fertility_log(
        log_date=date.today(),
        zinc=zinc,
        folate=folate,
        sleep_hours=sleep_hours,
        exercise=exercise,
        stress=stress,
        notes=notes,
    )
    st.success("✅ 今日の記録を保存しました！")

    # スコアを簡易計算して表示
    score = 0
    if zinc:
        score += 25
    if folate:
        score += 25
    if exercise:
        score += 25
    if 6.0 <= sleep_hours <= 9.0:
        score += 15
    if stress <= 2:
        score += 10

    if score >= 80:
        st.balloons()
        st.success(f"🌟 本日の妊活スコア：{score}点 — 素晴らしい！")
    elif score >= 50:
        st.info(f"👍 本日の妊活スコア：{score}点 — 良いペースです！")
    else:
        st.warning(f"💡 本日の妊活スコア：{score}点 — もう少し頑張りましょう！")

# ─── 栄養素の解説 ────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("💡 精子の質を高める栄養素・習慣について"):
    st.markdown("""
| 栄養素/習慣 | 効果 | 目安 |
|------------|------|------|
| 🦪 **亜鉛** | 精子形成・テストステロン産生を促進 | 10mg/日（牡蠣・豚レバー・ナッツ類） |
| 🥬 **葉酸** | 精子のDNA品質を改善、染色体異常を低減 | 400μg/日（緑黄色野菜・納豆） |
| 😴 **睡眠** | テストステロン分泌・精子形成は睡眠中が最も活発 | 7〜8時間/日 |
| 🏃 **運動** | 精子の運動率・濃度を改善、ストレス軽減 | 有酸素運動20〜30分/日 |
| 😌 **ストレス管理** | 高ストレスはコルチゾールを増加させ精子質を低下 | 瞑想・深呼吸・趣味の時間 |
    """)

def _calc_score(log: dict) -> int:
    """妊活ログのスコアを計算する（0〜100点）"""
    score = 0
    if log.get("zinc"):
        score += 25
    if log.get("folate"):
        score += 25
    if log.get("exercise"):
        score += 25
    sleep = log.get("sleep_hours") or 0
    if 6.0 <= float(sleep) <= 9.0:
        score += 15
    stress = log.get("stress") or 3
    if int(stress) <= 2:
        score += 10
    return score


# ─── 生活習慣スコア推移グラフ ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 生活習慣スコアの推移")
st.caption("日々の妊活スコア（0〜100点）の変化を確認しましょう")

logs = get_fertility_logs()
if len(logs) >= 2:
    # 古い順に並べ替え
    sorted_logs = sorted(logs, key=lambda x: x.get("date", ""))
    chart_dates = [log.get("date", "") for log in sorted_logs]
    chart_scores = [_calc_score(log) for log in sorted_logs]

    fig_score = go.Figure()
    fig_score.add_trace(
        go.Bar(
            x=chart_dates,
            y=chart_scores,
            marker_color=[
                "#2ECC71" if s >= 80 else "#F39C12" if s >= 50 else "#E74C3C"
                for s in chart_scores
            ],
            hovertemplate="%{x}<br>スコア: %{y}点<extra></extra>",
        )
    )
    # 目標ライン
    fig_score.add_hline(
        y=80,
        line_dash="dash",
        line_color="rgba(46,204,113,0.6)",
        annotation_text="目標 80点",
        annotation_position="top right",
    )
    fig_score.update_layout(
        xaxis_title="日付",
        yaxis_title="スコア（点）",
        yaxis=dict(range=[0, 105]),
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_score, width='stretch')
else:
    st.info("2日以上記録するとグラフが表示されます。")

# ─── 記録履歴 ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 直近の記録（最大7日間）")

if logs:
    recent_logs = logs[:7]
    for log in recent_logs:
        log_date_str = log.get("date", "")
        try:
            log_date = date.fromisoformat(log_date_str)
            date_label = log_date.strftime("%m/%d（%a）").replace(
                "Mon", "月").replace("Tue", "火").replace("Wed", "水").replace(
                "Thu", "木").replace("Fri", "金").replace("Sat", "土").replace("Sun", "日")
        except ValueError:
            date_label = log_date_str

        zinc_icon = "✅" if log.get("zinc") else "⬜"
        folate_icon = "✅" if log.get("folate") else "⬜"
        exercise_icon = "✅" if log.get("exercise") else "⬜"
        sleep = log.get("sleep_hours") or "-"
        stress_val = log.get("stress") or "-"

        st.markdown(
            f"**{date_label}** | 亜鉛{zinc_icon} 葉酸{folate_icon} 運動{exercise_icon} "
            f"| 睡眠 {sleep}h | ストレス {stress_val}/5"
        )
        if log.get("notes"):
            st.caption(f"  📝 {log['notes']}")
else:
    st.info("記録はまだありません。上のフォームから入力してみましょう。")
