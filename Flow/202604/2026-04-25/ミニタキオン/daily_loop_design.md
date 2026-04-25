# Daily Loop 設計 — ミニタキオンを 1 日の運用ハブにする

Generated: 2026-04-25 22:30
Revised: 2026-04-25 23:00 (田中さんフィードバック反映)
Status: REVISED — 田中さん再レビュー待ち
BL: BL-TBD-004 (ミニタキオン Phase 3: Daily Loop)

---

## 何をしたいか

田中さんは毎朝、複数プロジェクトを横断して「今日何をやるか」を整理している。現状は手作業 (頭の中 + AIPM ファイル確認)。

ミニタキオンに **「☀️ 今日を始める / 🌙 今日を締める」** ボタンを置き、朝/夜のタスク整理 自体を AI に投げて、その案を ミニタキオン上のレビュー物として承認するフローにする。

つまり: **ミニタキオンを「1日の運用ハブ」に進化させる**。

---

## 現状のフロー (やや属人化)

```
朝:
  田中さん → 頭の中で整理 → 手で daily_tasks.md 編集 → AIPM 上で各プロジェクト見回り
日中:
  AI 進行 → 田中さんレビュー (PC + iPhone) → AI 続行
夜:
  田中さん → 寝る前に状況確認 → 次の朝の頭で整理
```

問題:
- 朝の整理が固定プロンプト化されておらず再現性がない (日によってブレる)
- 前日からの引き継ぎが田中さんの記憶頼り
- 整理プロセス自体が記録に残らない

---

## 提案フロー (Daily Loop)

```
☀️ 朝 (8:30 までに開始)
  田中さん [☀️ 今日を始める] → ミニタキオンが
    1. 固定プロンプトで Cockpit task 起動 (朝の整理エージェント)
    2. AI が「今日のタスク案.md」を生成
    3. その日の Flow フォルダに deliverable として登録
       → ミニタキオンの「📅 今日の運用」セクションに登場
  ↓
  田中さんが iPhone で「今日のタスク案」をタップ
    → 内容を読む
    → コメント or 修正依頼 → 承認 [✓ done]
  ↓
  AI が承認に基づき各 BL の priority/state を自動更新
  → 1日が始まる

🟢 日中 (既存通り)
  各 BL を AI が進める / 田中さんレビュー / AI 質問 → 田中さん回答
  ミニタキオンの「レビュー待ち / AIの番」を iPhone で見ながら作業

🌙 夜
  田中さん [🌙 今日を締める] → ミニタキオンが
    1. 固定プロンプトで Cockpit task 起動 (振り返りエージェント)
    2. AI が「今日の振り返り.md」を生成
       - 今日完了したこと / 残課題 / 翌日への申し送り
    3. その日の Flow フォルダに deliverable として登録
    4. STATUS.md を Flow → Stock にマージ (既存 Phase 5 設計と統合)
  ↓
  田中さんが「今日の振り返り」を読んで承認 → 1日終了

🔄 翌朝
  朝の整理エージェントが前日 (なければ前々日…最大 7 日) の振り返りを読んで、
  今日のタスク案を作成 → ループ
```

セーフティネット:
- **03:00 cron** が走り、未締めなら自動で 🌙 を実行 (既設計)
- 翌朝のエージェントが「昨日締めずに走り抜けたよね」を検知してリマインド
- ☀️ を 8:30 までに押し忘れた場合: ホームに「☀️ まだ今日を始めてません」のリマインド表示 (UI 上の警告のみ、自動実行はしない)

スキップ運用:
- 旅行や会議の日も普通に [☀️ 今日を始める] を押す
- 起動した整理エージェントに「今日はスキップ」と伝えれば、AI が短い案 (今日は休 / 重要レビュー無し等) を出す
- 専用「スキップ」ボタンは作らない

---

## 朝の整理エージェントの固定プロンプト

