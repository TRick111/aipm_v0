# PMBOK × Lean UX × Agile ― ハイブリッド管理システム 利用ガイド

このドキュメントは、PMBOK標準、Lean UX、およびアジャイル手法を融合したプロジェクト管理システムの使い方を説明するものです。

**対象読者**: プロジェクト責任者 / PO / スクラムマスター / UX デザイナー / PMO ― 「ドキュメントも実装もユーザー価値も、すべて1本のレールで回したい」人たち

## 1. システム概要

このシステムは、プロジェクト管理における文書作成から確定・アーカイブまでの流れを自動化し、LLM（大規模言語モデル）の支援を受けながらプロジェクトを効率的に進めるためのものです。

### 主な特徴

- **PMBOK × Lean UX × Agileハイブリッド**: 上流工程はPMBOK準拠の文書管理、中流にLean UXの発見と検証、実装フェーズはアジャイル手法を採用
- **フォルダ構造の分離**: `Flow`（ドラフト）→ `Stock`（確定版）→ `Archived`（完了プロジェクト）
- **自動文書生成**: 質問応答による文書ドラフト作成
- **自動同期**: 「確定反映」コマンドによるFlowからStockへの文書移動
- **LLM活用**: 各フェーズで適切な質問と文書テンプレートを提供

### 成し遂げたいこと

1. **"正しい課題"にフォーカス**: Lean UX & デザイン思考のDiscovery → 仮説検証をPMBOKの立ち上げに取り込み、作る前に迷子にならない
2. **学習しながら作る**: Dual-Track/Continuous DiscoveryをアジャイルDevelopmentと並走させ、ユーザーの声が常にバックログへ直結
3. **ドキュメントを無駄にしない**: "Flow → Stock → Archived"の3層によって、必要最小限の文書だけが公式資産として残る
4. **拡張し続けられる**: ルール自体を対話で増やせる（90_rule_maintenance.mdc）。プロセス改善がコード管理できる

## 2. システム全体像

```
┌──────────────────────────────┐   trigger（チャットコマンド）
│ 00_master_rules.mdc           │◀───────────────────────┐
└─────────┬────────────────────┘                        │
          call                                          │
┌─────────▼────────────┐   発散/収束も Draft 化           │
│ 01‑06_pmbok_*.mdc     │──────────────────┐             │
│ 08_flow_assist.mdc    │    create_draft  │             │
└─────────┬────────────┘                │             │
          ▼ Draft (.md)              │             │
      Flow/YYYYMM/YYYY‑MM‑DD/─────────────────────────────┘       │
          │  human review + "確定反映して"                         │
          ▼                                                      │
      Stock/programs/PROGRAM/projects/PROJECT/.. ← flow_to_stock_rules.mdc  ────┘
```

### 主要コンセプト

#### 三つ巴モデル

| 方法論 | 役割 |
|--------|------|
| **PMBOK** | フェーズ & 知識エリアで **What** を管理 |
| **Lean UX/Design Thinking** | ユーザー中心の **Why** を確認 |
| **Agile / Scrum** | イテレーションで **How** を適応 |

このシステムはPMBOKの骨格にLean UXのDiscoveryとアジャイルDeliveryをレイヤー合成しているため、上流で迷わず・開発中に学び・下流で残せるワークフローが1つにまとまります。

#### Flow / Stock / Archived

| 階層 | 役割 | 保存ポリシー |
|------|------|------------|
| **Flow** | 下書き・ラフアイデア・日次アウトプット | 年月/日付フォルダ。原則7〜14日で確定か消す |
| **Stock** | 承認済みドキュメント・正式成果物 | バージョンタグ付き。プロジェクト期間中は常時参照 |
| **Archived** | 完了プロジェクトの凍結コピー | 監査 & ナレッジ共有用に保管 |

#### 4ステップ・サイクル

1. **Ask** - LLMが質問で情報収集
2. **Draft** - テンプレへ自動整形（Flow）
3. **Review** - 人が編集 → 「確定反映して」
4. **Sync** - Shell / ルールでStockへ自動移動

## 3. 基本的なフォルダ構造

