#!/bin/bash
#============================================================
# setup_workspace_simple.sh
# ─ AIプロジェクト管理ワークスペースの簡易構築スクリプト
# 
# 使い方: ./setup_workspace_simple.sh [root_directory] [config_file]
#         ./setup_workspace_simple.sh [config_file]
# 例:     ./setup_workspace_simple.sh /Users/username/new_workspace ./my_config.sh
#         ./setup_workspace_simple.sh setup_config.sh  # カレントディレクトリに作成
#
# 基本的なフォルダ構造を作成し、Flowに日付フォルダを作成します
# コンフィグファイルを指定すると、クローンするリポジトリをカスタマイズできます
#============================================================

set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# デフォルト設定
# これらの設定はコンフィグファイルでオーバーライドできます
setup_default_config() {
  # ルールリポジトリ
  RULE_REPOS=(
    "https://github.com/miyatti777/rules_basic_public.git|.cursor/rules/basic"
  )
  
  # スクリプトリポジトリ
  SCRIPT_REPOS=(
    "https://github.com/miyatti777/scripts.git|scripts_public"
  )
  
  # プログラムリポジトリ
  PROGRAM_REPOS=(
    "https://github.com/miyatti777/sample_pj_curry.git|Stock/programs/夕食作り"
  )
  
  # サンプルプログラムフォルダ（フォールバック用）
  SAMPLE_PROGRAMS=(
    "夕食作り"
  )
  
  # 基本ディレクトリ
  BASE_DIRS=(
    "Flow"
    "Stock"
    "Archived"
    "Archived/projects"
    "scripts"
    ".cursor/rules"
    ".cursor/rules/basic"
    "Stock/programs"
  )
  
  # AUTO_APPROVE：trueに設定すると確認メッセージをスキップ
  AUTO_APPROVE=false
  
  # AUTO_CLONE：trueに設定するとリポジトリを自動クローン
  AUTO_CLONE=false
}

# コンフィグファイルの読み込み
load_config() {
  local config_file="$1"
  
  if [ -f "$config_file" ]; then
    log_info "コンフィグファイルを読み込んでいます: $config_file"
    # shellcheck source=/dev/null
    source "$config_file"
    log_success "コンフィグファイルを読み込みました"
  else
    log_warning "指定されたコンフィグファイルが見つかりません: $config_file"
    log_info "デフォルト設定を使用します"
  fi
}

# リポジトリのクローン処理
clone_repository() {
  local url=$1
  local target=$2
  local full_path="$ROOT_DIR/$target"
  
  # ターゲットディレクトリが既に存在し、かつgitリポジトリである場合はpullのみ
  if [ -d "$full_path/.git" ]; then
    log_info "リポジトリは既に存在します: $target - 更新を試みます"
    (cd "$full_path" && git pull)
    log_success "リポジトリを更新しました: $target"
  else
    # ディレクトリが存在する場合は中身を確認
    if [ -d "$full_path" ]; then
      # 空のディレクトリでなければエラー
      if [ "$(ls -A "$full_path")" ]; then
        log_error "ターゲットディレクトリ '$full_path' は空ではありません。クローンできません。"
        return 1
      fi
      # 空のディレクトリなら削除してクローン
      rmdir "$full_path"
    fi
    
    # 親ディレクトリを作成
    mkdir -p "$(dirname "$full_path")"
    
    # リポジトリをクローン
    log_info "リポジトリをクローンしています: $url -> $target"
    git clone "$url" "$full_path"
    if [ $? -eq 0 ]; then
      log_success "リポジトリをクローンしました: $target"
    else
      log_error "リポジトリのクローンに失敗しました: $url"
      return 1
    fi
  fi
}

