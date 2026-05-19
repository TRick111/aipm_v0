#!/usr/bin/env python3
"""202603 HTML から インバウンド比率スライドを削除し、slide-N を連番に詰める。
さらに PL関連スライドの分類条件帯（青帯）に家賃補完・初期費用除外の注釈を追記する。
"""
import re
from pathlib import Path

HTML = Path("/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-18/BFA/月報_202603/202603_BFA_月次報告資料.html")

src = HTML.read_text(encoding="utf-8")

# 1) インバウンド比率スライドを丸ごと削除
#    開始: <div class="slide" id="slide-N"> でタイトルに "客層分析①：インバウンド比率"
#    終了: 次の <div class="slide" id="slide-M"> の直前 (\n\n を含めて削除)
SLIDE_OPEN_RE = re.compile(r'<div class="slide(?:\s+[^"]+)?" id="slide-(\d+)">')
slide_starts = [(m.start(), m.group(0), int(m.group(1))) for m in SLIDE_OPEN_RE.finditer(src)]

target_idx = None
for i, (pos, tag, n) in enumerate(slide_starts):
    # 各スライドの末尾 = 次のスライドの開始
    end = slide_starts[i+1][0] if i+1 < len(slide_starts) else len(src)
    body = src[pos:end]
    if "客層分析①：インバウンド比率" in body:
        target_idx = i
        target_pos, target_end = pos, end
        break

if target_idx is None:
    raise SystemExit("inbound slide not found")

print(f"removing slide-{slide_starts[target_idx][2]} at [{target_pos}, {target_end})")
src2 = src[:target_pos] + src[target_end:]

# 余分な \n\n を整える
src2 = re.sub(r"\n\n\n+", "\n\n", src2)

# 2) slide-N を出現順に 1..N へ連番化
counter = {"n": 0}
def repl(m):
    counter["n"] += 1
    # クラス部分は保持して id だけ書き換える
    full = m.group(0)
    return re.sub(r'id="slide-\d+"', f'id="slide-{counter["n"]}"', full)

src3 = re.sub(r'<div class="slide(?:\s+[^"]+)?" id="slide-\d+">', repl, src2)
n_slides_after = counter["n"]

# 3) PL関連スライドの分類条件帯（青帯 = slide-classification）の <ul> 末尾に注釈 <li> を追加
ANNOTATION_LI = (
    '<li><b>注釈:</b> 家賃 ¥1,112,859 は【BFA】運営管理 / 新PL管理シート上では¥0だが、'
    '1-2月と同額（運用上の固定費）として補完表示。'
    '初期費用 ¥950,000（撮影/試作費等）は PL から除外（一過性費用）。</li>'
)

# スライド単位で走査
slide_open_positions = [m.start() for m in re.finditer(r'<div class="slide(?:\s+[^"]+)?" id="slide-\d+">', src3)]
slide_open_positions.append(len(src3))

new_parts = []
last = 0
added_count = 0
for i in range(len(slide_open_positions) - 1):
    s_start = slide_open_positions[i]
    s_end = slide_open_positions[i+1]
    new_parts.append(src3[last:s_start])
    body = src3[s_start:s_end]
    title_m = re.search(r'<div class="h-title">([^<]*)</div>', body)
    title = title_m.group(1) if title_m else ""
    if any(k in title for k in ["PL", "営業利益", "コスト構造", "費用構造", "損益", "P&L", "経費", "費用推移"]):
        # slide-classification の最初の <ul>...</ul> 内の </ul> の直前に注釈を1個だけ追加
        new_body, n = re.subn(
            r'(<div class="slide-classification">(?:(?!</div>).)*?<ul>(?:(?!</ul>).)*?)(</ul>)',
            r"\1" + ANNOTATION_LI + r"\2",
            body,
            count=1,
            flags=re.DOTALL,
        )
        if n > 0:
            added_count += 1
            body = new_body
        else:
            print(f"  [warn] PL slide '{title}' has no slide-classification ul")
    new_parts.append(body)
    last = s_end

new_parts.append(src3[last:])
src4 = "".join(new_parts)

# 書き出し
HTML.write_text(src4, encoding="utf-8")

print(f"✓ wrote {HTML}")
print(f"  size: {len(src4):,} bytes")
print(f"  slide count after: {n_slides_after}")
print(f"  PL slides annotated: {added_count}")
print(f"  annotation occurrences: {src4.count(ANNOTATION_LI)}")
