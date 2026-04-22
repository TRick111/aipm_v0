#!/usr/bin/env python3
"""_overview/ の LLM合成ファイルを Batch API で生成する。

フェーズ:
  python build_overview_batch.py --prepare
  python build_overview_batch.py --submit
  python build_overview_batch.py --process

生成対象:
  01_PON_persona.md            (Opus)
  02_business_overview.md      (Opus)
  03_decisions_log.md          (Sonnet)
  04_open_ideas.md             (Sonnet)
  themes/給与制度とスタッフマネジメント.md  (Sonnet)
  themes/プロモーション・マーケティング.md   (Sonnet)
  themes/商品開発・ブランド戦略.md        (Sonnet)
  themes/人事評価・採用.md               (Sonnet)
  themes/競合分析と市場対応.md           (Sonnet)
  themes/海外展開とJ-Beauty.md          (Sonnet)
  themes/経営指標・財務管理.md           (Sonnet)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# 親パイプラインの .env を使う
load_dotenv("/Users/rikutanaka/RestaurantAILab/Markdowns-1/Stock/バンコクPonさん案件/AIOS提供/ChatGPT分析/.env")

ROOT = Path("/Users/rikutanaka/aipm_v0/Flow/202604/2026-04-22/バンコクPonさん案件")
OVERVIEW_DIR = ROOT / "output/pon-chatgpt-knowledge/ChatGPT履歴/_overview"
BATCH_DIR = ROOT / "scripts/batch_work"
BATCH_DIR.mkdir(parents=True, exist_ok=True)

CONTENT_ROOT = ROOT / "output/pon-chatgpt-knowledge/ChatGPT履歴"
CATEGORIES = ["美容室", "美容専門店", "自社ブランド", "J-Beauty"]

MODEL_OPUS = "claude-opus-4-5"
MODEL_SONNET = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

PON_CONTEXT = """# PONさんコンテキスト
- 氏名: 近藤Pon (Rios Innovation Co., Ltd. 社長)
- 拠点: バンコク（タイ）
- 事業:
  * 美容室: Rapi-rabi（カラー専門10店舗）/ YAMS hair & cafe（託児）/ Cuu's hair（個室）/ BELL otonagami（オトナ世代）/ Rio Hair Design（シラチャ・日本）/ ベトナム支店（ホーチミン）
  * 美容専門店: ネイルサロン / アイラッシュ / MONDO BEAUTY clinic（医療系）
  * 自社ブランド: ヌリプラ（カラー剤）/ DOT（シャンプー・トリートメント）/ KINUJO（提携）/ 店販・EC
  * J-Beauty事業: 日本美容のタイ展開、アカデミー、政策提言、イベント、インフルエンサー連携
- 関係者: Hiroto（COO）/ 田中利空（開発）/ 町田大地（AI活用支援）/ その他多数のスタッフ

このコンテキストを踏まえた上で、以下の素材から指定された形式でMarkdownファイルを出力してください。
余計な前置き・コードブロック・説明文は不要。本文Markdownのみ出力。"""


def collect_all_summaries() -> str:
    """全サブカテゴリの conversations_summary.md を結合して返す。"""
    parts = []
    for cat in CATEGORIES:
        cat_dir = CONTENT_ROOT / cat
        for subcat_dir in sorted(cat_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue
            summary = subcat_dir / "conversations_summary.md"
            if summary.exists():
                parts.append(f"\n\n========== {cat} > {subcat_dir.name} ==========\n")
                content = summary.read_text(encoding="utf-8")
                # 各サマリーは長すぎる場合があるので先頭2500字に圧縮
                if len(content) > 2500:
                    content = content[:2500] + "\n...（以下省略）"
                parts.append(content)
    return "".join(parts)


def collect_category_readmes() -> str:
    """4カテゴリREADMEを結合して返す。"""
    parts = []
    for cat in CATEGORIES:
        readme = CONTENT_ROOT / cat / "README.md"
        if readme.exists():
            parts.append(f"\n\n========== {cat} ==========\n")
            parts.append(readme.read_text(encoding="utf-8"))
    return "".join(parts)


def build_requests() -> list[dict]:
    all_summaries = collect_all_summaries()
    cat_readmes = collect_category_readmes()

    requests = []

    # 01 PON_persona (Opus)
    requests.append({
        "custom_id": "ov_01_persona",
        "filename": "01_PON_persona.md",
        "model": MODEL_OPUS,
        "system": PON_CONTEXT,
        "user": f"""以下の素材（4カテゴリREADME）から、PONさんのペルソナ定義ファイルを生成してください。

