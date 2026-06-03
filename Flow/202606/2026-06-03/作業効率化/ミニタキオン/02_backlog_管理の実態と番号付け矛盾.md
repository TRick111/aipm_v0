# バックログ管理の実態と番号付けの不整合

> 田中さんの悩み「バックログ番号の振りに一貫性がない」「新規 BL 追加を UI からできない」への直接回答。  
> BL-0095 調査メモ Part 2。

---

## TL;DR

**田中さんの直感は正しい。実装にバグ寄りの設計問題が 2 つある:**

1. **BL ID は per-project 採番で、global ユニークではない**  
   → 11 個のプロジェクトに `BL-0001.yaml` が存在し、index-store の Map で **silently 上書きされている**。
2. **UI から新規 BL を作る導線が存在しない**  
   → API (`POST /api/bl`) は実装済みだが、UI に form / button が無い。だから cockpit / CLI 経由が事実上の唯一の手段になっている。

---

## 1. ドキュメントの仕様

`~/mini-tachyon/docs/CLI.md`:

```bash
mt bl create --title <T> --project <P> --category <C>
# id 省略時は自動採番 BL-XXXX
```

`~/mini-tachyon/docs/API.md`:

```
POST /api/bl
"id": "BL-0017",          // 省略時は自動採番 (BL-XXXX 形式)
```

→ ドキュメントは「BL-XXXX 形式で自動採番」とだけ書いてある。**スコープ (per-project? global?) について明記なし**。

---

## 2. 実装の実態

`~/mini-tachyon/lib/api/bl-paths.ts:50-65`:

```ts
// scan project backlog dir to find an unused numeric id
export async function nextNumericBLId(category: string, project: string): Promise<string> {
  const dir = projectBacklogDir(category, project);  // ← Stock/<category>/<project>/backlog/
  let names: string[] = [];
  try { names = await fs.readdir(dir); } catch { /* dir may not exist yet */ }
  let max = 0;
  for (const n of names) {
    const m = n.match(/^BL-(\d+)\.yaml$/);
    if (m) {
      const num = parseInt(m[1], 10);
      if (num > max) max = num;
    }
  }
  return `BL-${String(max + 1).padStart(4, "0")}`;
}
```

**→ scan するのは指定 project の dir だけ**。他のプロジェクトの BL や中央 Backlog.md は見ない。

結果として:
- 同じ category/project に複数回 create したとき (例: ミニタキオン Stock 配下) → BL-0001, BL-0002, BL-0003... と incrementally 採番される
- でも `BL-0095` のように見える ID は **どこで採番されているか不明** (実は 中央 Backlog.md の最大値を見て田中さん or cockpit エージェントが手動指定している)

### 実態の検証 (今のリポジトリ)

```bash
$ find ~/aipm_v0/Stock -name "BL-0001.yaml" | wc -l
11
```

`BL-0001.yaml` が **11 個** あり、それぞれが別プロジェクト:

```
0.Other/ユニゾンさん, 0.Other/広告クライアント相談, 0.Other/CoreDriven, 0.Other/鈴木さん案件
生活管理/シェアハウス・ビリヤードランキング
RestaurantAILab/AI-Core, RestaurantAILab/麻布しき, RestaurantAILab/週報, RestaurantAILab/BFA
作業効率化/インプット形式管理, 作業効率化/ミニタキオン
```

**中央 Backlog.md には BL-0001 は 1 行だけ** (`ダッシュボード改` の "売上ダッシュボードの客単価の計算方法の見直し")。

つまり 中央 Backlog.md の BL-0001 は ダッシュボード改 のものを指しているが、Stock には ダッシュボード改/backlog/BL-0001.yaml は **存在しない**。これは「中央 Backlog.md が canonical だった旧運用」の遺骨で、Stock 配下の BL-0001 たちは **各プロジェクトで独自に 1 始まりで追加された** ものと判明。

### index-store はこれをどう扱っているか

`~/mini-tachyon/lib/stock.ts:90-100`:

```ts
const bls = new Map<string, BL>();  // ← bl.id をキーに global Map
for (const sp of stockProjs) {
  const blList = await readStockBLs(sp);
  for (const bl of blList) {
    bls.set(bl.id, bl);   // ← 同じ id があれば silently 上書き
  }
}
```

**→ Map の key は `bl.id` 単体。11 個ある BL-0001 のうち 10 個は読み込み順で silently 消えている**。「複数の BL-0001 が見える」 vs 「一個しか出ない」 — 状況次第で挙動が変わる。

さらに `mergeCentralBLs()` は `idCollisions++` で counter を回しているだけで、ログ以外には残らない:

```ts
if (bls.has(bl.id)) {
  idCollisions++;   // ← counter だけ
  continue;
}
```

中央 Backlog.md と Stock の id 衝突は per-project Stock を優先するが、Stock 内の衝突は無音で発生。

---

## 3. 「BL-TBD-XXX」と「BL-XXXX」の二系統

