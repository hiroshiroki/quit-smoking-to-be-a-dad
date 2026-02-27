-- ============================================
-- パパになるための禁煙 - Supabaseスキーマ
-- ============================================

-- 禁煙設定テーブル
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    quit_date DATE NOT NULL,               -- 禁煙開始日
    cigarettes_per_day INTEGER NOT NULL,   -- 1日の本数
    price_per_pack INTEGER NOT NULL,       -- 1箱の価格（円）
    cigarettes_per_pack INTEGER DEFAULT 20, -- 1箱の本数
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 衝動ログテーブル
CREATE TABLE IF NOT EXISTS craving_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    logged_at TIMESTAMPTZ DEFAULT NOW(),   -- ログ日時
    intensity INTEGER NOT NULL CHECK (intensity BETWEEN 1 AND 5), -- 衝動の強さ(1-5)
    trigger TEXT,                          -- トリガー（ストレス・食後 など）
    resisted BOOLEAN DEFAULT TRUE,         -- 我慢できたか
    message TEXT,                          -- 子どもへのメッセージ（気を紛らわせる用）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 妊活デイリーチェックテーブル
CREATE TABLE IF NOT EXISTS fertility_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL UNIQUE,             -- 記録日（1日1件）
    zinc BOOLEAN DEFAULT FALSE,            -- 亜鉛摂取チェック
    folate BOOLEAN DEFAULT FALSE,          -- 葉酸摂取チェック
    sleep_hours NUMERIC(3,1),              -- 睡眠時間
    exercise BOOLEAN DEFAULT FALSE,        -- 運動チェック
    stress INTEGER CHECK (stress BETWEEN 1 AND 5), -- ストレスレベル(1-5)
    notes TEXT,                            -- メモ
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- マイルストーン達成テーブル
CREATE TABLE IF NOT EXISTS milestones (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    milestone_key TEXT NOT NULL UNIQUE,    -- マイルストーン識別キー
    achieved_at TIMESTAMPTZ DEFAULT NOW(), -- 達成日時
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 日記テーブル（未来の子どもへのメッセージ）
CREATE TABLE IF NOT EXISTS diary_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL,                    -- 投稿日
    message TEXT NOT NULL,                 -- メッセージ本文
    mood TEXT,                             -- 気分（happy/neutral/tough）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- updated_at自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fertility_logs_updated_at
    BEFORE UPDATE ON fertility_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
