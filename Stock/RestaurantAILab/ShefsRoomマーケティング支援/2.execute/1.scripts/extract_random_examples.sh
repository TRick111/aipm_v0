#!/bin/bash

INPUT="1.scripts/examples.yaml"

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
  for (i=1; i<=3 && i<=n; i++) print blocks[order[i]]
}
' "$INPUT" 