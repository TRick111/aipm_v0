import sys
import re

# 標準出力のエンコーディングを設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_markdown_file(file_path):
    """Markdownファイルの箇条書きフォーマットを修正"""
    print(f"修正対象: {file_path}")

    # ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # パターン1: ✅ **〜** の後に空行がない場合
    pattern1 = r'(✅ \*\*[^\n]+\*\*)\n(- )'
    replacement1 = r'\1\n\n\2'

    # パターン2: ⚠️ **〜** の後に空行がない場合
    pattern2 = r'(⚠️ \*\*[^\n]+\*\*)\n(- )'
    replacement2 = r'\1\n\n\2'

    # パターン3: 💡 **〜** の後に空行がない場合
    pattern3 = r'(💡 \*\*[^\n]+\*\*)\n(- )'
    replacement3 = r'\1\n\n\2'

    # 置換を実行
    content = re.sub(pattern1, replacement1, content)
    content = re.sub(pattern2, replacement2, content)
    content = re.sub(pattern3, replacement3, content)

    # 絵文字を太字の外に出す（✅ **text** → **✅ text**）
    content = re.sub(r'(✅|⚠️|💡) \*\*([^\*]+)\*\*', r'**\1 \2**', content)

    # ファイルに書き込む
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 修正完了: {file_path}")
    else:
        print(f"- 変更なし: {file_path}")

# W43のファイルを修正
fix_markdown_file(r'Stock\RestaurantAILab\週報\2_output\週報作成基礎資料.md')

print("\nすべてのファイルの修正が完了しました")
