# 「過去会話履歴」AIOSナレッジ — PONさん共有手順

- 作成日: 2026-06-05
- 担当: 田中利空 + Claude
- 関連 BL: BL-0087（PONさん新規プロジェクト立ち上げ）

---

## 0. 概要

PONさんの ChatGPT 過去会話履歴 (654件中 4カテゴリに該当する225件) を、**1会話 = 1サマリー**粒度で個別ナレッジ化したものを、PONさんの AIOS Stock に配置できる形でパッケージ化しました。

旧版 (2026-04-22 / `pon-chatgpt-knowledge` / サブカテゴリ単位の総体サマリー) と並存可能で、本パッケージは**個別会話単位の深い参照**を提供します。

### 統計

| Program | 個別サマリー | 関連 artifacts |
|---|---:|---:|
| 美容室 | 141 | 230 |
| 美容専門店 | 40 | 62 |
| 自社ブランド | 20 | 65 |
| J-Beauty | 25 | 82 |
| **合計** | **226** | **439** |

### 納品物の場所（田中さん側）

```
Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/output/aios_stock_packages/
├── README.md
├── MasterIndex_snippet.yaml
├── 美容室/
│   ├── README.md (Program README サンプル)
│   └── 過去会話履歴/   ← この Project ディレクトリを丸ごと納品
├── 美容専門店/
│   └── 過去会話履歴/
├── 自社ブランド/
│   └── 過去会話履歴/
└── J-Beauty/
    └── 過去会話履歴/
```

---

## 1. 共有方法の選択肢

| 方式 | 向いている状況 | 手間 |
|---|---|---|
| **A. 既存 private GitHub repo に追加 push** (`pon-chatgpt-knowledge` を v2 にアップグレード) | PONさんが既に旧版を git clone して運用している | 小 |
| **B. 新しい private GitHub repo を作成** (`pon-chatgpt-knowledge-v2` 等) | 旧版を残しつつ v2 を別 repo で並走させたい | 中 |
| **C. ZIP で直接渡す** (LINE / Google Drive) | git 運用していない、もしくは即渡したい | 小 |
| **D. 田中さん側からPONさん AIOS リポジトリに直接 PR** | PONさんの AIOS が GitHub にあって、田中さんに書込権がある | 中 |

**推奨: A**（旧 repo に v2 として追加 push）。理由：
- PONさんがすでにセットアップ済み
- 「git pull」で受け取れる
- 旧版と並存できる構造

---

## 2. 推奨ルート（A: 既存 private repo へ追加 push）

### Step 2-1. ローカルにクローン (既にあればスキップ)

```bash
cd ~/
gh repo clone <PONさん私的GitHubアカウント>/pon-chatgpt-knowledge
cd pon-chatgpt-knowledge
```

### Step 2-2. 新ブランチを切る

```bash
git checkout -b feat/v2-detailed-summaries
```

### Step 2-3. 納品物をコピー配置

```bash
SRC="/Users/rikutanaka/aipm_v0/Flow/202606/2026-06-05/RestaurantAILab/バンコクPonさん案件/output/aios_stock_packages"
# 4 Program 配下の「過去会話履歴」を repo ルートに配置
cp -r "$SRC/美容室"      ./
cp -r "$SRC/美容専門店"  ./
cp -r "$SRC/自社ブランド" ./
cp -r "$SRC/J-Beauty"    ./
# トップREADMEとMasterIndex_snippetもコピー
cp "$SRC/README.md" ./README_v2.md
cp "$SRC/MasterIndex_snippet.yaml" ./MasterIndex_snippet_v2.yaml
```

> 既存の README.md を上書きしないよう `README_v2.md` 名で配置。

### Step 2-4. コミット & push

```bash
git add 美容室 美容専門店 自社ブランド J-Beauty README_v2.md MasterIndex_snippet_v2.yaml
git commit -m "Add v2: 1会話=1サマリー粒度の個別ナレッジ (226件 + artifacts 439件)

旧 ChatGPT履歴/ (subcategory単位の総体サマリー) と並存。
4 Program × 1 Project (過去会話履歴) で AIOS規約準拠。"
git push origin feat/v2-detailed-summaries
```

