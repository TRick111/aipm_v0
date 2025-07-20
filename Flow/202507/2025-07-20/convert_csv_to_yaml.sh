#!/bin/bash

INPUT="Flow/202507/2025-07-20/input.csv"
OUTPUT="Flow/202507/2025-07-20/examples.yaml"

awk -F, -v OUTPUT="$OUTPUT" '
function yaml_escape(str) {
  gsub(/\"/, "\\\"", str)
  gsub(/\r/, "", str)
  gsub(/\n/, "\\n", str)
  return str
}
BEGIN {
  parts[1]="フック"; parts[2]="問題提起"; parts[3]="問題提起"; parts[4]="問題提起"; parts[5]="問題提起";
  parts[6]="問題拡張"; parts[7]="問題拡張"; parts[8]="問題拡張"; parts[9]="問題拡張";
  parts[10]="イントロ"; parts[11]="イントロ"; parts[12]="イントロ";
  parts[13]="解決"; parts[14]="解決"; parts[15]="解決"; parts[16]="解決";
  parts[17]="エンド";
  contents[1]="主張をはっきりさせた結論＋問題定義（極論でOK）";
  contents[2]="視聴者の感情を代弁";
  contents[3]="視聴者のやりがちな行動を代弁";
  contents[4]="それらを否定";
  contents[5]="その問題を放置するといずれ訪れる「最悪の未来」";
  contents[6]="コールドリーディングで掌握";
  contents[7]="あなたのニーズや悩みの理解してますよ";
  contents[8]="その裏側にある感情の代弁";
  contents[9]="寄り添いと突き放し";
  contents[10]="このあとへの興味付けを加える";
  contents[11]="比較を用いて伝える";
  contents[12]="例え話で伝える";
  contents[13]="正解を断定的に伝える";
  contents[14]="具体内容";
  contents[15]="解決策";
  contents[16]="見てる人の感情をなぞる";
  contents[17]="自分の主張を曖昧にせず簡潔に完結させる";
}
{
  if ($1 ~ /^ネタメモ/) {
    if (title != "") print "" >> OUTPUT
    title = $1
    gsub(/^ネタメモ：?/, "", title)
    print "- title: " title >> OUTPUT
    print "  sections:" >> OUTPUT
    next
  }
  if ($1 ~ /^[0-9]+$/ && length($2) > 0) {
    idx = $1 + 0
    lineval = $2
    for (i=3; i<=NF; i++) {
      if ($i != "") lineval = lineval "," $i
    }
    lineval = yaml_escape(lineval)
    print "    - part: " parts[idx] >> OUTPUT
    print "      content: (シーン" idx ") " contents[idx] >> OUTPUT
    print "      line: \"" lineval "\"" >> OUTPUT
  }
}
' "$INPUT"
