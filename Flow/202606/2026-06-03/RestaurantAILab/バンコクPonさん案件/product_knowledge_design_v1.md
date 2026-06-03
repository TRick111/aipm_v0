# 商品知識データ設計 v1 — Voice Beauty Advisor (Mia) 連携検証

- **BL**: BL-0044 PONさん案件: 商品知識データの作成と連携検証
- **親 BL**: BL-0041 バーチャル美容アドバイザー POC
- **隣接 BL**: BL-0042 (タイ語テキスト)、BL-0043 (タイ語 STT/TTS)、BL-0045 (実写アバター)、BL-0070 (JBeauty デジタルサイネージ要件)、BL-0072 (実プロダクト連携)
- **対象実装**: `~/RestaurantAILab/voice-beauty-advisor` (Next.js + OpenAI Realtime API)
- **作成日**: 2026-06-03

---

## 1. 目的とスコープ

### 1.1 目的
実データに近い形で商品知識を作成し、バーチャル美容アドバイザー Mia が **catalog から正しく取得し、推薦応答 (recommend_product tool 経由) に反映できる** ことを検証する。

### 1.2 今日のスコープ (朝のタスク案より)
> サンプル商品データを 5 件作成 → アドバイザーで取得検証

具体化:
1. **データスキーマ** を v1 で確定 (現状の `ALL_PRODUCTS` 構造の上位互換)
2. **サンプル商品 8 件** を `product_catalog_v1_sample.json` に書き出し (5 件目標 +α、肌タイプ/悩みを網羅)
3. **連携アーキテクチャ 3 段階** を提示 (段階 1 のみ今日着手、2/3 は別 BL/フェーズ)
4. **連携検証手順 3 シナリオ** を明文化 (実行は次フェーズ)
5. **開いた論点 3 件** を BL の pending_questions に書き戻し (実装方針確定のため)

### 1.3 スコープ外 (別 BL/別フェーズで扱う)
- 100-200 件への拡張 (BL-0070 / BL-0072 連動)
- ベクトル検索 / RAG 実装 (段階 3)
- 実 PON さん店舗の販売商品データ取得 (PON さん側情報依存)
- JBeauty 用途の日本コスメ大手 (花王 / 資生堂 / コーセー) 商品データ
- 画像生成 (現状は placeholder image path のみ)

---

## 2. 現状アーキテクチャ (Mia)

### 2.1 商品データの所在

`~/RestaurantAILab/voice-beauty-advisor/src/config/mia-prompt.ts`:

```ts
// (1) システムプロンプト内に 3 件文字列で埋め込み
export const MIA_SYSTEM_PROMPT = `
...
## 知っている製品
1. ルミナスモイスチャークリーム - 保湿クリーム、乾燥肌向け、セラミド配合、48時間保湿持続、¥4,800
2. クリアブルームセラム - 美容液、毛穴ケア・くすみ対策、ビタミンC誘導体配合、¥5,500
3. シルキーUVヴェール - 日焼け止め、SPF50+/PA++++、敏感肌対応、化粧下地兼用、¥3,200
...`;

// (2) UI 全件表示用 (3 件)
export const ALL_PRODUCTS = [
  { product_name, product_type, price, description, image }, ...
];

// (3) Realtime API ツール定義
export const RECOMMEND_PRODUCT_TOOL = {
  type: "function",
  name: "recommend_product",
  parameters: { product_name, product_type, price, reason }
};
```

### 2.2 連携フロー

1. ブラウザ → `/ws/realtime` (WebSocket) → OpenAI Realtime API
2. `session.update` で `MIA_SYSTEM_PROMPT` と `RECOMMEND_PRODUCT_TOOL` を送る (`useRealtimeSession.ts:150-167`)
3. ユーザー音声 → STT (Whisper) → モデルが knowledge から推薦 → `recommend_product` function call
4. `response.function_call_arguments.done` でクライアントが受け取り → `setProducts((prev) => [...prev, args])` → `ProductPanel` 表示

### 2.3 ボトルネック

| # | 課題 | 影響 |
|---|------|------|
| B1 | 商品情報がシステムプロンプトに直書き | スケール不能 (100+ 件で context 圧迫、メンテ困難) |
| B2 | recommend_product tool が「画面表示」を返すだけ | モデルは "知っている前提" で値を生成 → ハルシネーション余地 |
| B3 | カタログ照会の tool がない | モデルは prompt 内 3 件以外を答える根拠なし |
| B4 | 肌タイプ / 悩みのタグが構造化されていない | "敏感肌向けで紫外線対策" のような複合条件で適合度を判定できない |

---

## 3. データスキーマ v1