```
プロジェクトルート/
├── .cursor/
│   └── rules/         # LLMルールファイル群
│       ├── basic/     # 基本ルールフォルダ
│       │   ├── pmbok_paths.mdc
│       │   ├── 00_master_rules.mdc
│       │   ├── 01_pmbok_initiating.mdc
│       │   └── ...
│       └── real_estate/  # 業種別特化ルール
├── Flow/              # 日付ごとのドラフト文書
│   ├── YYYYMM/        # 年月フォルダ
│   │   ├── YYYY-MM-DD/    # 作業日ごとのフォルダ
│   │   │   ├── draft_project_charter.md
│   │   │   └── ...
│   │   └── ...
│   └── templates/     # テンプレート
├── Stock/             # 確定済み文書
│   ├── programs/      # プログラム単位でのフォルダ
│   │   └── PROGRAM_NAME/  # プログラムフォルダ
│   │       └── projects/
│   │           └── PROJECT_ID/  # プロジェクトごとのフォルダ
│   │               └── documents/
│   │                   ├── 1_initiating/
│   │                   ├── 2_discovery/
│   │                   ├── 2_research/
│   │                   ├── 3_planning/
│   │                   ├── 4_executing/
│   │                   ├── 5_monitoring/
│   │                   └── 6_closing/
│   └── shared/         # 共有テンプレート
│       └── templates/
└── Archived/          # 完了プロジェクト
    └── programs/      # アーカイブ済みプログラム
```

## 4. システムのセットアップ

### 初期設定

新規ワークスペースのセットアップは、以下のスクリプトを使用して簡単に行えます：

```bash
# 1. リポジトリのクローン (もしくはZIPでダウンロード)
git clone https://github.com/youruser/aipm_workspace.git
cd aipm_workspace

# 2. ワークスペース作成スクリプトの実行
./setup_workspace_simple.sh /path/to/new/workspace
```

これにより、基本的なディレクトリ構造、Flow内の年月日フォルダ、必要なリポジトリのクローンが行われます。

### セットアップスクリプトの主な機能

`setup_workspace_simple.sh` スクリプトを使用すると、以下の作業が自動的に行われます：

1. **基本ディレクトリ構造の作成**
   - Flow, Stock, Archived などの基本フォルダ
   - ルールファイル用の .cursor/rules フォルダ
   - プログラム用フォルダ Stock/programs

2. **Flow内の年月日フォルダ作成**
   - 現在の日付で Flow/YYYYMM/YYYY-MM-DD 形式のフォルダ作成

3. **各種リポジトリのクローン**
   - ルールリポジトリ（.cursor/rules/basic など）
   - スクリプトリポジトリ（scripts ディレクトリ）
   - プログラムリポジトリ（Stock/programs 配下）

### 必要なルールファイル

`.cursor/rules/`ディレクトリに以下のファイルを配置します：

- `basic/pmbok_paths.mdc` - パス変数定義
- `basic/00_master_rules.mdc` - マスタールール
- `basic/01_pmbok_initiating.mdc` - 立ち上げフェーズのテンプレート
- `basic/02_pmbok_discovery.mdc` - 発見フェーズのテンプレート
- `basic/02_pmbok_research.mdc` - 調査フェーズのテンプレート
- `basic/03_pmbok_planning.mdc` - 計画フェーズのテンプレート
- `basic/04_pmbok_executing.mdc` - 実行フェーズのテンプレート
- `basic/05_pmbok_monitoring.mdc` - 監視・コントロールフェーズのテンプレート
- `basic/06_pmbok_closing.mdc` - 終結フェーズのテンプレート
- `basic/08_pmbok_flow_assist.mdc` - フロー支援機能
- `basic/09_pmbok_development.mdc` - 開発フェーズ支援
- `basic/90_rule_maintenance.mdc` - ルール自体のメンテナンス用
- `basic/flow_to_stock_rules.mdc` - 自動同期ルール

## 5. フェーズ別の使い方

### 0️⃣ 事前準備

```bash
# ワークスペース作成
./setup_workspace_simple.sh /path/to/workspace

# プロジェクト作成ガイド
「カレー作りたい　プロジェクト開始して」  # → プログラム名を尋ねられます
「夕食作り」  # プログラム名を入力
「はい」  # 確認に応答
```

