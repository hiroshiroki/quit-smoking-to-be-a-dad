"""
Discord Webhook通知ユーティリティ
環境変数 DISCORD_WEBHOOK_URL が設定されている場合のみ動作する
"""
import os
from typing import Optional

import requests


def is_discord_configured() -> bool:
    """Discord Webhook URLが設定されているか確認する"""
    return bool(os.environ.get("DISCORD_WEBHOOK_URL"))


def send_discord_message(webhook_url: str, content: str) -> bool:
    """Discord Webhookにメッセージを送信する

    Args:
        webhook_url: Discord Webhook URL
        content: 送信するメッセージ本文

    Returns:
        送信成功なら True、失敗なら False
    """
    try:
        response = requests.post(
            webhook_url,
            json={"content": content},
            timeout=10,
        )
        return response.status_code == 204
    except requests.RequestException:
        return False


def send_milestone_notification(milestone_title: str, milestone_description: str) -> bool:
    """マイルストーン達成通知をDiscordに送信する

    Args:
        milestone_title: マイルストーンのタイトル
        milestone_description: マイルストーンの説明

    Returns:
        送信成功なら True、未設定または失敗なら False
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    content = (
        f"🎉 **マイルストーン達成！**\n"
        f"**{milestone_title}**\n"
        f"{milestone_description}"
    )
    return send_discord_message(webhook_url, content)


def send_daily_reminder(days: int, saved_money: int) -> bool:
    """妊活チェック未入力リマインダーをDiscordに送信する

    Args:
        days: 禁煙継続日数
        saved_money: 現在の節約金額（円）

    Returns:
        送信成功なら True、未設定または失敗なら False
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    content = (
        f"👶 **妊活チェックのリマインダー**\n"
        f"今日の妊活チェックをまだ入力していません！\n"
        f"禁煙 **{days}日目**、赤ちゃん貯金 **¥{saved_money:,}** 達成中です。\n"
        f"今日も記録しましょう 💪"
    )
    return send_discord_message(webhook_url, content)


def send_test_message() -> bool:
    """テスト用メッセージをDiscordに送信する

    Returns:
        送信成功なら True、未設定または失敗なら False
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    content = (
        "✅ **パパになるための禁煙** - Discord通知テスト\n"
        "通知の設定が正常に完了しています！"
    )
    return send_discord_message(webhook_url, content)
