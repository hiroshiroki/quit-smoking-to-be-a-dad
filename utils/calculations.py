"""
禁煙に関する計算ユーティリティ
"""
import re
from datetime import date, datetime, timedelta, timezone
from typing import Optional

# 日本標準時（UTC+9）
_JST = timezone(timedelta(hours=9))


def _parse_ts(ts_str: str) -> datetime:
    """Supabase の TIMESTAMPTZ 文字列を datetime に変換する。

    Python 3.10 の fromisoformat() はマイクロ秒が正確に6桁でないと失敗するため、
    1〜5桁のマイクロ秒をゼロパディングして正規化する。
    例: '2026-03-01T01:46:44.24046+00:00' → '2026-03-01T01:46:44.240460+00:00'
    """
    s = ts_str.replace("Z", "+00:00")
    s = re.sub(
        r"\.(\d{1,5})([+-])",
        lambda m: f".{m.group(1).ljust(6, '0')}{m.group(2)}",
        s,
    )
    return datetime.fromisoformat(s)


def to_jst_str(utc_str: str) -> str:
    """UTC タイムスタンプ文字列を JST の「YYYY-MM-DD HH:MM」形式に変換する"""
    if not utc_str:
        return ""
    try:
        return _parse_ts(utc_str).astimezone(_JST).strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return utc_str[:16].replace("T", " ")


def get_smoke_free_days(quit_date: date) -> int:
    """禁煙日数を計算する"""
    delta = date.today() - quit_date
    return max(0, delta.days)


def get_smoke_free_hours(quit_date: date) -> int:
    """禁煙時間（時間単位）を計算する"""
    return get_smoke_free_days(quit_date) * 24


def get_saved_money(quit_date: date, cigarettes_per_day: int,
                    price_per_pack: int, cigarettes_per_pack: int = 20) -> int:
    """節約金額を計算する（円）"""
    days = get_smoke_free_days(quit_date)
    price_per_cigarette = price_per_pack / cigarettes_per_pack
    return int(days * cigarettes_per_day * price_per_cigarette)


def get_cigarettes_not_smoked(quit_date: date, cigarettes_per_day: int) -> int:
    """吸わなかったタバコの本数を計算する"""
    return get_smoke_free_days(quit_date) * cigarettes_per_day


def format_money(amount: int) -> str:
    """金額を日本円フォーマットで返す"""
    return f"¥{amount:,}"


def format_days_hours(quit_date: date, quit_datetime_str: Optional[str] = None) -> str:
    """禁煙期間を「○日○時間」形式で返す。

    quit_datetime_str が与えられた場合はその時刻から正確に計算する。
    未指定の場合は quit_date の当日 JST 0時を起点とする。
    """
    now = datetime.now(_JST)
    if quit_datetime_str:
        # DBに記録された正確な時刻（タイムゾーン付き）から計算
        quit_dt = _parse_ts(quit_datetime_str).astimezone(_JST)
    else:
        # fallback: 当日 JST 0時を起点にする
        quit_dt = datetime(quit_date.year, quit_date.month, quit_date.day,
                           0, 0, 0, tzinfo=_JST)
    delta = now - quit_dt
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "0分"
    total_minutes = total_seconds // 60
    if total_minutes < 60:
        return f"{total_minutes}分"
    total_hours = total_minutes // 60
    days = total_hours // 24
    hours = total_hours % 24
    if days == 0:
        return f"{hours}時間"
    return f"{days}日 {hours}時間"


def get_daily_savings_data(
    quit_date: date,
    cigarettes_per_day: int,
    price_per_pack: int,
    cigarettes_per_pack: int = 20,
) -> list[dict]:
    """禁煙開始日から今日までの日別・累積節約金額データを返す

    Returns:
        [{"date": date, "daily": int, "cumulative": int}, ...]
    """
    price_per_cigarette = price_per_pack / cigarettes_per_pack
    daily_saving = int(cigarettes_per_day * price_per_cigarette)

    today = date.today()
    total_days = (today - quit_date).days + 1

    result = []
    cumulative = 0
    for i in range(total_days):
        d = quit_date + timedelta(days=i)
        cumulative += daily_saving
        result.append({"date": d, "daily": daily_saving, "cumulative": cumulative})
    return result
