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


# ─── user_settings ──────────────────────────────────────────────────────────

def get_user_settings() -> Optional[dict]:
    """ユーザー設定を取得する（最新1件）"""
    client = get_supabase_client()
    res = client.table("user_settings").select("*").order("created_at", desc=True).limit(1).execute()
    return res.data[0] if res.data else None


def upsert_user_settings(quit_date: date, cigarettes_per_day: int,
                         price_per_pack: int, cigarettes_per_pack: int = 20) -> dict:
    """ユーザー設定を保存する（既存があれば上書き）"""
    client = get_supabase_client()
    existing = get_user_settings()
    data = {
        "quit_date": str(quit_date),
        "cigarettes_per_day": cigarettes_per_day,
        "price_per_pack": price_per_pack,
        "cigarettes_per_pack": cigarettes_per_pack,
    }
    if existing:
        res = client.table("user_settings").update(data).eq("id", existing["id"]).execute()
    else:
        res = client.table("user_settings").insert(data).execute()
    return res.data[0]


# ─── craving_logs ────────────────────────────────────────────────────────────

def add_craving_log(intensity: int, trigger: str, resisted: bool,
                    message: str = "") -> dict:
    """衝動ログを追加する"""
    client = get_supabase_client()
    data = {
        "intensity": intensity,
        "trigger": trigger,
        "resisted": resisted,
        "message": message,
    }
    res = client.table("craving_logs").insert(data).execute()
    return res.data[0]


def get_craving_logs() -> list[dict]:
    """衝動ログを全件取得（新しい順）"""
    client = get_supabase_client()
    res = client.table("craving_logs").select("*").order("logged_at", desc=True).execute()
    return res.data


# ─── fertility_logs ──────────────────────────────────────────────────────────

def get_today_fertility_log() -> Optional[dict]:
    """今日の妊活ログを取得する"""
    client = get_supabase_client()
    today = str(date.today())
    res = client.table("fertility_logs").select("*").eq("date", today).limit(1).execute()
    return res.data[0] if res.data else None


def upsert_fertility_log(log_date: date, zinc: bool, folate: bool,
                         sleep_hours: float, exercise: bool,
                         stress: int, notes: str = "") -> dict:
    """妊活ログを保存する（当日分のupsert）"""
    client = get_supabase_client()
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
        res = client.table("fertility_logs").update(data).eq("id", existing["id"]).execute()
    else:
        res = client.table("fertility_logs").insert(data).execute()
    return res.data[0]


def get_fertility_logs() -> list[dict]:
    """妊活ログを全件取得（新しい順）"""
    client = get_supabase_client()
    res = client.table("fertility_logs").select("*").order("date", desc=True).execute()
    return res.data


# ─── milestones ──────────────────────────────────────────────────────────────

def get_achieved_milestones() -> set[str]:
    """達成済みマイルストーンのキーセットを返す"""
    client = get_supabase_client()
    res = client.table("milestones").select("milestone_key").execute()
    return {row["milestone_key"] for row in res.data}


def achieve_milestone(milestone_key: str) -> None:
    """マイルストーンを達成済みとして記録する"""
    client = get_supabase_client()
    client.table("milestones").upsert({"milestone_key": milestone_key}).execute()


# ─── diary_entries ───────────────────────────────────────────────────────────

def add_diary_entry(message: str, mood: str) -> dict:
    """日記エントリーを追加する"""
    client = get_supabase_client()
    data = {
        "date": str(date.today()),
        "message": message,
        "mood": mood,
    }
    res = client.table("diary_entries").insert(data).execute()
    return res.data[0]


def get_diary_entries() -> list[dict]:
    """日記エントリーを全件取得（新しい順）"""
    client = get_supabase_client()
    res = client.table("diary_entries").select("*").order("date", desc=True).execute()
    return res.data
