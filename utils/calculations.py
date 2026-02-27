"""
禁煙に関する計算ユーティリティ
"""
from datetime import date, datetime
from typing import Optional


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


def format_days_hours(quit_date: date) -> str:
    """禁煙期間を「○日○時間」形式で返す"""
    now = datetime.now()
    quit_datetime = datetime.combine(quit_date, datetime.min.time())
    delta = now - quit_datetime
    total_hours = int(delta.total_seconds() / 3600)
    days = total_hours // 24
    hours = total_hours % 24
    if days == 0:
        return f"{hours}時間"
    return f"{days}日 {hours}時間"
