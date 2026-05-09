# シェアハウス・ビリヤードランキング MVP 実装メモ

**Date**: 2026-05-09
**実装場所**: `~/Javascript/sharehouse-billiards`
**Build**: ✅ Next.js 16.2.6 / 11 routes / TypeScript pass

## ファイル構成

```
sharehouse-billiards/
├── package.json (Next 16.2.6 + Mongoose + glicko2 + recharts)
├── docker-compose.yml (MongoDB 7)
├── .env.example
├── README.md
├── src/
│   ├── lib/
│   │   ├── mongodb.ts        Mongoose 接続キャッシュ
│   │   ├── glicko.ts         Glicko-2 計算 + ハンデ50%緩和 + Soft Reset
│   │   ├── fargo.ts          FargoRate アンカー換算
│   │   ├── handicap.ts       ハンデ自動提案 + サマリ
│   │   ├── line.ts           LINE Messaging API push
│   │   ├── auth.ts           管理者 Basic Auth
│   │   ├── season.ts         シーズン補助
│   │   └── models/
│   │       ├── Player.ts
│   │       ├── Season.ts
│   │       └── Match.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   ├── page.tsx                      ランキング
│   │   ├── match/page.tsx                試合履歴
│   │   ├── match/new/page.tsx            試合登録
│   │   ├── player/[id]/page.tsx          プレイヤー詳細 (グラフ + 履歴)
│   │   ├── admin/page.tsx
│   │   ├── admin/players/page.tsx        プレイヤー管理
│   │   ├── admin/seasons/page.tsx        シーズン管理
│   │   └── api/
│   │       ├── ranking/route.ts
│   │       ├── players/route.ts
│   │       ├── players/[id]/route.ts
│   │       ├── matches/route.ts
│   │       ├── seasons/route.ts
│   │       └── handicap-suggest/route.ts
│   └── components/
│       └── RatingChart.tsx (recharts)
```

## 起動手順

```bash
cd ~/Javascript/sharehouse-billiards
cp .env.example .env  # ADMIN_USER/ADMIN_PASS、必要なら LINE_* を編集
docker compose up -d  # ローカル MongoDB
npm run dev           # http://localhost:3000
```

## 動作確認チェックリスト

- [ ] `/admin/players` で管理者認証 + アンカープレイヤー登録
- [ ] 残りプレイヤー登録 (初期レート見立て)
- [ ] `/match/new` で試合登録 (ハンデ自動提案が出ることを確認)
- [ ] `/` でランキング更新確認
- [ ] `/player/:id` でレート推移グラフ確認
- [ ] LINE 通知確認 (オプション)
- [ ] `/admin/seasons` で新シーズン開始 → Soft Reset 動作確認

## 仕様書との対応

| 仕様書 | 実装 |
|---|---|
| Glicko-2 (τ=0.5, 初期 R=1500/RD=350/σ=0.06) | `lib/glicko.ts` |
| **DAMPING_FACTOR=0.5 (全試合に適用)** | `lib/glicko.ts` `computeMatch` で blend |
| **HANDICAP_FACTOR=0.5 (ハンデ試合の追加圧縮)** | `lib/glicko.ts` 同上 |
| シーズン Soft Reset (R 30%引戻し / RD≥200) | `softReset` + `/api/seasons` POST |
| FargoRate アンカー換算 (K=0.5) | `lib/fargo.ts` |
| **ハンデ自動提案 (100 diff = 3 freeball アンカー)** | `lib/handicap.ts` + `/api/handicap-suggest` |
| LINE Messaging API push | `lib/line.ts` |
| 真剣勝負のみ記録 | 試合登録 = 全件ランキング戦 |
| 全種目統合レート | gameType フィールドのみ記録、計算には不使用 |
| 初期レート恣意設定 | `/admin/players` フォーム |
| 20人以内スケール | データモデル/UIともに小規模前提 |

## 改訂履歴

### v0.3 (2026-05-09 追加)

**称号システム実装** (仕様書 §7):
- 保持型 4種 (球聖 / 中ボス / ネイバーズカップ / ワールドカップ) — 防衛戦型ロジック
- 算出型 4種 (新人王 / 週刊王 / 戦闘強 / 連勝王) — 試合登録時に DB から再計算
- ワールドネイバーズ (ワールドカップ + ネイバーズカップ 2冠) 達成時のフルスクリーン金色演出
- LINE 通知に称号変動セクション追加 (奪取/獲得/卒業/失効)
- ホーム上部に「現在の盟主」セクション (8称号カード)
- ランキング行のプレイヤー名横に称号バッジ
- プレイヤー詳細に保有称号セクション
- Prisma に Title / TitleHistory モデル追加 + Player にリレーション
- `lib/titles.ts`: TITLE_CONFIGS / updateTitlesAfterMatch / recomputeComputedTitles / getAllTitleHolders / getTitleMapByPlayer

**LINE 連携完成**:
- Channel ID `2010023773` / シュートくん bot で稼働
- `LineGroup` テーブルで group/user/room を webhook 経由で自動登録
- friend add → group invite で何もせず通知対象が DB に追加される

### v0.2 (2026-05-09)

**インフラ**:
- DB: MongoDB → **Postgres (Neon)** に移行
- ORM: Mongoose → **Prisma**
- 本番デプロイ: **https://sharehouse-billiards.vercel.app** (個人 Vercel アカウント)
- `docker-compose.yml` 削除 (Neon に直接接続)

**アプリ**:
- タイトル「Share House Billiards」→ **「WNG Ranking」**
- UI 全面モバイルファースト化 (タッチターゲット 44px+, 縦並びカード, FAB)
- 試合登録 UX 刷新: per-player 勝利ボタン、ハンデは強者選択 + フリーボール回数のみ
- 試合登録後にレート変動 (before → after, 差分) を表示
- 「もう一試合」時にプレイヤー一覧を再取得して最新レート反映
- `_id` → `id` バグ修正 (Prisma 移行漏れ)

**レーティング校正**:
- **DAMPING_FACTOR=0.5 を導入** (全試合の変動量を 50% に圧縮)
- **ハンデ提案テーブル再校正**: 100 diff = 3 フリーボール アンカー、+100 diff ごと +1
- 詳細は仕様書 §5.4 / §6.4 / §6.5 参照

## 残課題 (Phase 1.5 / Phase 2 へ送り)

- LINE グループID 取得用の webhook ルート
- 「ランキング戦中」ステータス装飾
- ハンデ補正テーブル (案B 移行)
- LINE Login 認証
- ラック単位記録
- バックアップスクリプト (cron)
