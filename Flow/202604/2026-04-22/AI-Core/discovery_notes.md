# AI-Core PL作成（BL-0061） 探索メモ

- 作成日: 2026-04-22
- 担当: 田中利空
- 関連: BL-0061（AIコア PL作成・本タスク） / BL-0054（AI-Core 共用リポジトリ・ファイル共有設計・doing） / BL-0053（AIOSアップデート + G-Brain統合）
- 起点: 2026-04-22 朝の Daily Tasks（クラスA / 第一さんHTML起点・UI作成済み・DB付きデプロイへ）

---

> **2026-04-22 更新（v4 / Slack 削除反映後）**: Q-impl への田中回答で **Slack 通知を削除**。運用は Notion の `Status=未対応` ビュー巡回に統一。確定後の方針は `implementation_plan.md` v2.1 を参照。

## 1. 結論サマリー（v4）

| 項目 | 状況 | 補足 |
|---|---|---|
| 第一さんから届いた **HTML** | ✅ **確定** | `~/Downloads/AI秘書事業_事例集_v1.html`（2026-04-22 11:08, 137KB, 1994 行） |
| 「第一さん」の正体 | ✅ **確定** | **町田第一さん**（実在。エージェントの「大地さん」推測は誤り） |
| 既存の **UI**（チェック→登録） | ✅ **方針確定** | (b) HTML そのものを UI と扱い、チェックボックス＋送信機能を後付け |
| **デプロイ先（Vercel）** | ✅ **確定** | 既存ダッシュボードと同 Vercel team（orgId: `team_SxSmIbPKgsqBRWJz5I9KL4tO`）に新規プロジェクトを作成 |
| **DB** | ✅ **確定（v3で転換）** | **Notion**（事例一覧 / クライアント依頼 の 2 DB）。Postgres/Prismaは使わない。Admin画面も Notion で代替 |
| **通知** | ✅ **確定（v4で削除）** | **Slack 通知なし・Notion 運用のみ**。新規提出は `Status=未対応` で入り、田中／町田さんが Notion 側のビューで定期確認 |
| **GitHub** | ✅ **確定** | `RestaurantAILab` org に新規リポジトリ `ai-core-pl` |
| **規約参照元** | ✅ **特定** | `~/RestaurantAILab/Dashboard`（Next.js + Prisma + Neon）。Notion化により ORM/DBは継承しないが、Vercel team / GitHub org / Next.js は同規約 |
| **AI-Core プロジェクトの aipm_v0 Stock 登録** | ✅ **完了（2026-04-22）** | PONさん案件方式で `Stock/RestaurantAILab/AI-Core/` を新設（README/ProjectIndex/log）。MasterIndex 更新済。実体は Markdowns-1 |

---

## 2. 第一さん HTML 候補の中身

`~/Downloads/AI秘書事業_事例集_v1.html`

- **タイトル**: 「AI秘書 導入事例集 v1 — 月120〜160時間が戻る50の実例」
- **eyebrow**: 「AIOS / AI Core 導入事例 — 2026年版」
- **brand**: 「AI 秘書 導入事例集」（footerあり、署名なし）
- **デザイン**: Buddy Design System tokens（CSS変数で定義）
- **ナビ構成**: 1日の変化 / 解ける経営課題 / 11カテゴリ / 50事例 / はじめの一歩 / お問い合わせ
- **本体**: 11カテゴリ × 計50事例

### 2.1 構造化された事例データ（→ そのまま PL の選択肢として使える）

各事例は次のスキーマで定義されている。

```html
<article class="case"
         data-id="29"
         data-category="F"
         data-tools="slack,notion"
         data-frequency="morning,evening"
         data-role="ceo"
         data-difficulty="3">
  <div class="case-head">
    <span class="case-id">#29</span>
    <h3 class="case-title">個人活動の可視化（ワーク・アナリティクス）</h3>
    <span class="badge done">実装済み</span>  <!-- or proposed=応用提案 -->
  </div>
  <div class="case-grid">
    <div class="case-field pain-field"><label>こんな悩みに</label> ...</div>
    <div class="case-field"><label>AI 秘書がやること</label> ...</div>
    <div class="case-field"><label>データの流れ</label> ...</div>
    <div class="case-field"><label>頻度・所要時間</label> ...</div>
    <div class="case-field"><label>効果（推定）</label> ...</div>
    <div class="case-field"><label>使う道具</label> ...</div>
  </div>
</article>
```

