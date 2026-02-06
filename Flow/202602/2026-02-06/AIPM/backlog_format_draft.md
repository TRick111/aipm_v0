# Backlog（フォーマット案 / Draft）

目的: 自分が実施するタスクを **横断管理**し、**優先度・期日・所属（Program/Project）** を一覧で把握する。

要件:
- Markdownで見たときに **パッと見で分かる**（表で一覧）
- 「今日やるタスク抽出」等を **プログラムで処理できる**（規則的にパース可能）

## 提案する形式（結論）
**バックログの単一の正（Single Source of Truth）を “Markdown表” にする**のが一番運用が軽いです。
- **見やすさ**: 表はそのまま読める
- **機械処理**: 表を行単位で読み取り、`due` や `priority` でフィルタ/ソートできる
- **運用**: 1ファイルで完結（「YAML + 表の二重管理」にならない）

### フォーマットのルール（パース可能にするため）
- **列は固定**（ヘッダ名・順序を変更しない）
- **日付は `YYYY-MM-DD`**（空欄OK）
- **Priorityは `P0/P1/P2/P3`**（P0が最優先）
- **Statusは `todo/doing/blocked/done`**
- 1セル内で `|` は使わない（Markdown表が崩れてパースできなくなるため）
- `Tags` は `tag1,tag2` のカンマ区切り（空欄OK）

## バックログ（Draft）

| ID | Status | Priority | Due | Title | Program | Project | Tags | Notes |
|----|--------|----------|-----|-------|---------|---------|------|-------|
| BL-0001 | todo | P1 | 2026-02-06 | （例）バックログの最終配置先を決めてStockへ確定反映 | AIPM | 作業効率化 | aios,ops | まずFlowで運用し、固まったらFinalize |
| BL-0002 | todo | P2 |  | （例）週次でバックログを棚卸しする（15分） | AIPM | 定型作業 | routine | 毎週月曜AMなど |

## 取得（プログラム処理）のイメージ
同一フォルダの `backlog_tools.py` を使う想定（標準ライブラリのみ）。

例:
- 全件をJSONで出力: `python backlog_tools.py list --format json`
- 今日（または指定日）にやる候補を出力: `python backlog_tools.py today --date 2026-02-06`
- 期限超過を出力: `python backlog_tools.py overdue`

## 将来（Cursorルール化）したいこと
- バックログの置き場所（Stock内のパス）を固定する
- `backlog_tools.py` のコマンド仕様を固定する
- 「今日のFlowタスク作成（`mmdd_daily_tasks.md`）」時に
  - `today/overdue/next7days` を自動抽出して候補提示
  - ユーザーが取捨選択→`mmdd_daily_tasks.md` に反映