上記の対話により、以下の処理が行われます：
- プログラムディレクトリ作成（Stock/programs/夕食作り）
- プロジェクトディレクトリ作成（Stock/programs/夕食作り/projects/カレー）
- ドキュメントフォルダ作成（documents/1_initiating など）
- Flowフォルダ作成（Flow/YYYYMM/YYYY-MM-DD/夕食作り_カレー）

### 1️⃣ 立ち上げ（Initiating）

```
# プロジェクト憲章作成
「プロジェクト憲章を作成したい」  # LLMが質問に導きます
# 質問に回答すると、Flow/YYYYMM/YYYY-MM-DD/draft_project_charter.md が生成されます

# 内容確認後、確定反映
「確定反映して」  # draft_project_charter.mdがStockフォルダに移動

# プロダクト（プログラム）定義
「プロダクト定義」  # プログラムレベルの定義書作成
「確定反映して」  # 確定処理

# ステークホルダー分析
「ステークホルダー分析やりたい」  # 同様に質問と回答で文書作成
「確定反映して」  # 確定処理
```

### 2️⃣ 発見（Discovery）

```
# Discoveryフェーズのメニュー表示
「Discovery」  # 利用可能なテンプレートリスト表示

# 前提条件マップ作成
「仮説マップ」  # 仮説検証に必要な前提条件をマッピング
「確定反映して」  # Flow/YYYYMM/YYYY-MM-DD/draft_assumption_map.md を確定

# ペルソナ作成
「ペルソナ作成」  # ユーザーペルソナ定義
「確定反映して」

# 問題定義
「課題定義」  # 解決すべき問題の定義
「確定反映して」

# その他のDiscoveryドキュメント
「ジャーニーマップ」  # ユーザージャーニーマップ作成
「ソリューション定義」  # ソリューション定義書作成
「検証計画」  # 仮説検証計画
「UXリサーチ」  # UXリサーチ調査概要
```

### 2️⃣-B リサーチ（Research）

```
# Researchフェーズのメニュー表示
「Research」  # 利用可能な調査テンプレート表示

# 顧客調査レポート
「顧客調査」  # 顧客調査レポート作成
「確定反映して」

# 競合調査レポート
「競合調査」  # 競合分析
「確定反映して」

# デスクリサーチ
「デスクリサーチ」  # 市場・業界など総合的な調査
「確定反映して」

# 市場規模推定
「市場規模推定」  # TAM/SAM/SOM分析
「確定反映して」
```

### 2️⃣-C プレゼンテーション（Presentation）

```
# プレゼン資料生成
「プレゼン資料生成」  # Marpを使用したプレゼンテーション作成

# プレゼン用の図表作成
「図表生成」  # draw.ioテンプレートからの図表作成
「確定反映して」  # 編集したプレゼン資料を確定
```

### 3️⃣ 計画（Planning）

```
# WBS作成
「WBS作成」  # 質問に回答してWBSドラフトを作成
「確定反映して」  # 確定処理

# プロダクトバックログ初期化
「プロダクトバックログ初期化して」  # バックログの初期構造作成

# リスク計画
「リスク計画」  # リスク分析と対策計画作成

# プロジェクトスコープ記述書
「プロジェクトスコープ記述書」  # スコープ定義

# プロダクト要求仕様書
「プロダクト要求仕様書」 # PRD作成

# リリースロードマップ
「ロードマップ作成」  # リリース計画作成
```

### 4️⃣ 実行（Executing）とDevelopment

```
# 開発フェーズの開始
「Development」  # 利用可能な開発テンプレート表示

# 開発環境セットアップ
「開発環境初期化」  # 環境セットアップドキュメント作成

# 開発計画
「開発計画作成」  # 実装計画書作成

# 実装順序計画
「実装順序計画」  # 依存関係を考慮した実装順序の定義

# ストーリー実装
「ストーリー実装」  # 個別ストーリー実装計画

# スプリントゴール
「スプリントゴール」 # Sprint Goal Sheet作成

# 日次タスク
「今日のタスク」  # 日次タスクリスト生成
```