### Step 2-5. PR or 直接 merge

```bash
# シンプルに main へ
git checkout main
git merge feat/v2-detailed-summaries
git push
```

---

## 3. PONさん側での受領手順（田中さんがPONさんに伝える内容）

### 3-1. リポジトリを更新

```bash
cd ~/path/to/pon-chatgpt-knowledge
git pull
```

### 3-2. AIOS Stock に配置

PONさんの AIOS Stock ディレクトリに **Project 単位で**コピーします。

```bash
AIOS=~/path/to/your-aios  # PONさんのAIOSルート
REPO=~/path/to/pon-chatgpt-knowledge

# 既存 Program がある場合はそこに過去会話履歴 Project を追加
cp -r "$REPO/美容室/過去会話履歴"      "$AIOS/Stock/美容室/"
cp -r "$REPO/美容専門店/過去会話履歴"  "$AIOS/Stock/美容専門店/"
cp -r "$REPO/自社ブランド/過去会話履歴" "$AIOS/Stock/自社ブランド/"
cp -r "$REPO/J-Beauty/過去会話履歴"    "$AIOS/Stock/J-Beauty/"
```

> PONさん側に該当 Program が存在しない場合は、先に Program ディレクトリと Program README を作成してください（`{Program}/README.md` がサンプルです）。

### 3-3. MasterIndex.yaml に追記

`MasterIndex_snippet_v2.yaml` の各 Program の `projects.過去会話履歴:` を、PONさんの `Stock/MasterIndex.yaml` の該当 Program の `projects:` セクションに追記します。

例（美容室の場合）:
```yaml
# Stock/MasterIndex.yaml
美容室:
  summary: ...
  keywords: [...]
  projects:
    # 既存のProject群...
    過去会話履歴:  # ← ここを追記
      summary: 美容室 に関する PONさんの ChatGPT 過去会話を、1会話=1サマリー粒度...
      keywords: [...]
      path: Stock/美容室/過去会話履歴
      readme: README.md
      index: ProjectIndex.yaml
```

### 3-4. Cursor で動作確認

新しいチャットを開き、冒頭で以下のように参照させます：

> 「`Stock/美容室/過去会話履歴/_overview/01_PON_persona.md` を読んで、私が誰か理解してください。
> その上で、ラピラピのワタルさん向け給与体系の核心を、過去の整理を踏まえて教えてください。」

→ AI が `Stock/美容室/過去会話履歴/2026-03-19_美容室再建の給与設計_*.md` を参照し、`artifacts/` 内の最終オファー文まで辿れます。

---

## 4. 動作確認用の質問（5問）

これらをAIに投げて、過去ナレッジを参照した具体的な回答が返ってくるかをチェックしてください。一般論で逃げる回答 = ナレッジ未参照。

### Q1（美容室 / Rapi-rabi）
> ラピラピの再建プロジェクトで、新店長候補のワタルさんに対して設計した給与体系の核（固定給・インセンティブ構成・KPI・試用期間の扱い）を、過去に整理した最終オファー文の内容を踏まえて説明してください。なぜその設計にしたのか、背景の判断軸も添えて。

期待参照: `美容室/過去会話履歴/2026-03-19_美容室再建の給与設計_69bbac77.md` + 関連 artifacts

### Q2（美容専門店 / ネイルサロン）
> ネイルサロンのギャル気質のスタッフに対する面談・声かけ設計で、過去にまとめた「トーク台本」と「刺さるフレーズ集」の方針は何ですか。そのスタッフの実績分析と立地戦略の判断軸はどう紐づいているか含めて教えてください。

期待参照: `美容専門店/過去会話履歴/2025-12-22_スタッフへの声かけ方法_6949082f.md` + artifacts

### Q3（自社ブランド / DOT）
> 自社ブランド DOT の毛髪ケア製品について、主要3成分（キア種子エキス / 加水分解ケラチン / アミノ酸）の役割と、パンフレットのビジュアルコンセプトの方向性を、過去に整理した内容に基づいて教えてください。

期待参照: `自社ブランド/過去会話履歴/2025-05-10_毛髪ケア製品説明_681effd1.md` + artifacts