【生成物の形式】
```
# PONさんペルソナ定義（AI用コンテキスト）

## このファイルの目的
（AIが会話冒頭で読んで、PONさんを誰として扱うか即座に理解するためのファイル）

## 基本情報
（氏名、役職、会社、拠点、国籍・言語状況など）

## 事業ポートフォリオ
（美容室・美容専門店・自社ブランド・J-Beauty の俯瞰、各事業の位置づけ）

## 価値観・意思決定スタイル
（何を重視するか・どう判断するか・何を嫌うか——会話履歴から読み取れる傾向）

## 関心領域・現在の重点テーマ
（給与制度、海外展開、ブランディング等、今関心が集中している領域）

## コミュニケーションの特徴
（日本語中心、タイ語・英語の混ざり方、議論スタイル）

## AIへの期待（含み方）
（どんな使い方をしているか、どう返してほしいか）

## コンテキスト利用のヒント
（AIがこのファイルを読んだ後、さらにどのファイルを参照すべきかの案内）
```

本文のみ、3000〜5000字で。

【素材: カテゴリREADME群】
{cat_readmes[:40000]}"""
    })

    # 02 business_overview (Opus)
    requests.append({
        "custom_id": "ov_02_business",
        "filename": "02_business_overview.md",
        "model": MODEL_OPUS,
        "system": PON_CONTEXT,
        "user": f"""以下の4カテゴリREADMEから、PONさんの事業ポートフォリオ全体像を俯瞰する資料を生成してください。

【生成物の形式】
```
# 事業全体像俯瞰（PONさんのビジネスマップ）

## このファイルの目的

## 事業ポートフォリオ概観
（図解または階層的な箇条書きで、4事業領域の関係性・重なり・シナジーを示す）

## 各事業領域の解説
### 美容室事業
### 美容専門店事業
### 自社ブランド事業
### J-Beauty事業
（各事業の現状・主要な論点・相互作用）

## 横串の課題（複数事業にまたがる論点）
（人事制度・ブランディング・海外展開など、事業横断の論点をまとめる）

## 戦略的な方向性（会話履歴から読み取れる傾向）

## 参照ガイド
（特定事業を深掘りしたいとき、どのProject/subcategoryを見るか）
```

4000〜6000字。

【素材: 4カテゴリREADME】
{cat_readmes[:40000]}"""
    })

    # 03 decisions_log (Sonnet)
    requests.append({
        "custom_id": "ov_03_decisions",
        "filename": "03_decisions_log.md",
        "model": MODEL_SONNET,
        "system": PON_CONTEXT,
        "user": f"""以下の全サブカテゴリサマリーから、**PONさんが過去に下した具体的な決定事項**を時系列で抽出してください。
（給与率・コミッション率・人件費比率・手当金額・スケジュール・組織変更など、数値や具体的なアクションを伴うもの）

【生成物の形式】
```
# 決定事項ログ（時系列）

## このファイルの目的
（過去の決定事項を参照できるようにし、意思決定の一貫性を保つため）

## 決定事項一覧

### 給与・コミッション関連
- **決定日/時期**: YYYY-MM
  - 内容: ...
  - 背景: ...
  - 関連カテゴリ: ...
（以下、決定ごとに）

### 組織・人事制度

### 商品・ブランド

### 海外展開・出店

### 経営指標・KPI

### 福利厚生

### その他

## 注意・保留事項
（決まっていない・揺れている論点）
```

具体的な数値・日付を可能な限り残す。2500〜4500字。

【素材: 全サブカテゴリサマリー】
{all_summaries[:90000]}"""
    })

    # 04 open_ideas (Sonnet)
    requests.append({
        "custom_id": "ov_04_ideas",
        "filename": "04_open_ideas.md",
        "model": MODEL_SONNET,
        "system": PON_CONTEXT,
        "user": f"""以下の全サブカテゴリサマリーから、**PONさんが過去に検討したが実行には至っていない・保留になっているアイデア**を抽出してください。
（新商品案、新店舗候補、未投入のマーケ施策、検討段階の組織改編、未発表のブランド案 など）

【生成物の形式】
```
# 未実行アイデア集

## このファイルの目的
（過去のアイデアをストックし、将来再検討する際の参照源とする）

## アイデア一覧

### 商品・ブランド案

### 店舗・業態案

### マーケ・プロモーション案

### 組織・制度案

### 海外展開・新規事業案

### その他

## 各アイデアの記述形式
- **アイデア名**: ...
- **時期**: いつ話題に出たか
- **検討内容**: 何を検討したか
- **保留理由**: なぜ未実行か（推測含む）
- **関連**: 参照すべきサブカテゴリ

## 再検討の優先順（任意）
```

2500〜4500字。

