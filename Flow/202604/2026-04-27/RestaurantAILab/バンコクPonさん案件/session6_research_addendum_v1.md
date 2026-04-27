# 第6回セッション 追加調査メモ — Cursor「自動実行エージェント」と iCloud → Google Calendar 移行

- 作成: 2026-04-27 (BL-0073)
- 対象: PONさん 第6回セッション (本日本番) 直前の前提整理
- 田中さん指示の起点: Q1 への回答（Mac/個人端末/MDMなし、Googleアカウント保有、iCloud→Google 完全移行運用）
- 補足対象資料: `session6_outline_v2.md` / `session6_content_draft_v2.md`

---

## TL;DR (本番でPONさんに伝える結論)

1. **「特定プロンプトを定期実行」する Cursor の機能は `Cursor Automations`（クラウドエージェント／cron 起動）。** Background Agent / Auto-Run とは別物。コード／GitHub文脈前提なので、PONさんの普段使いには **代替（Claude Desktop Scheduled Tasks / ChatGPT Tasks / Zapier 等）の併走提示が現実的**。
2. **iCloud カレンダーは Mac で「カレンダーアーカイブ (.icbu)」として一括エクスポート可能**だが、**Google には取り込めない**（Apple独自形式）。Google 移行用には **`.ics` を1カレンダーずつ書き出す**のが正攻法。PON さんは数カレンダー想定なので2〜3分で完結する見込み。

---

## 1. Cursor の「自動実行エージェント」整理

PONさんが指す「自動実行エージェント」= **特定プロンプトを定期的にLLMで回す機能**。Cursor には類似機能が **3層** 存在し、今回該当するのは ③ Cursor Automations。

### ① Auto-Run モード（フォアグラウンド）
- IDE 内の通常 Cursor Agent が、ターミナルコマンドを毎回確認なしで連続実行（旧 YOLO mode）
- **Macローカル**動作。GitHub不要
- `Cursor Settings → Features → Agent → Auto-run mode` を ON
- **PONさん用途には合致しない**（手動 + 自動承認、定期実行ではない）

### ② Background Agent
- AWS Ubuntu VM 上でクラウド自走（最大8並列、Macを閉じても継続）
- ⌘E で起動 / GitHub 連携 + リポジトリ必須 / Max モデル課金
- **PONさん用途には合致しない**（依頼起点で動く、定期実行ではない）

