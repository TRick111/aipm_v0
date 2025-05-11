# setup_config.ps1
# ワークスペース構築スクリプト用のPowerShellコンフィグファイル例
#
# 使い方: コピーして編集後、.\setup_workspace_simple.ps1 [path] setup_config.ps1 を実行

# 自動確認をスキップする（$trueに設定すると確認なしで進行）
$AUTO_APPROVE = $true

# リポジトリを自動クローンする（$trueに設定すると確認なしでクローン）
$AUTO_CLONE = $true

# ルールリポジトリ
# 形式: "GitリポジトリURL|ターゲットパス"
$script:RULE_REPOS = @(
  'https://github.com/miyatti777/rules_basic_public.git|.cursor/rules/basic'
  # 必要に応じて追加
  # 'https://github.com/username/custom_rules.git|.cursor/rules/custom'
)

# スクリプトリポジトリ
$script:SCRIPT_REPOS = @(
  'https://github.com/miyatti777/scripts_public.git|scripts'
  # 必要に応じて追加
  # 'https://github.com/username/custom_scripts.git|scripts/custom'
)

# プログラムリポジトリ
$script:PROGRAM_REPOS = @(
  'https://github.com/miyatti777/sample_pj_curry.git|Stock/programs/夕食作り'
  # 必要に応じて追加
  # 'https://github.com/username/custom_program.git|Stock/programs/CUSTOM'
)

# 基本ディレクトリ構造
$script:BASE_DIRS = @(
  'Flow'
  'Stock'
  'Archived'
  'Archived/projects'
  'scripts'
  '.cursor/rules'
  '.cursor/rules/basic'
  'Stock/programs'
  # 必要に応じて追加
) 