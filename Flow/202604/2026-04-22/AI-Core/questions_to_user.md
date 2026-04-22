# BL-0061「AIコア PL作成」: ユーザーへの確認事項（Q-A〜Q-C）

- 作成日: 2026-04-22
- 状態: Q1〜Q3, Q7 は確定。Q4〜Q6 のうち、**実装計画確定後も並行確認できる項目だけ**残した
- 関連: `implementation_plan.md` v1.0
- **回答方法**: 各質問の「✍️ 回答記入欄」に直接書き込んでください

---

## ✅ 確定済み（参考）

| Q | 確定内容 |
|---|---|
| Q1 HTML | `~/Downloads/AI秘書事業_事例集_v1.html`（**町田第一さん**作成） |
| Q2 UI | HTML をそのまま土台にし、チェックボックス＋送信機能を後付け |
| Q3 デプロイ | Vercel: 既存ダッシュボードと同 team / DB: 新規 Neon プロジェクト / GitHub: `RestaurantAILab` org に新規リポ |
| Q7 期日 | 急ぎではない（実装は別タスクで起動） |

---

## Q-A. 価格 (`priceJpy` 列) の扱い [任意・回答なければデフォルト進行]

`prisma/schema.prisma` には `ServiceCase.priceJpy Int?` を**先に空で確保**しておく予定（後付けの破壊変更を避けるため）。

確認: 現時点で値を持たせたいか？

- (a) **null のまま運用、表示しない**（MVP 既定）
- (b) MVP の段階で 50事例ぶん仮単価を入れたい（その場合は単価表が必要）
- (c) 「基本プラン + オプション」二段表記にしたい（schema 拡張）

**AI推奨**: (a)。回答なければ (a) で進める。

### ✍️ 回答記入欄
> （a）

---

## Q-B. MVP の機能スコープ承認 [任意・回答なければデフォルト進行]

Phase 1 で実装する範囲を以下で確定したい。

| # | 機能 | MVP 含む？ |
|---|---|:---:|
| F1 | クライアント基本情報入力（社名/担当/連絡先/セグメント） | ✅ |
| F2 | 50 事例のチェックボックス選択（HTML 由来のカテゴリアコーディオン） | ✅ |
| F3 | フィルタ（role/tools/freq/difficulty/badge） | ✅（HTML 既存挙動の React 移植） |
| F4 | 送信 → DB 保存 + Slack 通知 | ✅ |
| F5 | 送信完了画面 + 共有 URL | ✅（最小） |
| F6 | Admin 画面（提出一覧） | ❌（Phase 2） |
| F7 | 提案書 PDF/Markdown 出力 | ❌（Phase 2） |
| F8 | 認証（Magic Link） | ❌（Phase 2） |

**AI推奨**: 上記のまま。回答なければそのまま進める。

### ✍️ 回答記入欄
> すみません。データベースはやっぱりNotionにしたいです。そうすることで、アドミン画面もほぼ不要になるかなと思っています。\n\nNotion上で事例の一覧の管理と、クライアントからの依頼の一覧を管理したいと思います。

---

## Q-C. AI-Core を aipm_v0 Stock に登録するか [方針確定・完了時に効く]

`aipm_v0/Stock/MasterIndex.yaml` に AI-Core が未登録。実装完了後の「Stock 反映」を AIOS ルールに沿って行うため、登録方針を決めたい。

- (a) aipm_v0 では **登録しない**（Markdowns-1 側を正とする。aipm_v0 は Flow とリンクメモのみ）
- (b-1) **RestaurantAILab program 配下のプロジェクトとして登録** = `Stock/RestaurantAILab/AI-Core/` ← 推奨（Daily Tasks 表記と一貫）
- (b-2) 独立 program として `Stock/AI-Core/` を新設（Markdowns-1 側のミラー）

**AI推奨**: (b-1)。ただし町田第一さん／町田大地さんが Markdowns-1 側を共同管理しているなら、ポインタ README だけ aipm_v0 に置く折衷案も検討可。

### ✍️ 回答記入欄
> RestaurantAILabの中にAI-Coreを追加したいです。PONさん案件のように各種ファイルの実態はMarkdown-1にあるけど、インデックスとしては保存してあるみたいな状態にしたいです。

---

## 補足：すでに Backlog 反映済み

`Stock/定型作業/バックログ/Backlog.md` BL-0061 Notes は更新済み（PL=Price List 明記、本日の探索完了、参照ファイルパス記載）。
