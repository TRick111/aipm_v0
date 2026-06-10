# _overview/ — Program横断ナレッジ

## このディレクトリについて

`ChatGPT履歴/` プログラム全体を俯瞰するためのファイル群です。
個別プロジェクト（美容室/美容専門店/自社ブランド/J-Beauty）を深掘りする前に、
まずここを読むとPONさんの全体像・思考傾向・過去の決定事項が把握できます。

## ファイル一覧と使い分け

| ファイル | 用途 | 最初に読むべきか |
|---|---|:---:|
| `01_PON_persona.md` | PONさんは誰・何をしている人か。AIの会話冒頭で参照する | ⭐ 必須 |
| `02_business_overview.md` | 美容室・美容専門店・自社ブランド・J-Beautyの全体俯瞰 | ⭐ 推奨 |
| `03_decisions_log.md` | 給与制度・コミッション率・人件費率など過去の決定事項（時系列） | テーマ依存 |
| `04_open_ideas.md` | 過去に話したが未実行のアイデア集 | ブレスト時 |
| `05_people_directory.md` | 登場人物（スタッフ・取引先・相談相手） | 名前が出たとき |
| `06_artifacts_index.md` | 成果物439件のカタログ | ファイル探したい時 |
| `themes/*.md` | テーマ別ナレッジ（給与・プロモ・商品・人事・競合・海外・経営指標） | 特定論点の深掘り |

## 典型的な会話パターン（Cursor + AIOS）

### パターンA: 既存テーマの続きを相談

例: 「給与制度の続きを相談したい」

1. AIに `01_PON_persona.md` と `themes/給与制度とスタッフマネジメント.md` を読ませる
2. さらに `03_decisions_log.md` で過去の決定を確認
3. 本題を相談

### パターンB: 新しい事業判断

例: 「新店舗をプノンペンに出したい」

1. `01_PON_persona.md` + `02_business_overview.md`
2. 近い事例として `美容室/ベトナム支店/README.md` + `themes/海外展開とJ-Beauty.md`
3. 本題

### パターンC: スタッフ個別の話

例: 「RISAさんに新しい役割を任せたい」

1. `05_people_directory.md` でRISAさんの登場文脈を確認
2. 該当する `conversations_summary.md` で過去のやり取りを参照
3. 本題

## 更新について

- `01_PON_persona.md` / `02_business_overview.md` / `03_decisions_log.md` / `04_open_ideas.md` / `themes/*.md` は Claude Sonnet / Opus で合成
- `05_people_directory.md` / `06_artifacts_index.md` は機械生成（再生成コスト低）
- 新しい会話を追加したい場合は田中さんまで