```
あなたは ミニタキオン の「朝の整理」担当エージェントです。

# やること (順番)

1. 「アクティブなプロジェクト」を抽出
   - ~/aipm_v0/Stock/*/*/backlog/ ディレクトリが存在し、
     そこに state ≠ done の BL が 1 件以上ある プロジェクトのみを対象にする
   - backlog を持たないプロジェクトは無視 (静的リファレンス・完了済アーカイブ等)

2. 抽出したプロジェクトについて、以下を読む
   - STATUS.md (現状)
   - backlog/*.yaml の active な BL
     (state, priority, pending_questions, decisions)
   - 当日 Flow に <today>/<project>/deliverables.yaml があれば読む

3. 前日の Daily Wrap-up を読む
   - ~/aipm_v0/Flow/<前日>/_orchestration/今日の振り返り.md
   - 無ければ前々日…と最大 7 日前まで遡って 直近のものを 1 件読む
   - 7 日遡っても無ければ「履歴なし」として進める

4. 以下を含む「今日のタスク案」を Markdown で出力

   # 今日のタスク案 — {YYYY-MM-DD}

   ## 🎯 今日のフォーカス
   <3-5 行で 今日のテーマを集約>

   ## ⏸ レビュー待ち (田中さんの番)
   <pending_questions / 未レビュー成果物 / awaiting_user 状態の BL を 優先順位順>
   - **BL-XXX (project)**: <概要> [推奨アクション]

   ## 🟢 AI 進行リスト
   <今日 AI が進める BL、目安時間付き>
   - **BL-XXX (project)**: <今日やる予定の作業 1-2 行>

   ## 💡 提案
   <新規 BL 案 / scope 変更 / 中止すべき BL>

   ## ❓ 田中さんへの質問
   <タスク整理時点で確認したいこと、なければ「なし」>

5. 出力先: ~/aipm_v0/Flow/<today>/_orchestration/今日のタスク案.md

6. ミニタキオン に成果物として登録:
   - ~/aipm_v0/Flow/<today>/_orchestration/deliverables.yaml に entry 追加
   - review_state: unreviewed
   - cockpit_task_id をエントリに記録 (BL は作らないので deliverable 単独で紐付け)

7. 田中さんに通知 (ミニタキオン上で「📅 今日の運用」に登場)

# 田中さんが done で承認したら

8. AI が以下を自動実行:
   - 「AI 進行リスト」に挙げた BL の priority/state を案どおりに更新
   - 「提案」が承認されたら新規 BL を作成
   - 更新内容を deliverables.yaml の decisions[] に追記
```

---

## 夜の振り返りエージェントの固定プロンプト

```
あなたは ミニタキオン の「夜の振り返り」担当エージェントです。

# やること

1. 当日の Flow から:
   ~/aipm_v0/Flow/<today>/<project>/deliverables.yaml
   - 今日 review_state が done に変わったもの
   - 今日 created_at の新規 deliverable

2. アクティブなプロジェクト (backlog/*.yaml に active BL を持つ) の BL.yaml decisions[] から:
   - 今日 (created_at が today) の decisions

3. 残課題の集計:
   - state が awaiting_user / blocked のままの BL
   - pending_questions[] が空でない BL

4. Markdown で出力:

   # 今日の振り返り — {YYYY-MM-DD}

   ## ✅ 今日完了したこと
   - **BL-XXX**: <変化のサマリー>
   - 成果物 N 件レビュー (done X / needs_revision Y)

   ## 🚧 残課題
   - <未完 BL とブロック理由>
   - <未回答の AI 質問>

   ## 📌 翌日への申し送り
   - <翌朝の整理エージェントが読む情報>
   - <優先的にレビューすべき BL>
   - <新規発見した課題>

   ## 📊 メトリクス (オプション)
   - 動かした BL: N 件
   - レビュー件数: M 件
   - AI 回答件数: K 件

5. 出力先: ~/aipm_v0/Flow/<today>/_orchestration/今日の振り返り.md

6. ~/aipm_v0/Flow/<today>/_orchestration/deliverables.yaml に entry 追加
   - review_state: unreviewed
   - cockpit_task_id をエントリに記録

7. STATUS.md を Flow から Stock にマージ
   - 各プロジェクトの Flow/<today>/<project>/STATUS.md を Stock の永続版にマージ
   - 履歴 append、完了済 union、次アクション 上書き

# 田中さんが done で承認したら

8. AI が以下を自動実行:
   - 翌日への申し送りを 翌朝の整理エージェントが読みやすい形にして保存済み
   - 必要なら新規 BL の作成
   - その日の Flow をクローズ (cron が代行する場合もあり)
```

---

## ファイル配置

朝/夜の整理結果は **その日の Flow フォルダ直下の `_orchestration/`** にまとめる。
プロジェクトごとに分けず、その日の運用はその日に紐づく形。

```
~/aipm_v0/Flow/202604/2026-04-25/
├── _orchestration/                  ← その日の運用ハブ (朝/夜共通)
│   ├── deliverables.yaml            ← 朝/夜 deliverable を 2 件保持
│   ├── 今日のタスク案.md             ← ☀️ 朝の成果物
│   └── 今日の振り返り.md             ← 🌙 夜の成果物
├── ミニタキオン/                     ← 通常プロジェクトの作業
│   └── deliverables.yaml
└── ... (他プロジェクト)
```

- BL-DAILY / BL-WRAPUP のような専用 BL は **作らない** (Stock を汚さない)
- 過去分は Flow フォルダ構造の中にそのまま蓄積され、日付フォルダを辿れば見られる
- 専用「アーカイブ」処理は不要 (どんどん貯まる方針)

---

## 必要な実装 (Phase 3 スコープ)

