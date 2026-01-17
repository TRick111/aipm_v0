#!/bin/bash

# VTTファイルのトランスクリプトをクリーンアップするスクリプト
# 使用方法: ./stripvtt.sh input.vtt [backup_suffix]

# 入力ファイルの確認
if [ $# -lt 1 ]; then
    echo "使用方法: $0 <入力VTTファイル> [バックアップサフィックス]"
    echo "例: $0 meeting.vtt .backup"
    echo "注意: 元のファイルが直接書き換えられます"
    exit 1
fi

input_file="$1"
backup_suffix="${2:-.backup}"

# 入力ファイルの存在確認
if [ ! -f "$input_file" ]; then
    echo "エラー: 入力ファイル '$input_file' が見つかりません。"
    exit 1
fi

# バックアップファイルを作成
backup_file="${input_file}${backup_suffix}"
cp "$input_file" "$backup_file"

echo "VTTファイルをクリーンアップ中: $input_file"
echo "バックアップファイル: $backup_file"

# VTTファイルをクリーンアップ
# 1. WEBVTTヘッダーを削除
# 2. 会話番号行を削除
# 3. タイムスタンプ行を削除
# 4. 空白行を削除
# 5. 話者名と発言内容のみを抽出

# より確実な方法でVTTファイルをクリーンアップ
# 一時ファイルを使用して段階的に処理
temp_file1=$(mktemp)
temp_file2=$(mktemp)

# 0. 改行コードをUnix形式に変換
tr -d '\r' < "$input_file" > "$temp_file1"

# 1. WEBVTTヘッダーを削除
grep -v "^WEBVTT$" "$temp_file1" > "$temp_file2"

# 2. 会話番号行を削除（数字のみの行）
grep -v "^[0-9][0-9]*$" "$temp_file2" > "$temp_file1"

# 3. タイムスタンプ行を削除
grep -v "^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9]$" "$temp_file1" > "$temp_file2"

# 4. 空白行を削除し、前後の空白を削除
sed '/^[[:space:]]*$/d' "$temp_file2" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' > "$temp_file1"

# 5. 元のファイルを書き換え
mv "$temp_file1" "$input_file"

# 一時ファイルを削除
rm -f "$temp_file2"

# 結果の確認
line_count=$(wc -l < "$input_file")
echo "クリーンアップ完了！"
echo "処理されたファイル: $input_file"
echo "行数: $line_count"

# 最初の10行をプレビュー表示
echo ""
echo "=== プレビュー（最初の10行） ==="
head -10 "$input_file"
echo ""

# ファイルサイズの確認
file_size=$(du -h "$input_file" | cut -f1)
echo "ファイルサイズ: $file_size"

echo "クリーンアップが完了しました。"
echo "元のファイルは $backup_file にバックアップされています。"