# リポジトリのクローン
clone_repositories() {
  log_info "リポジトリをクローンしています..."
  
  # git が必要
  if ! command -v git &> /dev/null; then
    log_warning "git がインストールされていません。リポジトリクローンをスキップします。"
    return 1
  fi
  
  # AUTO_CLONEがfalseの場合は確認
  local clone_confirm="y"
  if [ "$AUTO_CLONE" != "true" ]; then
    read -p "リポジトリをクローンしますか？ (y/n): " clone_confirm
    if [[ "$clone_confirm" != [yY] ]]; then
      log_info "リポジトリのクローンはスキップされました"
      return 0
    fi
  else
    log_info "AUTO_CLONE=true が設定されているため、すべてのリポジトリを自動クローンします"
  fi
  
  # ルールリポジトリ
  if [ ${#RULE_REPOS[@]} -gt 0 ]; then
    log_info "ルールリポジトリをクローンしています..."
    for repo_entry in "${RULE_REPOS[@]}"; do
      url=$(echo "$repo_entry" | cut -d'|' -f1)
      target=$(echo "$repo_entry" | cut -d'|' -f2)
      clone_repository "$url" "$target"
    done
  else
    log_info "ルールリポジトリの指定がないためスキップします"
  fi
  
  # スクリプトリポジトリ
  if [ ${#SCRIPT_REPOS[@]} -gt 0 ]; then
    log_info "スクリプトリポジトリをクローンしています..."
    for repo_entry in "${SCRIPT_REPOS[@]}"; do
      url=$(echo "$repo_entry" | cut -d'|' -f1)
      target=$(echo "$repo_entry" | cut -d'|' -f2)
      clone_repository "$url" "$target"
    done
  else
    log_info "スクリプトリポジトリの指定がないためスキップします"
  fi
  
  # プログラムリポジトリ
  if [ ${#PROGRAM_REPOS[@]} -gt 0 ]; then
    log_info "プログラムリポジトリをクローンしています..."
    for repo_entry in "${PROGRAM_REPOS[@]}"; do
      url=$(echo "$repo_entry" | cut -d'|' -f1)
      target=$(echo "$repo_entry" | cut -d'|' -f2)
      
      # AUTO_CLONEがtrueでない場合は各リポジトリごとに確認
      local repo_confirm="y"
      if [ "$AUTO_CLONE" != "true" ]; then
        read -p "$url をクローンしますか？ (y/n): " repo_confirm
      fi
      
      if [[ "$repo_confirm" == [yY] || "$AUTO_CLONE" == "true" ]]; then
        clone_repository "$url" "$target" || log_warning "リポジトリ $url のクローンに問題が発生しましたが、処理は継続します"
      else
        log_info "リポジトリはスキップされました: $url"
      fi
    done
  else
    log_info "プログラムリポジトリの指定がないためスキップします"
  fi
  
  log_success "リポジトリのクローンが完了しました"
}

# フォールバックのディレクトリ作成
create_fallback_directories() {
  log_info "追加のディレクトリを作成しています..."
  
  # 共通ナレッジ領域作成
  if [ ! -d "$ROOT_DIR/Stock/programs/Common/Public" ]; then
    mkdir -p "$ROOT_DIR/Stock/programs/Common/Public"
    log_info "共通ナレッジディレクトリ作成: Stock/programs/Common/Public"
  fi
  
  # サンプルプログラムフォルダの作成（クローンが失敗または選択されなかった場合のフォールバック）
  for prog in "${SAMPLE_PROGRAMS[@]}"; do
    if [ ! -d "$ROOT_DIR/Stock/programs/$prog" ]; then
      mkdir -p "$ROOT_DIR/Stock/programs/$prog"
      log_info "プログラムディレクトリ作成: Stock/programs/$prog"
    fi
  done
}

# VSCodeの設定を更新
setup_vscode_settings() {
  log_info "VSCode設定を更新しています..."
  
  # .vscode ディレクトリ作成
  mkdir -p "$ROOT_DIR/.vscode"
  
  # settings.json のパス
  SETTINGS_JSON="$ROOT_DIR/.vscode/settings.json"
  
  # 設定データ
  MARP_THEMES_SETTING='{
  "markdown.marp.themes": [
    ".cursor/rules/basic/templates/marp-themes/explaza.css",
    ".cursor/rules/basic/templates/marp-themes/modern-brown.css"
  ]
}'
  
  # settings.json が存在するか確認
  if [ -f "$SETTINGS_JSON" ]; then
    log_info "既存のsettings.jsonを更新します"
    
    # すでに markdown.marp.themes 設定が含まれているか確認
    if grep -q "markdown.marp.themes" "$SETTINGS_JSON"; then
      log_info "markdown.marp.themes の設定はすでに存在します。スキップします。"
    else
      # JSON 形式を保持しながら設定を追加
      # 最後の閉じ括弧を一時的に削除し、設定を追加してから閉じ括弧を戻す
      sed -i.bak '$ s/}$/,/' "$SETTINGS_JSON"
      sed -i.bak '$ s/,$//' "$SETTINGS_JSON"  # 末尾のカンマを削除
      echo "$MARP_THEMES_SETTING" | sed 's/^{//' | sed 's/}$//' >> "$SETTINGS_JSON"
      echo "}" >> "$SETTINGS_JSON"
      rm -f "$SETTINGS_JSON.bak"
      log_success "settings.jsonにマープテーマ設定を追加しました"
    fi
  else
    # 新規作成
    echo "$MARP_THEMES_SETTING" > "$SETTINGS_JSON"
    log_success "settings.jsonを新規作成しました"
  fi
}

# マープテーマCSSの背景画像パスを更新
update_marp_theme_paths() {
  log_info "マープテーマのパスを更新しています..."
  
  # テーマディレクトリ
  THEME_DIR="$ROOT_DIR/.cursor/rules/basic/templates/marp-themes"
  
  # テーマディレクトリが存在するか確認
  if [ ! -d "$THEME_DIR" ]; then
    log_warning "テーマディレクトリが見つかりません: $THEME_DIR"
    return 1
  fi
  
  # 新しい絶対パス
  NEW_PATH="$ROOT_DIR/.cursor/rules/basic/templates/marp-themes/assets"
  
  # CSSファイルのパスを更新
  log_info "CSSファイル内の背景画像パスを更新中..."
  for css_file in "$THEME_DIR"/*.css; do
    if [ -f "$css_file" ]; then
      # 背景画像の絶対パスを検索して置換
      sed -i.bak "s|background-image: url(\"[^\"]*assets/|background-image: url(\"$NEW_PATH/|g" "$css_file"
      rm -f "${css_file}.bak"
      log_info "更新: $css_file"
    fi
  done
  
  log_success "マープテーマの背景画像パスを更新しました"
}

# メイン処理
main() {
  echo "============================================================"
  echo "     AIプロジェクト管理ワークスペース簡易構築スクリプト"
  echo "============================================================"
  
  # 引数の処理を柔軟にする
  # 引数が1つだけの場合、それがconfig_fileかどうかを判断
  if [ $# -eq 1 ] && [[ "$1" == *".sh" ]]; then
    ROOT_DIR="./"
    CONFIG_FILE="$1"
  else
    # 通常の引数処理（以前と同じ）
    ROOT_DIR="${1:-./}"
    CONFIG_FILE="${2:-./setup_config.sh}"
  fi
  
  # デフォルト設定をロード
  setup_default_config
  
  # コンフィグファイルをロード（指定されていれば）
  if [ -n "$CONFIG_FILE" ]; then
    load_config "$CONFIG_FILE"
  fi
  
  # 絶対パスに変換（ディレクトリが存在しなくてもパスを解決できるように）
  if [[ "$ROOT_DIR" = /* ]]; then
    # 既に絶対パスの場合はそのまま
    :
  else
    # 相対パスの場合は現在のディレクトリからの絶対パスに変換
    ROOT_DIR="$(pwd)/$ROOT_DIR"
  fi
  
  log_info "ワークスペースのルートディレクトリ: $ROOT_DIR"
  log_info "使用するコンフィグファイル: $CONFIG_FILE"
  
  # 確認メッセージ（AUTO_APPROVEがtrueの場合はスキップ）
  if [ "$AUTO_APPROVE" != "true" ]; then
    read -p "この場所にワークスペースを作成してよろしいですか？ (y/n): " confirm
    if [[ "$confirm" != [yY] ]]; then
      log_info "キャンセルされました"
      exit 0
    fi
  else
    log_info "AUTO_APPROVE=true が設定されているため、確認をスキップします"
  fi
  
  # ルートディレクトリ作成
  mkdir -p "$ROOT_DIR"
  
  log_info "基本ディレクトリ構造を作成しています..."
  
  # ディレクトリ作成
  for dir in "${BASE_DIRS[@]}"; do
    mkdir -p "$ROOT_DIR/$dir"
    log_info "ディレクトリ作成: $dir"
  done
  
  # 日付フォルダ作成
  log_info "Flow 内に日付フォルダを作成しています..."
  TODAY=$(date +"%Y-%m-%d")
  YEAR_MONTH=$(date +"%Y%m")
  FLOW_DATE_DIR="$ROOT_DIR/Flow/$YEAR_MONTH/$TODAY"
  mkdir -p "$FLOW_DATE_DIR"
  log_info "日付フォルダ作成: Flow/$YEAR_MONTH/$TODAY"
  
  # リポジトリのクローン（先に行う）
  clone_repositories
  
  # クローンされなかったディレクトリをフォールバックとして作成
  create_fallback_directories
  
  # VSCode設定を更新
  setup_vscode_settings
  
  # マープテーマのパスを更新
  update_marp_theme_paths
  
  # 完了メッセージ
  log_success "ワークスペースの構築が完了しました: $ROOT_DIR"
  echo "============================================================"
  echo "完了しました！新しいワークスペースが構築されました。"
  echo "ディレクトリ: $ROOT_DIR"
  echo "============================================================"
}

# スクリプト実行
main "$@" 