ミニタキオン project には:
- `BL-TBD-001` 〜 `BL-TBD-012` (12 個、レガシー id)
- `BL-0001`, `BL-0002`, `BL-0095` (3 個、新フォーマット)

の 2 系統が混在。`today-selected.ts:14-26` を見ると:

```ts
export const BL_ID_REGEX_SRC = "BL-(?:TBD-\\d+|\\d+)";

// (c) ミニタキオン own BL (BL-TBD-XXX) で active state なら常時可視
export function isMiniTachyonOwnBLActive(bl: BL): boolean {
  if (!/^BL-TBD-\d+$/.test(bl.id)) return false;  // ← TBD- だけ特別扱い
  return bl.state === "in_progress" || bl.state === "awaiting_user";
}
```

→ **`BL-TBD-` という prefix を「ミニタキオン自身の dogfood BL」のマーカーとして special-case している**。ミニタキオン以外の人が見たら謎の特別扱い。  
→ 一方で ミニタキオンの新規 BL (例: BL-0095) は TBD- 形式ではないので、この special-case には乗らない (= 朝のタスク案に [x] するか今日 decisions を append しないと「今日の選択」に出ない)。**鳥肌**

---

## 4. UI から新規 BL を作れない問題

`/api/bl` POST は実装済 (`lib/api/bl-write.ts:25-90`)。  
だが UI 側で POST を呼ぶ form / button を grep しても **ゼロ件**:

```bash
$ grep -rn "POST\|fetch.*api/bl" app/page.tsx app/bl/ app/projects/ components/
# (該当なし)
```

→ 田中さんの認識「ミニタキオン上から新規 BL を作れない」は **実装的に正しい**。

現状の代替手段:
- 田中さんが iPhone で cockpit から「BL-XXX 作って」と話しかけ → エージェントが `mt bl create` を呼ぶ
- 田中さんが Mac で `mt bl create` を直接叩く
- 朝のタスク案で AI が新規 BL 候補を出し、田中さんが「採択 → spawn」したときに finalize 経由で create (これは ID を AI が提案する方式なので衝突しがち)

cockpit 経由は **採番タイミングが不安定**:
- AI が「BL-0094 がない、次は BL-0095 ですね」と中央 Backlog.md を見て採番 → BL-0095 を `mt bl create --id BL-0095` で渡す
- でも同時に別 project で API が `nextNumericBLId('作業効率化', 'ミニタキオン')` を叩くと BL-0003 (= ミニタキオン dir の最大 + 1) が返ってくる
- → **同じ「次の BL は何番か」の質問に 2 通りの答え**

これが「番号の振りに一貫性がない」感覚の正体。

---

## 5. 矛盾の構造化

| 矛盾 | 旧運用の前提 | 新運用の前提 | 現状 |
|---|---|---|---|
| **中央 Backlog.md** | global 採番表 | per-project YAML が canonical | Backlog.md と per-project YAML が **二重管理**。中央には古い ID しかなく、新規は per-project に勝手に追加されている |
| **BL ID スコープ** | global ユニーク | (明示なし、per-project でも globalでも) | 実装は per-project、UI / Index は global ユニーク前提で Map に詰める → silent 衝突 |
| **新規 BL 入口** | 田中さんが手で Backlog.md に行追加 | `mt bl create` (CLI / MCP) | UI form 無し → cockpit / 手書き多発 |

---

## 6. 改善案 (中→大)

### A. 中央 Backlog.md を canonical な ID 採番表に戻す (小修正、推奨)

- `nextNumericBLId` を変更: project dir + 中央 Backlog.md + Stock 全体スキャンの **max + 1** を返す
- 既存 BL の ID は触らない (renumber すると ref 切れまくる)
- 効果: 新規 create は global ユニーク。既存重複は残るが今後増えない。

### B. UI に「新規 BL」ボタンを足す (中、推奨)

- ホーム or projects 一覧に「+ 新規 BL」モーダル
- title / project / category / priority / description を入力
- POST /api/bl で create → chokidar が反映
- BL-TBD-007 (Phase 3d UI 拡張) に統合可能

### C. BL-TBD-XXX の special-case を廃止 (中、推奨)

- `isMiniTachyonOwnBLActive` の special-case を消し、「ミニタキオン project の active BL は今日の選択に出す」の汎用ルール (own-project rule) に置き換え
- もしくは「常時可視 BL」を user が flag で指定する仕組み (例: BL の `pin_today: true`)

### D. 既存重複 BL-0001 を rename (大、要相談)

- 11 個の BL-0001.yaml を BL-0XXX (global ユニーク) に renumber
- deliverables.yaml の bl_id 参照、中央 Backlog.md の ID も同時に書き換え
- スクリプト化は可能だが ref 切れリスクあり、要田中さん判断

---

## 続き

- 01: 俯瞰 → `01_overview_実装とドキュメントの対応.md`
- 03: AIOS 連携 / 別リポ → `03_aios連携_別リポ_スキル.md`
- 04: 4 つの悩みへの回答 → `04_田中さんの悩みへの回答と推奨アクション.md`
