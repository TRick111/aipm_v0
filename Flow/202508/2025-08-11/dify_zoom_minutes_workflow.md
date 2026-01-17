# Dify × Zoom 自動議事録ワークフロー設計（ドラフト）

## 全体像（結論）
- 推奨は「URL または オブジェクトストレージの署名付きURL」をDifyに渡す方式。
  - 理由: Zoomの自動録音/自動トランスクリプトはクラウド上に保存されるため、サイズ制限・API制限を考慮するとDifyに直接ファイルをアップロードするより、URLで参照→Dify側で取得・処理が安定。
  - オンプレ/ローカルでしか保持しない場合のみ、ファイル添付（Drive/Vectorに投入）の運用を検討。

## トリガー
- Zoom会議終了 → Zoom Webhook: `meeting.ended` / `recording.completed` / `transcript.completed`
  - 収録運用なら `recording.completed` が扱いやすい
  - 字幕/文字起こしを使うなら `transcript.completed` が最短

## 取得パターン
1) Zoom Cloud録画＋Zoom Transcripts
   - Webhookペイロード → recording_files のdownload_url / transcript_file を受領
   - 受領URLは有効期限付き。サーバ（もしくは中継のCloud Functions）で短期保存 or 署名付きURLに再発行
2) Zoom Cloud録画＋外部STT（例: Whisper API）
   - 音声トラック(M4A/MP4)のdownload_urlを取得 → 中継で音声抽出 → STT → Difyへ文字列/URL渡し
3) Zoom ローカル録画
   - Zoomクライアント終了後、ローカルに.vtt/.m4a生成 → 自動アップロード（S3/GCS/Drive） → 署名付きURL発行 → DifyにURL渡し

## Dify でのフロー（おすすめ構成）
- Flow: Orchestrator（HTTPトリガー受信）
  1. 入力: `meeting_id`, `topic`, `start_time`, `end_time`, `transcript_url`（または`audio_url`）
  2. ツール: HTTP Request ノードで `transcript_url` からデータ取得
  3. 前処理: 文字化け/話者タグ正規化（VTT/SRT→プレーンテキスト）
  4. LLM ノード: 要約・章立て・決定事項抽出・アクションアイテム抽出（プロンプトに観点定義）
  5. 追加: 役割推定/担当割当（規則ベース）
  6. 出力: Markdown整形 + 保存（外部ストレージ or GitHub/Notion/Google Docs）

- App（Chatflow/Workflow）: ユーザー確認・再生成
  - 入力: 会議タイトル、対象プロジェクト、体裁テンプレ（md）
  - 出力: 確定版議事録（MD）

## データ受け渡し方式の比較
- URL渡し（推奨）
  - Pros: DifyのHTTP取得が容易、サイズ制限回避、非同期処理に強い
  - Cons: URL期限/認可の管理が必要
- ファイル直接渡し
  - Pros: 閉域/ローカル完結
  - Cons: Difyの入力サイズ制約、アップロード導線の整備が必要、Zoomクラウドとの親和性は低め

## セキュリティ
- Zoomのdownload_urlは期限付きトークン。即時に中継サーバでS3/GCSへ再保管し、`signed URL (短命)` を発行してDifyに渡す
- PII対策: 前処理で固有名詞の疑似匿名化フィルタをオプション化

## 参考API/イベント
- Zoom Webhook: meeting.ended / recording.completed / transcript.completed
- Zoom API: Get meeting recordings, Get transcript file
- 中継: Cloud Run/Functions, or GitHub Actions（cron/dispatch）

## 疑似シーケンス
1. Zoom → Webhook（recording.completed）
2. 中継サーバ: recording/transcriptのURLを取得→ストレージへ保存→署名付きURL生成
3. 中継サーバ → Dify Flow（HTTP Trigger）にPOST
   - body: { meeting_id, topic, start_time, end_time, transcript_url }
4. Dify Flow: URLからVTT/SRT/JSONを取得→正規化→要約/抽出→Markdown生成
5. Dify Flow: 保存先へPUT（GitHub/Notion/GDrive）→結果URLを返却

## Dify HTTP Trigger 例（リクエストJSON）
```json
{
  "meeting_id": "123-456-789",
  "topic": "採用施策ブレスト",
  "start_time": "2025-08-11T10:00:00Z",
  "end_time": "2025-08-11T11:00:00Z",
  "transcript_url": "https://signed.example.com/zoom/abc.vtt?token=...",
  "project": "RestaurantAILab/ChefsRoom"
}
```

## Dify プロンプト要点（抜粋）
- 入力: 正規化済みトランスクリプト
- タスク: 
  - 「クライアントから聞いた内容」「コンサルが伝えた内容」「決定事項」「アクションアイテム」を抽出
  - あいまい語は「不明」と明記しつつ担当は推測表記
- 出力: 指定Markdownテンプレートに整形

## 保存・通知
- 保存先: GitHub（PR作成）/ Notion DB / Google Drive（フォルダ日付分け）
- 通知: Slack/メールに結果URLを送信

## 実装メモ
- VTT→テキスト変換は中継で実施してサイズ削減（行番号/タイムスタンプ除去、話者名保持）
- 将来拡張: 音声から再文字起こし（Whisper）による補完、用語辞書の適用、日英混在対策

