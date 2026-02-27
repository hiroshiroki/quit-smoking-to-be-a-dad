"""
禁煙マイルストーンの定義（科学的根拠に基づく）
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Milestone:
    """マイルストーンの定義"""
    key: str          # 識別キー
    days: int         # 達成に必要な禁煙日数
    title: str        # タイトル
    description: str  # 詳細説明
    emoji: str        # アイコン


# 科学的根拠に基づくマイルストーン一覧
MILESTONES: list[Milestone] = [
    Milestone(
        key="day_1",
        days=1,
        title="禁煙1日達成！",
        description="血中一酸化炭素濃度が正常値に戻り始めます。体が酸素を効率よく使えるようになります。",
        emoji="🌱",
    ),
    Milestone(
        key="day_3",
        days=3,
        title="禁煙3日達成！",
        description="ニコチンが体内からほぼ排出されます。禁断症状がピークを迎えますが、あと少し！",
        emoji="💪",
    ),
    Milestone(
        key="day_7",
        days=7,
        title="禁煙1週間達成！",
        description="味覚・嗅覚が改善し始めます。精子の酸化ストレスが低下し始めます。",
        emoji="⭐",
    ),
    Milestone(
        key="day_14",
        days=14,
        title="禁煙2週間達成！",
        description="精子の運動率が改善し始めます。血行が良くなり、性機能も回復傾向に。",
        emoji="🎯",
    ),
    Milestone(
        key="day_30",
        days=30,
        title="禁煙1ヶ月達成！",
        description="精子のDNA損傷リスクが低下します。肺機能が著しく改善し、運動能力が上がります。",
        emoji="🏆",
    ),
    Milestone(
        key="day_60",
        days=60,
        title="禁煙2ヶ月達成！",
        description="精子の形態・数が改善傾向に。体全体の酸化ストレスが大幅に低下します。",
        emoji="🌟",
    ),
    Milestone(
        key="day_74",
        days=74,
        title="精子の新サイクル完了！",
        description="精子の生成サイクル（約74日）が完了。禁煙後初めての健康な精子が完成しました！",
        emoji="🍀",
    ),
    Milestone(
        key="day_90",
        days=90,
        title="禁煙3ヶ月達成！",
        description="精子の質（運動率・形態・数）が顕著に改善。妊活に向けて最高の状態に近づいています。",
        emoji="👶",
    ),
    Milestone(
        key="day_180",
        days=180,
        title="禁煙半年達成！",
        description="肺の繊毛機能がほぼ回復。精子の質は非喫煙者と同等レベルになっています。",
        emoji="🎊",
    ),
    Milestone(
        key="day_365",
        days=365,
        title="禁煙1年達成！",
        description="心臓病リスクが喫煙者の半分に。赤ちゃんのために最高の体になりました！",
        emoji="🥇",
    ),
]


def get_achieved_milestones(smoke_free_days: int) -> list[Milestone]:
    """現在の禁煙日数で達成済みのマイルストーン一覧を返す"""
    return [m for m in MILESTONES if smoke_free_days >= m.days]


def get_next_milestone(smoke_free_days: int) -> Optional[Milestone]:
    """次のマイルストーンを返す"""
    upcoming = [m for m in MILESTONES if m.days > smoke_free_days]
    return upcoming[0] if upcoming else None


def get_milestone_by_key(key: str) -> Optional[Milestone]:
    """キーでマイルストーンを検索する"""
    return next((m for m in MILESTONES if m.key == key), None)