【素材: 全サブカテゴリサマリー】
{all_summaries[:90000]}"""
    })

    # Themes (7 × Sonnet)
    theme_defs = [
        ("給与制度とスタッフマネジメント", "給与体系・コミッション・人件費・評価・昇給・福利厚生"),
        ("プロモーション・マーケティング", "SNS・広告・キャンペーン・コラボ・ブランディング"),
        ("商品開発・ブランド戦略", "カラー剤・シャンプー・EC・商品企画・ブランド構築"),
        ("人事評価・採用", "採用・離職対策・面接・評価制度・店長育成・研修"),
        ("競合分析と市場対応", "競合調査・価格・市場ポジション・韓国系サロン・差別化戦略"),
        ("海外展開とJ-Beauty", "タイ進出・ベトナム・日本市場逆輸入・J-Beauty政策・アカデミー"),
        ("経営指標・財務管理", "売上・利益・人件費率・KPI・予算・税務・法務"),
    ]
    for idx, (theme_name, theme_desc) in enumerate(theme_defs, start=1):
        requests.append({
            "custom_id": f"ov_theme_{idx:02d}",
            "filename": f"themes/{theme_name}.md",
            "model": MODEL_SONNET,
            "system": PON_CONTEXT,
            "user": f"""以下の全サブカテゴリサマリーから、「**{theme_name}**」({theme_desc}) に関するPONさんの思考・議論・決定をテーマ横断でまとめてください。

【生成物の形式】
```
# {theme_name}

## このテーマの位置づけ
（PONさん事業における位置・重要度）

## 過去の主要議論（時系列）
- **時期**: YYYY-MM
  - 論点: ...
  - 検討結果: ...
（4〜10件程度）

## 決定事項（数値・具体アクション）

## 未解決・継続検討事項

## ノウハウ・ベストプラクティス
（議論から抽出できた知見）

## 関連Project
- 美容室 > ...
- 自社ブランド > ...
```

必ず数値・具体例を含める。2000〜3500字。

【素材: 全サブカテゴリサマリー】
{all_summaries[:80000]}"""
        })

    return requests


def prepare():
    print("=" * 60)
    print("Overview Batch [prepare]")
    print("=" * 60)
    requests = build_requests()
    out_file = BATCH_DIR / "batch_requests.jsonl"
    meta = []
    with open(out_file, "w", encoding="utf-8") as f:
        for r in requests:
            meta.append({"custom_id": r["custom_id"], "filename": r["filename"], "model": r["model"]})
            body = {
                "custom_id": r["custom_id"],
                "params": {
                    "model": r["model"],
                    "max_tokens": MAX_TOKENS,
                    "system": r["system"],
                    "messages": [{"role": "user", "content": r["user"]}],
                },
            }
            f.write(json.dumps(body, ensure_ascii=False) + "\n")
    (BATCH_DIR / "batch_items_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  {len(requests)} requests prepared at {out_file}")
    print(f"  size: {out_file.stat().st_size/1024:.1f} KB")


def get_client():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=key)


def submit():
    print("=" * 60)
    print("Overview Batch [submit]")
    print("=" * 60)
    client = get_client()
    req_file = BATCH_DIR / "batch_requests.jsonl"
    requests = [json.loads(line) for line in open(req_file, encoding="utf-8")]
    print(f"  submitting {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    log = {
        "batch_id": batch.id,
        "status": batch.processing_status,
        "request_count": len(requests),
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (BATCH_DIR / "batch_log.json").write_text(
        json.dumps([log], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  batch_id: {batch.id}  status: {batch.processing_status}")


def process():
    print("=" * 60)
    print("Overview Batch [process]")
    print("=" * 60)
    client = get_client()
    log = json.loads((BATCH_DIR / "batch_log.json").read_text(encoding="utf-8"))
    batch_id = log[-1]["batch_id"]
    batch = client.messages.batches.retrieve(batch_id)
    print(f"  batch_id: {batch_id}  status: {batch.processing_status}")
    print(f"  succeeded: {batch.request_counts.succeeded}, errored: {batch.request_counts.errored}")
    if batch.processing_status != "ended":
        print("  NOT ready yet")
        sys.exit(2)
    results_file = BATCH_DIR / "batch_results.jsonl"
    with open(results_file, "w", encoding="utf-8") as f:
        for r in client.messages.batches.results(batch_id):
            f.write(r.model_dump_json() + "\n")
    meta = json.loads((BATCH_DIR / "batch_items_meta.json").read_text(encoding="utf-8"))
    meta_map = {m["custom_id"]: m for m in meta}

    success = 0
    errors = []
    for line in open(results_file, encoding="utf-8"):
        entry = json.loads(line)
        cid = entry.get("custom_id")
        result = entry.get("result", {})
        if result.get("type") != "succeeded":
            errors.append((cid, result.get("error", {})))
            continue
        text = ""
        for block in result.get("message", {}).get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")
        m = meta_map.get(cid)
        if not m:
            print(f"  WARN: unknown custom_id {cid}")
            continue
        out_path = OVERVIEW_DIR / m["filename"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        success += 1
        print(f"  ✓ wrote {out_path.name} ({len(text)} chars)")
    if errors:
        print(f"\n  ERRORS: {len(errors)}")
        for cid, err in errors:
            print(f"    - {cid}: {err}")
    print(f"\n  SUCCESS: {success}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--submit", action="store_true")
    p.add_argument("--process", action="store_true")
    args = p.parse_args()
    if args.prepare:
        prepare()
    elif args.submit:
        submit()
    elif args.process:
        process()
    else:
        p.print_help()
