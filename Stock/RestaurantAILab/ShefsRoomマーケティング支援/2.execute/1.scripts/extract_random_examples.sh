#!/bin/bash

INPUT="/Users/rikutanaka/Documents/aipm_v0/Stock/RestaurantAILab/ShefsRoomマーケティング支援/2.execute/1.scripts/examples.yaml"

awk '
/^- title:/ {
  if (block) {
    blocks[++n] = block
    block = ""
  }
}
{ block = block $0 ORS }
END {
  if (block) blocks[++n] = block
  srand()
  for (i=1; i<=n; i++) order[i]=i
  for (i=n; i>1; i--) {
    j = int(rand()*i)+1
    tmp=order[i]; order[i]=order[j]; order[j]=tmp
  }
  for (i=1; i<=10 && i<=n; i++) print blocks[order[i]]
}
' "$INPUT" 