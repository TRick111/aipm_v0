# sources/ — 生データ・bulk import

## ここに置くもの
API ダンプ・CSV 取込・周期スナップショット

## ここに置かないもの
primary subject が明確なら該当 dir に

## ファイル命名
`<slug>.md`（小文字、ASCII or 日本語、空白はハイフン）

## 必須 frontmatter
`slug` / `type` / `created_at` / `updated_at`（その他 type 固有フィールドは schema.md 参照）

## See Also
- `../RESOLVER.md` — 全体の決定木
- `../schema.md` — ページ構造とテンプレート
