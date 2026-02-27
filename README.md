# 👶 パパになるための禁煙

男性妊活 × 禁煙サポート Web アプリケーション

禁煙の動機を「赤ちゃんのため」に紐づけることで、長期継続をサポートします。
科学的根拠に基づいた精子への効果を可視化し、禁煙のモチベーションを維持します。

---

## 機能一覧

| 画面 | 機能 |
|------|------|
| 🏠 ダッシュボード | 禁煙日数・節約金額のリアルタイム表示、マイルストーン進捗、本日のチェック状況 |
| 🚭 禁煙トラッカー | 「吸いたい」衝動ログ（強度・トリガー・我慢成否）、マイルストーン一覧 |
| 🌿 妊活チェック | 亜鉛・葉酸・睡眠・運動・ストレスの日次チェックリスト |
| 💌 日記 | 未来の子どもへのメッセージ投稿・閲覧 |
| ⚙️ 設定 | 禁煙開始日・1日の本数・タバコ価格の設定 |

---

## 技術スタック

| 区分 | 技術・サービス |
|------|--------------|
| フロントエンド | [Streamlit](https://streamlit.io/) |
| バックエンド / DB | [Supabase](https://supabase.com/)（無料枠：500MB・50,000行） |
| デプロイ | [Streamlit Community Cloud](https://streamlit.io/cloud)（無料） |
| グラフ | Plotly / Altair（Phase 2で追加予定） |
| 通知 | LINE Notify（Phase 3で追加予定） |

---

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <your-repo-url>
cd smoke
```

### 2. Supabase の設定

既存プロジェクトへの同居、または新規プロジェクトどちらでも対応しています。
テーブルはすべて `smoke` スキーマ内に作成されるため、他プロジェクトのテーブルと衝突しません。

#### 2-1. テーブルの作成

プロジェクトの **SQL Editor** を開き、`schema.sql` の内容を貼り付けて実行します。

#### 2-2. `smoke` スキーマの公開（必須）

デフォルトでは `public` スキーマしか公開されていないため、以下の設定が必要です。

1. Supabase ダッシュボード → **Settings → API**
2. **「Exposed schemas」** に `smoke` を追加
3. **「Save」** をクリック

> この設定をしないと API からのアクセスが拒否されます。

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、Supabase の接続情報を記入します。

```bash
cp .env.example .env
```

`.env` を編集：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

> **接続情報の確認場所：** Supabase ダッシュボード → Project Settings → API

### 4. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 5. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

---

## 初回セットアップ

アプリ起動後、まず **設定** 画面（サイドバーの「4_設定」）から以下を入力してください。

- 禁煙開始日
- 1日に吸っていた本数
- 1箱の価格

設定を保存するとダッシュボードに禁煙日数・節約金額が表示されます。

---

## ファイル構成

```
smoke/
├── app.py                  # ホーム（ダッシュボード）
├── pages/
│   ├── 1_禁煙トラッカー.py  # 衝動ログ・マイルストーン
│   ├── 2_妊活チェック.py    # デイリーチェックリスト
│   ├── 3_日記.py           # 未来の子どもへのメッセージ
│   └── 4_設定.py           # 禁煙設定・タバコ情報
├── utils/
│   ├── supabase_client.py  # DB操作関数
│   ├── calculations.py     # 禁煙日数・節約金額計算
│   └── milestones.py       # マイルストーン定義（科学的根拠）
├── schema.sql              # Supabase テーブル作成 SQL
├── requirements.txt        # 依存パッケージ
├── .env.example            # 環境変数テンプレート
└── README.md
```

---

## Streamlit Community Cloud へのデプロイ

1. GitHub にリポジトリを push（`.env` は **push しない**）
2. [Streamlit Community Cloud](https://share.streamlit.io/) にログイン
3. 「New app」→ リポジトリ・ブランチ・`app.py` を選択
4. 「Advanced settings」→ Secrets に環境変数を設定：

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

5. 「Deploy」をクリック

---

## マイルストーン一覧

禁煙日数に応じて、科学的根拠に基づくマイルストーンが解除されます。

| 日数 | マイルストーン |
|------|--------------|
| 1日 | 血中一酸化炭素濃度が正常値に回復 |
| 3日 | ニコチンが体内からほぼ排出 |
| 7日 | 精子の酸化ストレスが低下し始める |
| 14日 | 精子の運動率が改善し始める |
| 30日 | 精子の DNA 損傷リスクが低下 |
| 60日 | 精子の形態・数が改善傾向に |
| 74日 | 精子の新サイクル完了（約74日サイクル） |
| 90日 | 精子の質が顕著に改善 |
| 180日 | 精子の質が非喫煙者と同等レベルに |
| 365日 | 心臓病リスクが喫煙者の半分に |

---

## 今後の実装予定

### Phase 2
- 衝動ヒートマップ（時間帯別グラフ）
- 節約金額の累積グラフ
- 生活習慣スコアの推移グラフ

### Phase 3
- LINE Notify 連携（毎朝リマインド・マイルストーン通知）
- PWA 対応（スマホのホーム画面に追加可能）
- パートナー共有機能