抽出可能な属性:

| 属性 | 値の取りうる範囲 | 備考 |
|---|---|---|
| `data-id` | 1〜50 | 事例ID。PRIMARY KEY 候補 |
| `data-category` | A〜K（11種） | 朝の経営ダッシュボード / 週次マネジメント / MTG / 顧客営業分析 / 戦略意思決定 / チーム運営 / ナレッジ / 財務法務CS / マーケPRIR / 個人ライフ / 自動化の自動化 |
| `data-tools` | notion, slack, salesforce, gmail, sheets, recording, jira, ... | カンマ区切り（マルチ） |
| `data-frequency` | morning, evening, night, weekly, ondemand, event, ... | カンマ区切り（マルチ） |
| `data-role` | ceo, hr, sales, cs, backoffice | カンマ区切り（マルチ） |
| `data-difficulty` | 1〜3 | 導入難易度 |
| `badge` | `done`（実装済み） / `proposed`（応用提案） | 提供可否のマーカー |

### 2.2 11カテゴリ一覧（HTMLから抽出）

| code | カテゴリ | 月削減目安 | 件数 |
|---|---|---|---|
| A | 朝の経営ダッシュボード | 30–40h | 5 |
| B | 週次マネジメント | 15–20h | 6 |
| C | MTG・議事録運営 | 15–20h | 5 |
| D | 顧客・営業分析 | 15–20h | 5 |
| E | 戦略・意思決定 | 10–15h | 5 |
| F | チーム運営・人事 | 5–10h | 4 |
| G | ナレッジ運用 | 5–10h | 5 |
| H | 財務・法務・CS | 10–15h | 4 |
| I | マーケ・PR・IR | 10–15h | 4 |
| J | 個人・ライフ | 3–5h | 3 |
| K | 自動化の自動化 | — | 4 |

**合計 50 事例**。`badge` で「実装済み」と「応用提案」が混在するので、PL UI ではフィルタ／表示出し分けが必要になる可能性大。

---

## 3. 「PL」の意味の再定義（重要）

ユーザー(田中)説明:
> 提供メニューをチェックして登録できる Price List (PL)
> ユーザー（飲食店クライアント）が「我々が提供しているメニューのうちこれが欲しい」をチェックして登録

→ PL = **Price List = 提供サービス選択リスト**（飲食店経営でいう Profit & Loss ではない）。

Backlog.md `BL-0061` の Notes には「AIコアプロジェクトのPL（損益計算）を作成」とあるが、これは **誤記**。後続の `update Backlog` ステップで修正する。

また、AI-Core 6ヶ月レビュー（`team_economics_report.md` ほか）でも:
> 価格と提供メニューは固まっていない。営業のたびに「何をいくらで売るか」を再設計している
> 提供範囲と料金体系を明文化する。講義・伴走・設定代行・自動化実装・外部連携・データ移行・チーム展開を分け、基本プランと追加オプションを明示する

と明示されており、**「50事例を提供メニューカタログ化し、クライアントに『これを欲しい』を選んでもらう」フローはこの戦略課題に直接効く**。つまり HTML→PL は単なる作業ではなく、AI-Core 営業オペレーションの基盤になる位置づけ。

ただし ユーザー説明の「**飲食店クライアント**がチェックして登録」と HTML の「**B2B SaaS 経営者**向け事例集」には対象が一致しない部分がある（HTML lead は「社員数十名の B2B SaaS 企業の経営者」と明記）。要確認。

---

## 4. 既存 UI 探索結果（見つからず）

ユーザー説明: 「UIは既に作成済み」「バックエンドのある場所にデプロイするだけの状態」

