# published/ — 公開済 Snapshot 凍結領域（案F 固有）

外部に渡した・公開した固定版を保存する immutable な領域。

## ここに置くもの
- 顧客に提出した提案書
- ステークホルダーに送ったレポート
- 公開発表の資料
- 契約・覚書のスナップショット
- ある時点の「絶対に変えてはいけない版」

## ここに置かないもの
- 編集中のドラフト → writing/
- 内部メモ → personal/ または writing/
- 公開予定だが未公開のもの → writing/ で待機

## ルール

1. **immutable** — 一度書いたら rewrite しない。Brain の auto-update 対象外
2. ファイル名: `<YYYY-MM-DD>-<slug>-<version>.md`（例: `2026-04-30-jbeauty-proposal-v1.md`）
3. 各ファイルに `<filename>.lock` メタ情報（YAML）
4. 編集中の最新版は writing/<slug>.md を参照
5. version を上げる時は新しいファイルを作る（旧版は残す）

## .lock ファイルの形式

```yaml
# 例: 2026-04-30-jbeauty-proposal-v1.lock
slug: 2026-04-30-jbeauty-proposal-v1
type: published
recipient: companies/jbeauty
source_writing: writing/jbeauty-proposal
version: v1
published_at: 2026-04-30T10:00:00+09:00
sha256: <content hash>
notes: 飯武さん経由で先方に送付
```

## ワークフロー（snapshot freeze）

```bash
# 1. writing/ でドラフト作成・編集
# 2. 公開準備が整ったら snapshot を取る
gbrain publish-snapshot writing/jbeauty-proposal.md \
  --to published/2026-04-30-jbeauty-proposal-v1.md \
  --recipient companies/jbeauty \
  --version v1
# → published/ に固定コピー、.lock を生成
# → writing/ のドラフトは継続編集可
```