### ③ Cursor Automations ← 今回の本命
- **クラウドエージェントを cron / イベントで自動起動**する機能
- 設定: [cursor.com/automations](https://cursor.com/automations)
- トリガー:
  - **cron スケジュール**（毎朝9時 / 2時間ごと 等）
  - GitHub PR / マージ / CI 完了
  - Slack / Linear / Sentry / PagerDuty / Webhook
- ユースケース（公式提示）: 機能フラグ清掃、脆弱性検出、Sentryトリアージ、PRレビュー
- 課金: クラウドエージェント使用量ベース（トークン従量）
- **動作環境**: 完全クラウド（ローカル実行不可）

### Automations の限界（PONさん視点）

| 観点 | 状況 |
|---|---|
| 用途想定 | コード保守・GitHubリポ前提のワークフロー中心 |
| 「単純に毎朝LLMにプロンプトを投げて結果を通知」 | できなくはないが過剰スペック。設計上は開発者向け |
| 結果の出力先 | Slack / GitHub / Linear / Webhook が主。メールやLINE直送は別途連携が必要 |
| セットアップ難易度 | 中（GitHub/Slack 連携、トリガー設計が必要） |

### 代替案（PONさんが「コードと無関係に毎日プロンプトを回したい」場合）

| ツール | 特徴 | PONさん適性 |
|---|---|---|
| **Claude Desktop Scheduled Tasks** | GUI、PC を閉じても動く（Claude Desktop 常駐前提） | ◎ 個人運用に最適 |
| **ChatGPT Tasks (Scheduled)** | ChatGPT 内蔵のスケジュール機能 | ◎ 既存ChatGPTを使うなら最短 |
| **Claude Code `/loop`** | セッション内ループ。手元作業向き | ○ 開発者寄り |
| **Zapier / Make + LLM API** | ノーコード、トリガー多彩、メール/LINE連携可 | ◎ 業務フロー組込みに強い |
| **Cursor Automations** | 開発文脈の本命 | △（コード作業を本格化したら） |

### セッションでの提示方針案
- Part「Cursor で AI を自動実行」では **Auto-Run（自動承認）→ Background Agent（クラウド自走）→ Automations（定期実行）** の3層を明示
- 「PONさんの“自動実行”ニーズが定期実行ならCursor単体では過剰。**Claude Desktop Scheduled Tasks か ChatGPT Tasks** が最短ルート」とフラットに提示
- Cursor Automations の本領が出るのは PONさんが GitHub リポでの開発に踏み込んだ後、と整理

---

## 2. iCloud → Google Calendar 移行（PONさん運用: 完全移行）

### 結論
- **Mac から `.icbu` 一括エクスポートは可能だが Google には取り込めない**
- **Google 移行には `.ics` を1カレンダーずつ書き出す** のが公式かつ確実
- iCloud上の **過去〜未来の予定すべて**（繰り返し含む）は `.ics` に含まれる

### 一括（.icbu）が使えない理由
- `.icbu` = Apple Calendar Archive（Apple 独自バックアップ形式）
- **Google Calendar インポートが受け付けるのは `.ics` または `.csv` のみ**
- `.icbu` は別Macの カレンダー.app への復元用途専用

### 推奨フロー（Mac 経由 / 個別エクスポート）

#### Step A: Mac カレンダー.app から `.ics` 書き出し（カレンダーごと）
1. カレンダー.app を開く
2. サイドバーで対象カレンダー名（例: 「ホーム」「仕事」）をクリック
3. **ファイル → 書き出す → 書き出す…**
4. 保存先指定 → 書き出す
5. `.ics` ファイル取得
6. 複数ある場合は2〜5を繰り返す

#### Step B: Google Calendar に取り込み
1. [calendar.google.com](https://calendar.google.com) を開く
2. ⚙ → 設定 → インポート / エクスポート
3. パソコンからファイルを選択 → `.ics` を選ぶ
4. 「予定の追加先カレンダー」で取り込み先を指定（必要なら事前に同名カレンダーを作成）
5. インポート
6. 複数ファイルなら繰り返す

#### Step C: 完全移行運用に切替
- **iPhone**: 設定 → カレンダー → アカウント → Googleアカウント追加（カレンダーON）。 設定 → カレンダー → デフォルトカレンダー → Googleカレンダーを既定に
- **Mac**: システム設定 → インターネットアカウント → Google → カレンダーON
- **iCloudカレンダー**: しばらく両表示で確認 → 漏れ無しを確認後、表示を OFF（削除ではなくOFFが安全）

### 移行時の注意（セッション中に伝える）
- 取り込みは **一度きり**（再同期はされない）
- 移行日以降は **Googleに直接書き込む運用**に切替（iCloud側に追加しないと決める）
- **ゲスト情報・会議URL は引き継がれない**（自分の予定本体は問題なし）
- 念のため **当日朝に最終 `.icbu` 一括バックアップ**を取っておくと完全保険（Mac内で復元可能）

### サードパーティ一括エクスポート（参考、原則不要）
- CopyTrans Contacts / TouchCopy 等で複数iCloudカレンダーを一括 `.ics` 化可能
- PONさんのカレンダー数が3〜5個程度なら手動の方が早く確実

---

## 3. v2 ドラフトへの反映ポイント（要 outline / content_draft 修正）

| 該当箇所 | 修正内容 |
|---|---|
| Part「Cursor で AI を自動実行」| **Cursor Automations の説明を本筋に追加**。Auto-Run / BA / Automations の3層提示。「定期実行ニーズ」が出たら代替 (Claude Desktop / ChatGPT Tasks) に逃がす分岐を台本化 |
| Part「Google Calendar 連携」| **「PONさんは完全移行運用」を前提に確定**。並行運用パートは縮小、移行ハンズオンを厚く。一括 .icbu の罠（Google取り込み不可）を必ず明示 |
| 補足資料 E（Google OAuth）| 変更なし、ただし冒頭に「移行前提の運用フロー」サマリ追加 |
| 想定 Q&A | 「全部 .icbu でまとめて Google に入れたい」→「.icbu は Google 不可、`.ics` 個別が必要」を追加 |
| 安全運用ルール | iCloud OFF は削除でなく「表示OFF」で復元保険を残す、を明記 |

---

## 4. PONさん向け即答カード（本番セッションで紙/画面に出す想定）

```
■ 自動実行エージェント
  → Cursor では「Cursor Automations」（cron + クラウドAI）
  → ただし開発向け。日常プロンプトの定期化なら
     「Claude Desktop Scheduled Tasks」「ChatGPT Tasks」が最短

■ iCloud → Google Calendar 移行
  STEP1: Mac カレンダー.app → カレンダーごとに「ファイル → 書き出す」(.ics)
  STEP2: calendar.google.com → 設定 → インポート → .ics をアップ
  STEP3: iPhone/Mac で Google アカウント追加 → 既定カレンダーに設定
  STEP4: iCloud は削除せず「表示OFF」で保険
  注意 :「カレンダーアーカイブ (.icbu)」は Google 取り込み不可。
       必ず .ics で個別書き出し。
```

---

## 5. 田中さん次アクション

1. v2 outline / content draft の **Part 1（Cursor自動実行）と Part 4（Google Calendar）を本メモ通り改訂**
2. PONさんの「カレンダー数」を当日確認（3〜5個ならハンズオンで全件移行可、それ以上なら2回に分けるか持ち帰り）
3. Cursor Automations は **概念紹介に留める**判断（PONさんがGitHubリポ作業に進む時点で再導入）

---

## 出典

- [Cursor – Background Agents (公式)](https://docs.cursor.com/en/background-agent)
- [Cursor Automations (公式 docs)](https://cursor.com/docs/cloud-agent/automations)
- [Build agents that run automatically · Cursor Blog](https://cursor.com/blog/automations)
- [Cursor 3 Introduces Agent-First Interface (InfoQ, 2026/04)](https://www.infoq.com/news/2026/04/cursor-3-agent-first-interface/)
- [Claude CodeのloopとClaude DesktopとCursor Automationsの違い (DevelopersIO)](https://dev.classmethod.jp/articles/claude-code-loop-instructions/)
- [Import or export calendars on Mac - Apple Support](https://support.apple.com/guide/calendar/import-or-export-calendars-icl1023/mac)
- [Import events to Google Calendar - Google Calendar Help](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop)
- [iCloudからPCにカレンダーをエクスポートする方法 (CopyTrans)](https://www.copytrans.jp/support/icloud%E3%81%8B%E3%82%89pc%E3%81%AB%E3%82%AB%E3%83%AC%E3%83%B3%E3%83%80%E3%83%BC%E3%82%92%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%9D%E3%83%BC%E3%83%88%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95/)