### 探索場所

- `~/RestaurantAILab/` 直下の全リポジトリ（package.json で確認）
  - albert / c5med-booking / ChefsAssistant / ChefsAssistant_old / DailyAgent2_2 / Dashboard / Dashboard-Kai / GenAI_Example / gfs_AIDailyReport / haccp-temperature-app / LineAPITester / module-cook / RunwayAPITest / voice-beauty-advisor
  - **PL/事例集/メニュー選択 を扱うものは無し**
- `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/`（成果物の正側）
  - 共通提供基盤 / 次期戦略案 配下に Markdown はあるが、UI 実装ファイル無し
- `~/RestaurantAILab/Markdowns-1/Flow/202604/2026-04-21/AI-Core/`
  - `AI-Core_Cursor導入後のおすすめ設定.md` のみ（UI と無関係）
- `~/RestaurantAILab/Markdowns-1/outputs/`
  - レビュー成果物のみ（UI 無し）
- `~/Downloads/`, `~/Desktop/`
  - 該当する追加 HTML/JS は無し

### 仮説

| 仮説 | 妥当性 | 補足 |
|---|---|---|
| (a) 既存UI = HTMLそのもの。チェックボックスを差し込んで送信機能を付けるだけ | 中 | 50事例カードが既にある。各カードに `<input type="checkbox" name="case-{id}">` を足してフォーム化するのは比較的軽い |
| (b) 既存UI = 別リポにあり、田中のローカルに無い（町田さん側 or 別マシン） | **高** | 「UIは既に作成済み」の主語が町田大地さんなら、彼のリポジトリに存在する可能性が高い |
| (c) 既存UI = 直近で v0 / Bolt / Claude等で生成したミドルウェア（ローカル外） | 低中 | デザイン感は v0 由来っぽいが、コードのローカル所在確認が必要 |
| (d) ユーザー記憶違いで UI は未作成 | 低 | 棚卸ノートにも UI 完成の記述なし |

→ **ユーザー確認必須**。

---

## 5. デプロイ先 / DB 候補の現状

### 5.1 デプロイ先候補

- ダッシュボード改 = Vercel + Neon 構成（推測）
- BL-0064「Vercel アカウント整理」が同時 todo（複数アカウントで散らばっている）
- AI-Core 用に独立プロジェクトを切るのが筋。ただし既存 Vercel チームのどこに置くか要確認

### 5.2 DB 候補

| 候補 | 妥当性 | コメント |
|---|---|---|
| Neon Postgres（新規DB / 共有Neonの新DB） | **高** | ダッシュボード改と同スタックで運用知見あり。AI-Core 用に新DB を切るのが安全 |
| Vercel Postgres（=Neon の Vercel 統合） | 中 | プロジェクト紐づけが楽 |
| Supabase | 低 | 既存資産なし |
| Sheets/Notion 直書き | 低中 | 「DB付き」要件にやや弱いが、軽い PoC ならあり |

### 5.3 想定スキーマ（ドラフト）

```sql
-- 提供メニュー（HTML から seed）
CREATE TABLE service_cases (
  id           INT PRIMARY KEY,                 -- data-id (1..50)
  category     CHAR(1) NOT NULL,                -- A..K
  title        TEXT NOT NULL,
  pain         TEXT,
  what_ai_does TEXT,
  data_flow    TEXT,
  frequency    TEXT,         -- HTML 表記の生文字
  effect       TEXT,
  tools        TEXT,         -- HTML 表記の生文字
  -- 検索用 normalized
  tools_arr    TEXT[],       -- ["notion","slack"]
  freq_arr     TEXT[],
  role_arr     TEXT[],
  difficulty   SMALLINT,     -- 1..3
  status       TEXT          -- 'done' | 'proposed'
);

-- クライアント
CREATE TABLE clients (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,         -- 店舗名 or 会社名
  contact     TEXT,
  segment     TEXT,                  -- 'restaurant' | 'b2b_saas' | ...
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 提案セッション（1クライアント × N回）
CREATE TABLE selection_sessions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id   UUID REFERENCES clients(id),
  submitted_at TIMESTAMPTZ DEFAULT now(),
  notes       TEXT
);

-- 選択結果
CREATE TABLE selected_cases (
  session_id  UUID REFERENCES selection_sessions(id),
  case_id     INT REFERENCES service_cases(id),
  priority    SMALLINT,            -- 1..3 (任意)
  PRIMARY KEY(session_id, case_id)
);
```

