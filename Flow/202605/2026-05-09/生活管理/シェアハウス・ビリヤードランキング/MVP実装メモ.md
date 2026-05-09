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
| ハンデ付き試合 50% 緩和 | `computeMatch` で blend |
| シーズン Soft Reset (R 30%引戻し / RD≥200) | `softReset` + `/api/seasons` POST |
| FargoRate アンカー換算 (K=0.5) | `lib/fargo.ts` |
| ハンデ自動提案 | `lib/handicap.ts` + `/api/handicap-suggest` |
| LINE Messaging API push | `lib/line.ts` |
| 真剣勝負のみ記録 | 試合登録 = 全件ランキング戦 |
| 全種目統合レート | gameType フィールドのみ記録、計算には不使用 |
| 初期レート恣意設定 | `/admin/players` フォーム |
| 20人以内スケール | データモデル/UIともに小規模前提 |

## 残課題 (Phase 1.5 / Phase 2 へ送り)

- LINE グループID 取得用の webhook ルート
- 「ランキング戦中」ステータス装飾
- ハンデ補正テーブル (案B 移行)
- LINE Login 認証
- ラック単位記録
- バックアップスクリプト (cron)
