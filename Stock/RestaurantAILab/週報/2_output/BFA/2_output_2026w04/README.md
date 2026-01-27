# 2_output_2026w04（BFA）

このフォルダは週報（2026w04）の出力置き場です。

## Gitに反映されない理由
- Gitは **空ディレクトリを追跡しません**
- このフォルダの主な成果物は **`.png`** で、リポジトリの `.gitignore` に `*.png` があるため、PNGは追跡対象外です  
  → その結果、このフォルダはGit視点で「空」と同等になり、リモートに出ません

## PNGもGitで管理したい場合
`.gitignore` に例外ルールを追加してください（例）:

```gitignore
!Stock/RestaurantAILab/週報/2_output/BFA/2_output_2026w04/*.png
```