### 3.1 設計判断
- 既存 `ALL_PRODUCTS` フィールドは **下位互換** (UI 表示用に必要)
- 検索キーを追加する: `id` / `tags` (悩み) / `suitable_skin_types` (肌タイプ) / `keywords`
- 多言語化を視野: `name_ja` / `name_th` / `name_en` (タイ語は BL-0042/0043 で品質確認後に正式投入)
- 在庫・販売状況フィールドは v1 では入れない (PON さん実商品との連携 = BL-0072 で議論)

### 3.2 v1 スキーマ (JSON Schema 風)

```jsonc
{
  "id": "vba-0001",                          // 一意 ID (vba- = voice beauty advisor)
  "name_ja": "ルミナスモイスチャークリーム",
  "name_en": "Luminous Moisture Cream",       // 任意 (Tavus 等多言語アバター用)
  "name_th": null,                            // BL-0042/0043 で確定後に追加
  "brand": "Lumière Studio",                  // 架空ブランド (PoC 用)
  "product_type": "保湿クリーム",              // UI バッジ表示・既存互換
  "category": "skincare",                     // skincare | suncare | makeup | haircare
  "price_jpy": 4800,                          // 数値で持つ (表示は ¥{n.toLocaleString()})
  "price_display": "¥4,800",                  // フォーマット済 (Realtime tool 引数互換)
  "volume": "50g",
  "suitable_skin_types": ["dry", "normal"],   // dry | oily | combination | sensitive | normal
  "tags": ["保湿", "セラミド", "乾燥対策", "夜用"],
  "key_ingredients": ["セラミド NP", "ヒアルロン酸", "シアバター"],
  "concerns": ["乾燥", "小じわ", "バリア機能"],  // 美容悩み (検索キー)
  "contraindications": [],                   // 禁忌 (敏感肌注意 等)
  "description_short": "乾燥肌向け・セラミド配合・48時間保湿持続",
  "description_long": "夜のスキンケアの締めに使う高保湿クリーム。3 種のセラミドが角層深部まで浸透し、翌朝までうるおいが続きます。デリケートな肌の方は使用前にパッチテストを推奨。",
  "usage": "洗顔・化粧水のあと、適量を顔全体になじませてください。",
  "image": "/images/products/moisture.png",
  "release_year": 2024,
  "active": true
}
```

### 3.3 ALL_PRODUCTS 互換マッピング

| 既存 (UI) | 新 (catalog) | 移行 |
|---|---|---|
| `product_name` | `name_ja` | rename or 両方持つ |
| `product_type` | `product_type` | そのまま |
| `price` | `price_display` | そのまま |
| `description` | `description_short` | そのまま |
| `image` | `image` | そのまま |

---

## 4. 連携アーキテクチャ 3 段階

### 4.1 Phase 1 (今日着手 → 明日 PR 想定): カタログ JSON + 静的 prompt 注入

```
catalog.json (8 件)
        │
        ▼
mia-prompt.ts ← buildSystemPrompt(catalog) でプロンプト動的生成
        │       (## 知っている製品 セクションを catalog から map)
        ▼
session.update.instructions
```

- **メリット**: 既存アーキ最小変更 / 即動く
- **デメリット**: 100 件超で context 肥大 (~2-3k トークン)、tool call は依然 hallucination 余地
- **検証可能事項**: 「prompt に書いた商品を Mia が正しく説明できるか」「8 件中 N 件にカバー要求して全部出るか」

### 4.2 Phase 2 (別 BL 推奨): 検索 tool 化 (lookup_product)

新 tool 追加:

```ts
export const LOOKUP_PRODUCT_TOOL = {
  type: "function",
  name: "lookup_product",
  description: "肌タイプ・悩み・キーワードから候補商品を検索する",
  parameters: {
    type: "object",
    properties: {
      skin_type: { type: "string", enum: ["dry","oily","combination","sensitive","normal"] },
      concerns: { type: "array", items: { type: "string" } },
      keyword: { type: "string" }
    }
  }
};
```

- システムプロンプトには商品一覧を書かず、ユーザーの悩みを掴んだら `lookup_product` で取得 → `recommend_product` で UI 反映
- カタログ 100-200 件まで context 圧迫なしでスケール

### 4.3 Phase 3 (BL-0072 / RAG 議論): ベクトル検索 / RAG

- 500+ 件 / マルチブランド / 長い説明文を抱える段階で必要
- pgvector or Pinecone or OpenAI vector store
- BL-0072 (実プロダクト連携) と合流予定

---

## 5. サンプルデータ 8 件 (catalog v1)

実体は `product_catalog_v1_sample.json`。網羅性方針:

| ID | 肌タイプ | 悩みカバー | 用途 |
|---|---|---|---|
| vba-0001 | dry, normal | 乾燥、小じわ | 保湿 (既存) |
| vba-0002 | combination, normal | 毛穴、くすみ | 美容液 (既存) |
| vba-0003 | sensitive, all | UV、敏感 | 日焼け止め (既存) |
| vba-0004 | oily, combination | 皮脂、ニキビ | 化粧水 (新規) |
| vba-0005 | sensitive | 赤み、バリア | 敏感肌専用クリーム (新規) |
| vba-0006 | all | クレンジング、メイク落とし | クレンジング (新規) |
| vba-0007 | dry, sensitive | 唇の乾燥 | リップケア (新規) |
| vba-0008 | all | 朝の時短、化粧下地 | BB クリーム (新規) |

---

## 6. 連携検証手順 (Phase 1 完了後に実施)

### 6.1 検証シナリオ A: prompt-only 取得確認
1. catalog v1 (8 件) を `mia-prompt.ts:buildSystemPrompt()` で動的注入
2. UI で会話開始 → 「最近肌が乾燥していて」と発話
3. **期待**: vba-0001 または vba-0005 のいずれかが `recommend_product` で呼ばれる
4. **NG ケース**: catalog 外の架空商品名が返る → ハルシネーション、Phase 2 が必要な兆候

### 6.2 検証シナリオ B: 複合条件
1. 「敏感肌で、紫外線対策がしたい」と発話
2. **期待**: vba-0003 (シルキーUVヴェール、sensitive 対応、SPF50+) が推薦される
3. tool 引数 `product_name` / `price` / `reason` が catalog 値と一致するか確認

### 6.3 検証シナリオ C: カタログ外要求
1. 「美白の薬用美容液はある?」と発話 (catalog に該当なし)
2. **期待**: 「申し訳ございませんが、その製品については詳しくないのですが」と prompt ルール通り返答
3. **NG**: 架空商品を捏造 → Phase 2 (lookup tool) を急ぐ理由になる

### 6.4 ログ取得
- ブラウザ Console: `response.function_call_arguments.done` の引数
- `useRealtimeSession.ts:316-355` 経由で `setProducts` に流れる値
- 検証用ログ追加箇所: `parseToolCallArgs` の直後に `console.info("[BL-0044]", args)`

### 6.5 合否基準
- A/B/C 各 3 試行、計 9 試行のうち 7/9 以上正答で Phase 1 合格 → Phase 2 (lookup_product tool) に進む

---

## 7. 実装手順 (Phase 1) — 次セッションで PR 化想定

```
1. mkdir -p src/data && mv product_catalog_v1_sample.json src/data/catalog.json
2. src/config/mia-prompt.ts を refactor:
   - import catalog from "@/data/catalog";
   - export function buildSystemPrompt(): string { ... map catalog into ## 知っている製品 ... }
   - ALL_PRODUCTS を catalog から派生 (filter active=true)
3. useRealtimeSession.ts:154 で instructions: buildSystemPrompt() に差し替え
4. ProductCard.tsx で image を catalog から引く (現状 name -> image hard map)
5. npm run dev で起動 → §6 検証シナリオ A/B/C を実行
```

---

## 8. 開いた論点 (BL.pending_questions に書き戻し)

### Q1: catalog の本体ロケーション
- (A) Mia の DEMO 用に架空商品セット (本提案、PoC 完結)
- (B) PON さん店舗の実販売商品 (本番投入前提、PON さん側ヒアリング要)
- (C) JBeauty 文脈で日本コスメ大手 (花王 / 資生堂 / コーセー) — BL-0070 が要求

→ 今日の v1 は (A) で作成。本番方針が (B) (C) に振れる場合、catalog スキーマは流用できるが商品リスト全置換が必要。

### Q2: Phase 2 (lookup_product tool) の優先度
- (a) Phase 1 で 7/9 合格 → Phase 2 を急がない (system prompt 拡張で 30-50 件まで耐える)
- (b) PON さん本番 / JBeauty 展示会が近い → Phase 2 を並走着手
- (c) BL-0072 (実プロダクト連携) と Phase 3 まで一気通貫で別 BL を切る

### Q3: catalog の格納先と版管理
- (a) `voice-beauty-advisor/src/data/catalog.json` (本提案、リポ内・型チェック容易)
- (b) `RestaurantAILab/共通商品 catalog/` の独立リポ (複数アプリ共有想定)
- (c) DB (Supabase / Vercel KV) (動的更新前提)

→ 今日は (a) を前提に PoC。スケール時に (b) か (c) に分離。

---

## 9. 次のアクション (本セッション完了後)

1. 本ドキュメントと `product_catalog_v1_sample.json` を deliverable として register
2. Q1 / Q2 / Q3 を BL の pending_questions に登録
3. 田中さん回答を待ち → Q1=(A) 確定なら Phase 1 実装 PR を別セッションで作成
4. BL state は in_progress 継続 (Phase 1 実装まで)
