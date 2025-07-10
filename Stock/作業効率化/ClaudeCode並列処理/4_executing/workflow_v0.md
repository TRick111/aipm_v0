```bash
#!/bin/bash


SESSION="cc-company"

MANAGER_FIXED=$'あなたは【マネージャーClaude】です。\nあなたの仕事は、Child1とChild2に対して役割とタスクを設計し、tmux send-keys を使ってそれぞれに指示を出し、進捗を [REPORT] 形式で受け取り、必要なフィードバックを返すことです。\n\n指示形式：\n  tmux send-keys -t cc-company:dev.1 "[TASK] <Child1のタスク>" && sleep 0.1 && tmux send-keys -t cc-company:dev.1 Enter\n  tmux send-keys -t cc-company:dev.2 "[TASK] <Child2のタスク>" && sleep 0.1 && tmux send-keys -t cc-company:dev.2 Enter\n\nChild から返ってくる [REPORT] は自動でこの画面に流れます。\nすべての作業が完了したら、ALL_DONE と発言してください。'

# 🧩 可変部分（プロジェクトごとのタスク依頼内容）
MANAGER_DYNAMIC=$' 今回のあなたへの依頼内容は ローカルで動作するOCRのWebアプリの作成です。ローカルで、パソコンのローカルで動作するOCRのライブラリを使って、文字の読み取りを行うアプリをNext.jsで構築してください。'

MANAGER_MESSAGE="$MANAGER_FIXED"$'\n\n'"$MANAGER_DYNAMIC"

CHILD1_ROLE=$'あなたは【Child1／フロントエンド担当】Claudeです。\nマネージャーからの [TASK] を受けて作業を開始してください。\n進捗は [REPORT from Child1] <IN_PROGRESS|DONE|BLOCKED> <概要> の形式で報告してください。マネージャーへの報告は次のようにしてマネージャーに報告してください：tmux send-keys -t cc-company:dev.0 "[REPORT from Child1] <内容>" && sleep 0.1 && tmux send-keys -t cc-company:dev.0 Enter\n了解なら READY。'

CHILD2_ROLE=$'あなたは【Child2／バックエンド担当】Claudeです。\nマネージャーからの [TASK] を受けて作業を開始してください。\n進捗は [REPORT from Child2] <IN_PROGRESS|DONE|BLOCKED> <概要> の形式で報告してください。マネージャーへの報告は次のようにしてマネージャーに報告してください：tmux send-keys -t cc-company:dev.0 "[REPORT from Child2] <内容>" && sleep 0.1 && tmux send-keys -t cc-company:dev.0 Enter\n了解なら READY。'

# セッション開始 & ペイン作成
tmux new-session -d -s "$SESSION" -n dev
tmux split-window -h -t "$SESSION":dev
tmux split-window -v -t "$SESSION":dev.1
tmux select-layout -t "$SESSION":dev tiled

# Claude Code 起動
for P in 0 1 2; do
  tmux send-keys -t "$SESSION":dev.$P 'claude --dangerously-skip-permissions' && sleep 0.1 && tmux send-keys -t "$SESSION":dev.$P Enter
done

# Claude の起動完了を待つ
sleep 4

# Child1: 役割説明
tmux send-keys -t "$SESSION":dev.1 "$CHILD1_ROLE" && sleep 0.1 && tmux send-keys -t "$SESSION":dev.1 Enter

# Child2: 役割説明
tmux send-keys -t "$SESSION":dev.2 "$CHILD2_ROLE" && sleep 0.1 && tmux send-keys -t "$SESSION":dev.2 Enter

# 応答待ち
sleep 5

# マネージャーに固定＋可変の指示をまとめて送る
tmux send-keys -t "$SESSION":dev.0 "$MANAGER_MESSAGE" && sleep 0.1 && tmux send-keys -t "$SESSION":dev.0 Enter

# 子ペインのレポートをマネージャーペインに転送
for P in 1 2; do
  tmux pipe-pane -o -t "$SESSION":dev.$P \
    "grep --line-buffered '^\\[REPORT\\]' | while read -r L; do tmux send-keys -t $SESSION:dev.0 \"\$L\" C-m; done"
done

# セッション表示
tmux attach -t "$SESSION"

```
