"""
Supabaseクライアントの初期化と共通データアクセス関数
"""
import os
from datetime import date, datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


@st.cache_resource
def get_supabase_client() -> Client:
    """Supabaseクライアントをシングルトンで返す"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("⚠️ .envファイルにSUPABASE_URLとSUPABASE_KEYを設定してください。")
        st.stop()
    return create_client(url, key)


def _table(table_name: str):
    """smokeスキーマのテーブルを返すヘルパー"""
    return get_supabase_client().schema("smoke").table(table_name)


# ─── user_settings ──────────────────────────────────────────────────────────

def get_user_settings() -> Optional[dict]:
    """ユーザー設定を取得する（最新1件）"""
    res = _table("user_settings").select("*").order("created_at", desc=True).limit(1).execute()
    return res.data[0] if res.data else None


def upsert_user_settings(quit_date: date, cigarettes_per_day: int,
                         price_per_pack: int, cigarettes_per_pack: int = 20) -> dict:
    """ユーザー設定を保存する（既存があれば上書き）"""
    existing = get_user_settings()
    data = {
        "quit_date": str(quit_date),
        "cigarettes_per_day": cigarettes_per_day,
        "price_per_pack": price_per_pack,
        "cigarettes_per_pack": cigarettes_per_pack,
    }
    if existing:
        res = _table("user_settings").update(data).eq("id", existing["id"]).execute()
    else:
        res = _table("user_settings").insert(data).execute()
    return res.data[0]


# ─── craving_logs ────────────────────────────────────────────────────────────

def add_craving_log(intensity: int, trigger: str, resisted: bool,
                    message: str = "") -> dict:
    """衝動ログを追加する"""
    data = {
        "intensity": intensity,
        "trigger": trigger,
        "resisted": resisted,
        "message": message,
    }
    res = _table("craving_logs").insert(data).execute()
    return res.data[0]


def get_craving_logs() -> list[dict]:
    """衝動ログを全件取得（新しい順）"""
    res = _table("craving_logs").select("*").order("logged_at", desc=True).execute()
    return res.data


# ─── fertility_logs ──────────────────────────────────────────────────────────

def get_today_fertility_log() -> Optional[dict]:
    """今日の妊活ログを取得する"""
    today = str(date.today())
    res = _table("fertility_logs").select("*").eq("date", today).limit(1).execute()
    return res.data[0] if res.data else None


def upsert_fertility_log(log_date: date, zinc: bool, folate: bool,
                         sleep_hours: float, exercise: bool,
                         stress: int, notes: str = "") -> dict:
    """妊活ログを保存する（当日分のupsert）"""
    existing = get_today_fertility_log()
    data = {
        "date": str(log_date),
        "zinc": zinc,
        "folate": folate,
        "sleep_hours": sleep_hours,
        "exercise": exercise,
        "stress": stress,
        "notes": notes,
    }
    if existing:
        res = _table("fertility_logs").update(data).eq("id", existing["id"]).execute()
    else:
        res = _table("fertility_logs").insert(data).execute()
    return res.data[0]


def get_fertility_logs() -> list[dict]:
    """妊活ログを全件取得（新しい順）"""
    res = _table("fertility_logs").select("*").order("date", desc=True).execute()
    return res.data


# ─── milestones ──────────────────────────────────────────────────────────────

def get_achieved_milestones() -> set[str]:
    """達成済みマイルストーンのキーセットを返す"""
    res = _table("milestones").select("milestone_key").execute()
    return {row["milestone_key"] for row in res.data}


def achieve_milestone(milestone_key: str) -> None:
    """マイルストーンを達成済みとして記録する"""
    _table("milestones").upsert({"milestone_key": milestone_key}).execute()


# ─── diary_entries ───────────────────────────────────────────────────────────

def add_diary_entry(message: str, mood: str) -> dict:
    """日記エントリーを追加する"""
    data = {
        "date": str(date.today()),
        "message": message,
        "mood": mood,
    }
    res = _table("diary_entries").insert(data).execute()
    return res.data[0]


def get_diary_entries() -> list[dict]:
    """日記エントリーを全件取得（新しい順）"""
    res = _table("diary_entries").select("*").order("date", desc=True).execute()
    return res.data


# ─── partner_shares ──────────────────────────────────────────────────────────

def get_partner_share() -> Optional[dict]:
    """有効なパートナー共有設定を取得する（最新1件）"""
    res = (
        _table("partner_shares")
        .select("*")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def get_partner_share_by_code(code: str) -> Optional[dict]:
    """共有コードで有効なパートナー共有設定を取得する"""
    res = (
        _table("partner_shares")
        .select("*")
        .eq("share_code", code)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def create_partner_share() -> dict:
    """パートナー共有コードを新規生成して保存する

    既存の有効な共有がある場合は無効化してから新規作成する
    share_code は secrets.token_urlsafe(6) の先頭8文字を大文字化した英数字文字列
    """
    import secrets

    # 既存の有効な共有を無効化
    existing = get_partner_share()
    if existing:
        deactivate_partner_share()

    # 8文字の共有コードを生成（英数字大文字）
    share_code = secrets.token_urlsafe(6)[:8].upper()

    res = _table("partner_shares").insert({"share_code": share_code, "is_active": True}).execute()
    return res.data[0]


def deactivate_partner_share() -> None:
    """有効なパートナー共有を無効化する"""
    existing = get_partner_share()
    if existing:
        _table("partner_shares").update({"is_active": False}).eq("id", existing["id"]).execute()


# ─── partner_messages ────────────────────────────────────────────────────────

def add_partner_message(share_code: str, sender: str, message: str) -> dict:
    """パートナーメッセージを追加する

    Args:
        share_code: 共有コード
        sender: 送信者種別（'user' または 'partner'）
        message: メッセージ本文
    """
    data = {
        "share_code": share_code,
        "sender": sender,
        "message": message,
    }
    res = _table("partner_messages").insert(data).execute()
    return res.data[0]


def get_partner_messages(share_code: str) -> list[dict]:
    """指定した共有コードのメッセージを最新50件取得する（新しい順）"""
    res = (
        _table("partner_messages")
        .select("*")
        .eq("share_code", share_code)
        .order("sent_at", desc=True)
        .limit(50)
        .execute()
    )
    return res.data