### Q4（J-Beauty / アカデミー）
> 日本ビューティーをASEANに広げる「12ヶ月モデル事業」の予算取り設計で、施策枠として置いた5つの軸（SNS / クリエイター育成 / 現地展示会 / ブランド輸出支援 / ASEAN向け教育動画）それぞれの狙いを教えてください。2033年に置いている数値目標と、起用候補としているアンバサダー（三浦孝太を中心とした三刀流体制）の意図も。

期待参照: `J-Beauty/過去会話履歴/2025-11-22_日本ビューティー展開案_6921aecb.md` + artifacts

### Q5（横断 / 経営指標）
> 美容室の店販コミッション制度を最終的にどう設定したか（個人/店舗の比率）、理想とする人件費率、家族手当制度の枠組みなど、これまで決まった経営指標を、決定の背景と共に整理してください。

期待参照: `_overview/03_decisions_log.md` + 複数会話の横断（個人10% / 店舗1-3%、人件費率45-55%、家族手当 子供1人3,000-5,000バーツ等）

### 評価チェックリスト

| ✓ | 観点 |
|---|---|
| ☐ | 固有名詞が正確に出る（ワタルさん、ヌイ、キア種子エキス、三浦孝太など） |
| ☐ | 数値が正確（個人10% / 店舗1-3%、人件費率45-55%、2033年17兆円目標など） |
| ☐ | 決定に至った**背景・理由**まで触れる |
| ☐ | 関連 artifact ファイル名やパスを引用してくる |
| ☐ | 一般論で逃げていない（「一般的には〜」が多いと未参照） |

---

## 5. PONさんへ送るメッセージ案（田中さんからPonさんへ）

```
お疲れ様です！

過去のChatGPT会話をAIOSナレッジに統合する v2 を作りました。

【概要】
旧版 (ChatGPT履歴/) はサブカテゴリ単位の総体サマリーでしたが、今回は
1会話 = 1サマリー粒度で、過去225件の会話を個別にナレッジ化しています。
論点・結論・決定事項・関連artifactsへのリンク・原文重要引用まで含む形式です。

【ボリューム】
- 個別サマリー 226件 + 関連artifacts 439件
- 4 Program × 1 Project (過去会話履歴) のAIOS規約準拠構造

【受け取り方】
git pull で pon-chatgpt-knowledge リポジトリを更新してください。
README_v2.md にセットアップ手順（cp + MasterIndex追記）があります。

【使い方の例】
Cursorで「Stock/美容室/過去会話履歴/_overview/01_PON_persona.md を読んで、
ラピラピの〇〇について教えて」と聞くと、過去の整理を踏まえた回答が返ります。

動作確認用の質問5問もREADMEに添付しています。
おかしな挙動・粒度の違和感あればフィードバックお願いします！
```

---

## 6. トラブルシューティング

| 症状 | 対処 |
|---|---|
| Cursor が個別サマリーを参照しない | 会話冒頭で `_overview/01_PON_persona.md` を明示的に Read させる |
| 一般論回答が返る | 質問内に「過去の整理を踏まえて」「{固有名詞} について」を入れる |
| artifact のリンクが切れる | `_overview/06_conversations_index.md` から正しいパスを確認 |
| 旧版と新版で情報がズレる | 新版の決定事項を優先（旧版より粒度・新しさが高い） |
| 重複ファイル疑い | `2025-03-13_Lightroom_*` 等が226件中1件、片方は不要な可能性 |

---

## 7. 関連ドキュメント

- 本パッケージ README: `output/aios_stock_packages/README.md`
- 各 Project README: `output/aios_stock_packages/{Program}/過去会話履歴/README.md`
- AIOSルール: `~/aipm_v0/.cursor/rules/aios/00_aios_core.mdc`
- 旧版 README: `Stock/RestaurantAILab/バンコクPonさん案件/output_2026-04-22/pon-chatgpt-knowledge/README.md`
- BL-0087: `Flow/202605/2026-05-05/RestaurantAILab/バンコクPonさん案件/BL-0087_依頼整理と進め方案.md`