### A. UI 変更
- ホーム画面の上部に **「☀️ 今日を始める」「🌙 今日を締める」** ボタン
  - 時間帯で強調を切り替え (朝は ☀️ 大、夜は 🌙 大)
  - 既に当日の朝/夜 deliverable があれば、ボタンは「📅 今日の運用へ」リンクに変わる
  - 8:30 までに ☀️ を押していなければ、ホームに警告バッジを出す
- ホーム上部に **「📅 今日の運用」セクション** (既存プロジェクト一覧の上)
  - `Flow/<today>/_orchestration/deliverables.yaml` を直接読み、朝/夜 deliverable をカード表示
  - BL に紐づかない deliverable を ミニタキオン UI で表示できるようにするのが要点
- ホーム下部に **「📚 過去の運用」リンク** (Flow の日付フォルダを日付降順でリスト)

### B. Server Actions
```typescript
// app/actions.ts に追加
async function startDailyLoop(): Promise<Result<{ deliverableId: string }, ...>> {
  // 1. Flow/<today>/_orchestration/ ディレクトリを作成 (なければ)
  // 2. Cockpit task を起動 (固定プロンプト daily-start.md)
  // 3. AI が deliverable を作成 → deliverables.yaml に entry 追記
  //    (cockpit_task_id を deliverable entry に直接保存)
  // 4. revalidatePath
}

async function endDailyLoop(): Promise<Result<{ deliverableId: string }, ...>> {
  // 似たフロー、daily-wrapup.md で起動
}
```

BL を作らないので、cockpit_task_ids は **deliverable entry に直接持たせる** スキーマ変更を入れる。

### C. 固定プロンプトファイル
```
~/.agi-tools/mini-tachyon/lib/prompts/
├── daily-start.md     # 朝の整理プロンプト (上記)
└── daily-wrapup.md    # 夜の振り返りプロンプト
```

### D. deliverables.yaml スキーマの軽微な拡張
- `_orchestration/deliverables.yaml` 用に、entry 単位で `cockpit_task_id` (単数) を持つ形を追加
- `bl_id` は省略可 (Daily Loop deliverable は紐付け先 BL がない)

### E. 03:00 cron との統合
既設計の Phase 5 cron に「未締めなら 🌙 endDailyLoop を実行」を追加。

### F. 承認後の自動更新ロジック
- 田中さんが「今日のタスク案」の deliverable を done に変えたら、
  AI が「AI 進行リスト」に書かれた BL の priority/state を自動更新
- 自動更新はサーバーアクションから Cockpit task に投げる形 (既存ハンドオフを再利用)

### G. テスト
- Server Actions のテスト (deliverable 作成、Cockpit fallback 各分岐、revalidatePath)
- `_orchestration` deliverables.yaml が UI に表示されること

### 工数見積
- Phase 3a: ☀️ ボタン + 朝の整理エージェント + `_orchestration` deliverable 作成 (1-2 日)
- Phase 3b: 🌙 ボタン + 夜の振り返り + Stock マージ (1 日)
- Phase 3c: 03:00 cron との統合 + 承認後自動更新 (半日 + 半日)
- Phase 3d: 「📅 今日の運用」UI + 「📚 過去の運用」リンク (半日)

**合計 3-4 日 (1-2 週末)**

---

## 決定事項 (旧 Open Questions の回答)

| # | 論点 | 決定 |
|---|------|------|
| D1 | 朝/夜 deliverable の置き場所 | Stock に専用プロジェクトを作らず、`Flow/<date>/_orchestration/` に保存 |
| D2 | 1日に作る成果物の数 | 朝 + 夜 で 2 件 (deliverable として) |
| D3 | タスク案の粒度 | BL 優先順位 + 各 BL「今日 AI が進める」内容 1-2 行 |
| D4 | 承認後の AI 権限 | done 承認で AI が priority/state を自動更新 |
| D5 | アーカイブ | なし。Flow フォルダ構造にどんどん貯める。「📚 過去の運用」リンクから日付降順で参照 |
| D6 | ☀️ を押す目標時刻 | **8:30 まで**。朝のうちにやる前提。それ以降はホームに警告バッジ |
| D7 | スキップ機能 | なし。スキップしたい日も ☀️ を押し、エージェントに「今日はスキップ」と伝える |
| D8 | 朝のエージェントの読み込み対象 | **backlog/ に active な BL を持つプロジェクトのみ**。全 Stock 走査ではない |
| D9 | 前日履歴の参照 | 前日 → なければ前々日 → 最大 7 日遡る |

---

## 副次的: 既存運用との整合

- AIPM の 3 ファイル同期 (STATUS / INBOX / daily_tasks) は **既に廃止** 決定 (Phase 4 で実施予定)
- 「daily_tasks.md」を作る役割は **「今日のタスク案.md」が引き継ぐ**
- INBOX は ミニタキオン 自体が引き継ぎ済 (pending_questions[])
- Phase 3 完了で AIPM 散文 3ファイルから完全離脱できる