### 5️⃣ 監視・コントロール（Monitoring）

```
# 変更要求管理
「変更要求」  # 変更要求テンプレート作成

# スプリントレビュー
「スプリントレビュー作成」  # レビュー自動生成
```

### 6️⃣ 終結（Closing）

```
# 教訓記録
「教訓記録」  # Lessons Learned作成
「確定反映して」

# 移管ドキュメント
「移管ドキュメント作成」  # 引き継ぎ資料作成
```

## 6. ユースケース：カレープロジェクト

以下は、実際のプロジェクト例として「カレー作り」プロジェクトの流れを示します。

### 1. プロジェクト初期化
```
User: カレー作りたい　プロジェクト開始して
AI: 「カレー」のプログラム名（カテゴリ）を教えてください。
User: 夕食作り
AI: 以下の内容でプロジェクトを初期化します：
    プログラム: 夕食作り
    プロジェクト: カレー
    よろしいですか？
User: はい
```

この対話により、以下のフォルダ構造が作成されます：
```
Stock/programs/夕食作り/projects/カレー/
└── documents/
    ├── 1_initiating/
    ├── 2_discovery/
    ├── 2_research/
    ├── 3_planning/
    ├── 4_executing/
    ├── 5_monitoring/
    └── 6_closing/

Flow/202505/2025-05-05/夕食作り_カレー/
└── daily_tasks.md
```

### 2. プロジェクト憲章の作成
```
User: プロジェクト憲章つくって
AI: 【プロジェクト憲章】の作成に必要な情報を収集します。以下の質問に回答してください。
    1. プロジェクト名: カレー
    2. プロジェクトの目的: 
    3. プロジェクトの背景: 
    [...]
User: おまかせ
AI: 収集した情報で「プロジェクト憲章」のドラフトを作成してよろしいですか？
User: はい
```

AIは以下の内容を含む詳細なプロジェクト憲章を作成します：
- プロジェクト概要（名前、期間、オーナー）
- 目的と背景
- スコープ（含まれるもの/含まれないもの）
- 成果物
- ステークホルダー一覧
- マイルストーン
- 予算（食材費3,000円、消耗品500円）
- リスク管理計画
- 制約条件と前提条件

### 3. ペルソナの作成
```
User: ペルソナ作成して
AI: 【ペルソナ作成】に必要な情報を収集します。以下の質問に回答してください。
    1. ペルソナの名前: 
    2. 年齢・世代: 
    [...]
User: おまかせ
```

AIは以下の詳細情報を含むペルソナを作成します：
- 基本情報：田中健太（42歳、IT企業PM、4人家族）
- ライフスタイル：平日は仕事、週末は料理担当
- 目標と課題：家族の好みにばらつきがある、調理時間の見積もりが苦手
- 行動特性：レシピサイトやSNSで情報収集、家族の意見を聞いて決定
- 好みと傾向：程よい辛さのカレーが好き
- 使用ツール：スマートフォン、料理アプリ
- 代表的な発言：「家族が笑顔になる料理を作りたいな」

この例はプロジェクト管理手法を日常的なタスクに適用する方法を示しており、以下のフェーズに進むことで、カレープロジェクトは成功へと導かれます：
- Discovery：材料や調理方法の調査
- Planning：レシピ決定、買い物リスト作成
- Executing：材料購入、調理
- Monitoring：味の調整
- Closing：完成・振り返り

## 7. 主要コマンドリファレンス

### 文書作成コマンド（トリガーワード）

#### 立ち上げフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「プロジェクト初期化」 | プログラム・プロジェクト構造作成 | Stock/programs/<PROGRAM>/projects/<PROJECT>/ |
| 「プロダクト定義」 | プロダクト（プログラム）定義書作成 | Flow/YYYYMM/YYYY-MM-DD/draft_program_definition.md |
| 「プロジェクト憲章」 | プロジェクト憲章作成 | Flow/YYYYMM/YYYY-MM-DD/draft_project_charter.md |
| 「ステークホルダー分析」 | ステークホルダー分析 | Flow/YYYYMM/YYYY-MM-DD/draft_stakeholder_analysis.md |

#### Discoveryフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「仮説マップ」 | 前提条件マップ作成 | Flow/YYYYMM/YYYY-MM-DD/draft_assumption_map.md |
| 「ペルソナ作成」 | ユーザーペルソナ作成 | Flow/YYYYMM/YYYY-MM-DD/draft_persona.md |
| 「課題定義」 | 問題定義書作成 | Flow/YYYYMM/YYYY-MM-DD/draft_problem_statement.md |
| 「仮説バックログ」 | 仮説リスト作成 | Flow/YYYYMM/YYYY-MM-DD/draft_hypothesis_backlog.md |
| 「ジャーニーマップ」 | ユーザージャーニーマップ | Flow/YYYYMM/YYYY-MM-DD/draft_user_journey_map.md |

#### Researchフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「顧客調査」 | 顧客調査レポート | Flow/YYYYMM/YYYY-MM-DD/draft_customer_research.md |
| 「競合調査」 | 競合分析レポート | Flow/YYYYMM/YYYY-MM-DD/draft_competitor_research.md |
| 「デスクリサーチ」 | 総合調査レポート | Flow/YYYYMM/YYYY-MM-DD/draft_desk_research.md |
| 「市場規模推定」 | TAM/SAM/SOM分析 | Flow/YYYYMM/YYYY-MM-DD/draft_market_size_estimation.md |

#### プレゼンテーションフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「プレゼン資料生成」 | Marpによるスライド作成 | Flow/YYYYMM/YYYY-MM-DD/draft_presentation.md |
| 「図表生成」 | Draw.io図表テンプレート作成 | Flow/YYYYMM/YYYY-MM-DD/assets/diagram.drawio |

#### Planningフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「WBS作成」 | WBSドラフト作成 | Flow/YYYYMM/YYYY-MM-DD/draft_wbs.md |
| 「リスク計画」 | リスク分析と計画 | Flow/YYYYMM/YYYY-MM-DD/draft_risk_plan.md |
| 「プロジェクトスコープ記述書」 | スコープ定義書 | Flow/YYYYMM/YYYY-MM-DD/draft_project_scope_statement.md |
| 「プロダクト要求仕様書」 | PRD作成 | Flow/YYYYMM/YYYY-MM-DD/draft_product_requirements.md |
| 「ロードマップ作成」 | リリース計画 | Flow/YYYYMM/YYYY-MM-DD/draft_product_roadmap.md |

#### Developmentフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「開発環境初期化」 | 環境セットアップ | Flow/YYYYMM/YYYY-MM-DD/development/draft_setup.md |
| 「開発計画作成」 | 実装計画書 | Flow/YYYYMM/YYYY-MM-DD/development/draft_development_plan.md |
| 「実装順序計画」 | 実装順序定義 | Flow/YYYYMM/YYYY-MM-DD/development/draft_implementation_order.md |
| 「ストーリー実装」 | ストーリー実装計画 | Flow/YYYYMM/YYYY-MM-DD/development/draft_story_implementation.md |

#### Executingフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「スプリントゴール」 | スプリント目標設定 | Flow/YYYYMM/YYYY-MM-DD/draft_sprint_goal_Sn.md |
| 「今日のタスク」 | 日次タスク | Flow/YYYYMM/YYYY-MM-DD/daily_tasks.md |
| 「議事録」 | 会議議事録 | Flow/YYYYMM/YYYY-MM-DD/draft_meeting_minutes.md |

#### Closingフェーズ
| コマンド | 説明 | 出力先 |
|--------|------|-------|
| 「教訓記録」 | 教訓記録 | Flow/YYYYMM/YYYY-MM-DD/draft_lessons_learned.md |
| 「移管ドキュメント作成」 | 引き継ぎ資料 | Flow/YYYYMM/YYYY-MM-DD/draft_transition_document.md |

### システムコマンド

| コマンド | 説明 |
|--------|------|
| 「確定反映して」 | Flow→Stock同期を実行 |
| 「作業開始」 | 今日の日付フォルダとタスクファイルを作成 |
| 「フェーズ追加」 | 新しいフェーズルールの雛形を生成 |