> 「価格」を持たせるかは要確認（「Price List」と命名されているが、HTMLには金額が無い。価格は別レイヤで管理する可能性）。

---

## 6. AIOS的な未整備（要決定）

- **`Stock/MasterIndex.yaml` に AI-Core プロジェクトが未登録**
  - 同一の `AI-Core` という program 名は `~/RestaurantAILab/Markdowns-1/Stock/MasterIndex.yaml` 側に既に存在
  - aipm_v0 側で扱う場合、「AI-Core を RestaurantAILab program 配下のプロジェクトとして新設するか」「Markdowns-1 にポインタ的README だけ置くか」の方針が必要
- **作業フォルダ命名は OK**: `Flow/202604/2026-04-22/AI-Core/` （朝の Daily Tasks で生成済み）
- AIOSルール `02_project_init.mdc` の確認は、上記方針が決まってから実施

---

## 7. 他の関連バックログとの干渉

| BL ID | 状態 | 干渉点 |
|---|---|---|
| BL-0054 | doing（2026-04-21着手） | 共用リポジトリ・ファイル共有設計。AI-Core PL のリポジトリ配置先（共用か個別か）は BL-0054 の決定に従うべき |
| BL-0053 | todo | AIOSアップデート + G-Brain 統合。AI-Core 関連の Stock 設計に影響。当日の Daily Tasks では「BL-0053 完了後に BL-0054 着手」と明記 |
| BL-0064 | todo | Vercel アカウント整理。デプロイ先決定の前提 |

→ 厳密に直列化すると BL-0053 → BL-0054 → BL-0064 → BL-0061 の順になり詰まる。BL-0061 を独立進行させるなら、**「暫定の独立リポジトリ + 個人 Vercel アカウント + AI-Core 専用 Neon DB」で割り切る** 案が現実的。後で BL-0054 の決定に合わせて移行。

---

## 8. 次アクション（推奨）

1. ユーザー確認（`questions_to_user.md` 参照）
   - 「第一さん」の正体・HTML特定（候補1で合っているか）
   - 既存UIの所在
   - デプロイ先・DBの方針
   - PL の対象セグメント（飲食店 vs B2B SaaS 経営者）と価格情報の有無
   - AI-Core を aipm_v0 Stock に登録するか
2. 回答が揃い次第、`implementation_plan.md` を確定（DBスキーマ確定 / API設計 / フロント実装範囲 / 段階デプロイ）
3. 並行して、HTML を「機械可読 JSON 化」できる軽いパースツールを作っておくと、UI 着手時にすぐ使える（任意・先行可能）

---

## 9. 参照ファイル一覧

- HTML候補: `/Users/rikutanaka/Downloads/AI秘書事業_事例集_v1.html`
- 朝のDaily Tasks: `Flow/202604/2026-04-22/0422_daily_tasks.md`
- 棚卸ノート: `Flow/202604/2026-04-19/RestaurantAILab総括/これまでの取り組み棚卸し.md`
- AI-Core README: `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/README.md`
- 共通提供基盤 README: `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/共通提供基盤/README.md`
- 次期戦略案 README: `~/RestaurantAILab/Markdowns-1/Stock/AI-Core/次期戦略案/2026-04-04_商品設計プラン/README.md`
- 6monthレビュー: `~/RestaurantAILab/Markdowns-1/outputs/ai-core_review_2026-04-04/`, `~/RestaurantAILab/Markdowns-1/outputs/ai-core-6month-review-20260404/`
- Backlog: `Stock/定型作業/バックログ/Backlog.md`（BL-0061 / BL-0054 / BL-0053 / BL-0064）
