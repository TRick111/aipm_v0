# AIOS Stock パッケージ（PONさん納品用）

PONさんの ChatGPT 過去会話を、AIOS Stock 規約に沿って **4 Program × 1 Project (過去会話履歴)** で整理した納品物です。

## 統計

| Program | 個別サマリー | artifacts |
|---|---:|---:|
| 美容室 | 141 | 230 |
| 美容専門店 | 40 | 62 |
| 自社ブランド | 20 | 65 |
| J-Beauty | 25 | 82 |
| **合計** | **226** | **439** |

## ディレクトリ構造

```
aios_stock_packages/                  ← この納品物の最上位
├── README.md                          ← このファイル
├── MasterIndex_snippet.yaml           ← PONさん側 Stock/MasterIndex.yaml への追記分
├── 美容室/                            ← Program
│   ├── README.md                       (Program README サンプル)
│   └── 過去会話履歴/                  ← Project（これを Stock/美容室/ にコピー）
│       ├── README.md
│       ├── ProjectIndex.yaml
│       ├── log.md
│       ├── _overview/                 ← Program別ローカルナレッジ
│       ├── {date}_xxx.md            (141件)
│       └── artifacts/                 (230件)
├── 美容専門店/
├── 自社ブランド/
└── J-Beauty/
```

## PONさん側でのセットアップ（3ステップ）

### Step 1: Project単位でコピー

各 Program 配下の `過去会話履歴/` ディレクトリをそのまま、PONさん側 Stock の該当 Program に配置します。

```bash
# PONさんのAIOSリポジトリのルートで実行
cp -r 美容室/過去会話履歴      ~/path/to/your-aios/Stock/美容室/
cp -r 美容専門店/過去会話履歴  ~/path/to/your-aios/Stock/美容専門店/
cp -r 自社ブランド/過去会話履歴 ~/path/to/your-aios/Stock/自社ブランド/
cp -r J-Beauty/過去会話履歴    ~/path/to/your-aios/Stock/J-Beauty/
```

PONさん側に **Program ディレクトリが存在しない**場合は、先に Program 直下に README.md を作成してください（本パッケージの `{Program}/README.md` がサンプルです）。

### Step 2: MasterIndex.yaml に追記

`MasterIndex_snippet.yaml` の内容を、自分の `Stock/MasterIndex.yaml` の対応する Program エントリに追記してください。具体的には、各 Program の `projects:` セクションに `過去会話履歴:` を追加します。

### Step 3: Cursorで使う

新しいチャットを開き、冒頭で以下のように参照します：

> 「Stock/美容室/過去会話履歴/_overview/01_PON_persona.md を読んで、私が誰か理解してください。
> その上で、ラピラピのワタルさん向け給与体系の核心を、過去の整理を踏まえて教えてください。」

AI は `Stock/美容室/過去会話履歴/2026-03-19_美容室再建の給与設計_*.md` を参照し、`artifacts/` 内の最終オファー文まで辿れます。

## AIOS規約への準拠

- ✅ `Stock/<Program>/<Project>/` 階層
- ✅ Program 直下: `README.md`
- ✅ Project 直下: `README.md` / `ProjectIndex.yaml` / `log.md`
- ✅ `ProjectIndex.yaml` に全ファイルを `files` 列挙
- ✅ `MasterIndex_snippet.yaml` で PON 側へマージ可能

## 注意

- スタッフ氏名・給与額・取引先など機微情報を含みます。**privateリポジトリで運用してください**。
- 旧版 `pon-chatgpt-knowledge` (2026-04-22 / `Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/`) と並存可能です。本パッケージはより詳細なサマリー粒度を提供します。
