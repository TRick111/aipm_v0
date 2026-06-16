# log（ChefsRoomマーケティング支援）

## 目的
- このプロジェクトの変更履歴（ファイルの作成/削除/編集）が追えるようにする。

## 変更履歴

| 日付 | 種別 | ファイル | 変更内容（任意） | 変更理由（任意） |
|---|---|---|---|---|
| 2026-01-17 | create | `README.md` | プロジェクト初期化 | |
| 2026-01-17 | create | `ProjectIndex.yaml` | プロジェクト初期化 | |
| 2026-01-17 | create | `log.md` | プロジェクト初期化 | |
| 2026-02-01 | create | `2.execute/2.input/2026-02-01/input.csv` | 入力テーマリスト（Flowから確定反映） | |
| 2026-02-01 | create | `2.execute/2.input/2026-02-01/input_raw.csv` | 変換前素材（Flowから確定反映） | |
| 2026-02-01 | create | `2.execute/2.input/2026-02-01/input2.csv` | 入力テーマリスト（Flowから確定反映） | |
| 2026-02-01 | create | `2.execute/2.input/2026-02-01/input2_raw.csv` | 変換前素材（Flowから確定反映） | |
| 2026-02-01 | create | `2.execute/3.output/2026-02-01/generated_scripts_2026_02_01.csv` | 台本生成結果（12件×17シーン） | |
| 2026-02-01 | create | `2.execute/3.output/2026-02-01/generated_scripts_2026_02_01_input2.csv` | 台本生成結果（12件×17シーン） | |
| 2026-02-01 | create | `2.execute/1.scripts/flow_runner/*` | Flow上で完結実行するためのスクリプト一式 | |
| 2026-02-01 | edit | `ProjectIndex.yaml` | 確定反映ファイルを追記 | |
| 2026-02-01 | edit | `README.md` | ネクストアクションを更新 | |
| 2026-06-08 | create | `skills/takeya-instagram-reel/SKILL.md` | スプレッドシート→台本生成→書き戻しの一連を Anthropic Skill 形式でパッケージ化 | 竹矢さんが自分で実行できるようにするため |
| 2026-06-08 | create | `skills/takeya-instagram-reel/scripts/extract_input.py` | 対象シートから input CSV を抽出 | スキル同梱の参照実装 |
| 2026-06-08 | create | `skills/takeya-instagram-reel/scripts/writeback.py` | output CSV からスプレッドシート batchUpdate ボディを生成 | スキル同梱の参照実装 |
| 2026-06-08 | edit | `ProjectIndex.yaml` | skill 関連ファイルを追記 | |