## 8. ワークスペースのゼロからの構築方法

AIプロジェクト管理システムを新規に構築するには、以下の手順に従います：

### 1. 基本ワークスペースの構築

```bash
# 方法1: GitHubからリポジトリをクローン
git clone https://github.com/yourusername/aipm_workspace.git
cd aipm_workspace

# 方法2: スクリプトファイルを直接ダウンロードして使用
# setup_workspace_simple.sh をダウンロードし、実行権限を付与
chmod +x setup_workspace_simple.sh

# ワークスペース構築の実行
./setup_workspace_simple.sh /path/to/new/workspace
```

このスクリプトは以下を自動的に実行します：
- 基本ディレクトリ構造の作成
- 現在の日付でFlow内に年月/日付フォルダを作成
- 必要に応じてルールリポジトリとスクリプトリポジトリをクローン

### 2. ルールファイルのセットアップ

```bash
# ルールファイルがクローンされない場合は手動でコピー
mkdir -p /path/to/workspace/.cursor/rules/basic
cp -r sample_rules/basic/* /path/to/workspace/.cursor/rules/basic/

# 業種別特化ルールのセットアップ（オプション）
mkdir -p /path/to/workspace/.cursor/rules/real_estate
cp -r sample_rules/real_estate/* /path/to/workspace/.cursor/rules/real_estate/
```

### 3. 最初のプロジェクト作成

```bash
# LLMとのチャットで実行
「プロジェクト初期化」
# プログラム名とプロジェクト名を入力
```

### 4. 同期スクリプトのセットアップ

```bash
# 同期スクリプトの配置
cp sample_scripts/flow_to_stock.sh /path/to/workspace/
chmod +x /path/to/workspace/flow_to_stock.sh
```

## 9. トラブルシューティング

### よくある問題と解決方法

1. **ファイル名パターンマッチングエラー**
   - **症状**: 「指定されたパターンに一致するファイルが見つかりません」
   - **解決方法**: ドラフトファイル名が`flow_to_stock_config.sh`のパターンと一致しているか確認

2. **同期エラー**
   - **症状**: 同期が失敗する
   - **解決方法**: シェルスクリプトに実行権限があることを確認
     ```bash
     chmod +x flow_to_stock.sh trigger_flow_to_stock.sh
     ```

3. **ルール発火しない**
   - **症状**: トリガーワードを入力してもLLMが応答しない
   - **解決方法**: `.cursor/rules/`内のルールファイルパスを確認。00_master_rules.mdcのトリガーとキーワードが合っているか確認。

4. **Flow/Stock パス解決エラー**
   - **症状**: パスが正しく解決されない
   - **解決方法**: `pmbok_paths.mdc` のパス定義が最新の構造（年月/日付フォルダ）に対応しているか確認

## 10. ベストプラクティス

1. **年月/日付フォルダの利用**: Flow内は必ず年月/日付フォルダ（YYYYMM/YYYY-MM-DD形式）を使用
2. **YAML前付け**: Flow文書にはYAML前付けを追加（doc_targets, importance等）
3. **定期的な同期**: 文書編集後は速やかに「確定反映して」を実行
4. **ファイル命名規則**: ドラフトには必ず`draft_`プレフィックスを付ける
5. **ルールファイル管理**: ルールファイルの変更は慎重に行い、バックアップを取る
6. **プログラム/プロジェクト階層**: 関連プロジェクトはプログラム名でグループ化

## 11. 今後のロードマップ

- **Slide-Builder**: Flowのdraft_story → Keynote / PPTXを自動生成
- **AI QA Bot**: Stock内ドキュメントをベクトル検索してSlack Q&A
- **Metrics Dashboard**: Velocity・NPS・リードタイムを自動集計
- **クロスプロジェクト分析**: 複数プロジェクトのメタデータ収集と分析

アイデア歓迎！ "ルール自体をChatで増やせる"文化で継続的に改善しましょう。

---

このシステムは「Ask → Draft → Review → Sync」の4アクションを軸に、**PMBOK × Lean UX × Agile**のベストプラクティスを一貫して実現します。 
