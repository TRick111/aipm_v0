# Dify ワークフロー作成手順（Zoomトランスクリプト → 正規化 → 要約 → Google Drive 保存）

このドキュメントは、Zoomのトランスクリプトテキストを入力として、`stripvtt.sh` 相当の整形処理 → `merge_same_speaker.sh` 相当の連結処理 → AI要約 → Google DriveへMarkdownファイル保存までを、Dify（クラウド版）のワークフローで実現する手順です。

---

## 全体フロー（概要）
1. 入力（HTTP Trigger または 手動実行）: `transcript_text`（プレーンテキスト）
2. 正規化（Codeノード: Python）: VTT/SRTのタイムスタンプ・行番号除去（`stripvtt.sh` 相当）
3. 同一話者連結（Codeノード: Python）: 連続する同一話者の発話を1行に結合（`merge_same_speaker.sh` 相当）
4. 要約（LLMノード）: 観点別要約（クライアント提供/コンサル提案/決定事項/アクション）
5. Markdown整形（Template/Code）
6. Google Driveへ保存（HTTP Requestノード → Google Apps Script Web App）

---

## 事前準備
- Dify（クラウド版）でプロジェクトを作成
- Google Apps Script（Drive保存用のWeb App）を準備（後述）

---

## ノード設計（詳細）

### 0) トリガー
- 方式A: HTTP Trigger
  - 受け取るJSON例:
    ```json
    {
      "meeting_id": "123-456-789",
      "topic": "採用施策ブレスト",
      "transcript_text": "WEBVTT...\n00:00:01.000 --> 00:00:03.000\nAlice: ..."
    }
    ```
- 方式B: 手動実行（App/WorkflowのRun）
  - 入力フォームに `transcript_text`（貼り付け）と `topic` を用意

必須入力変数
- `transcript_text`（string）: Zoomから取得したトランスクリプト（VTT/SRT/プレーン）
- `topic`（string, 任意）: 会議名/用途

---

### 1) Code ノード（Python）: VTT/SRT 正規化（`stripvtt.sh` 相当）
目的: タイムスタンプや行番号、`WEBVTT` ヘッダを削除し、`話者名: 発話` のテキストへ整形する。

- 入力: `transcript_text`
- 出力: `normalized_text`
- サンプル（Pythonスニペット）:
  ```python
  import re

  def strip_vtt(vtt_text: str) -> str:
      # 1) ヘッダ除去
      text = re.sub(r'^\s*WEBVTT.*$', '', vtt_text, flags=re.MULTILINE)
      # 2) タイムスタンプ行除去
      text = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}.*$', '', text, flags=re.MULTILINE)
      # 3) 行番号のみの行除去
      text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
      # 4) 余計なホワイトスペース整形
      lines = [ln.strip() for ln in text.splitlines()]
      # 空行を詰めつつ、話者: 発話 の形式以外はそのまま残す
      lines = [ln for ln in lines if ln]
      return "\n".join(lines)

  normalized_text = strip_vtt(inputs["transcript_text"])  # DifyのCodeノード入力参照
  outputs["normalized_text"] = normalized_text
  ```

---

### 2) Code ノード（Python）: 同一話者の連結（`merge_same_speaker.sh` 相当）
目的: `Speaker: 発話` 形式を前提に、連続する同一話者を結合する。

- 入力: `normalized_text`
- 出力: `merged_text`
- サンプル（Pythonスニペット）:
  ```python
  import re

  speaker_line = re.compile(r'^(?P<spk>[^:：]+)\s*[:：]\s*(?P<utt>.+)$')

  def merge_same_speaker(text: str) -> str:
      merged = []
      last_speaker = None
      last_utter = []
      for line in text.splitlines():
          m = speaker_line.match(line)
          if m:
              spk = m.group('spk').strip()
              utt = m.group('utt').strip()
              if last_speaker == spk:
                  last_utter.append(utt)
              else:
                  if last_speaker is not None:
                      merged.append(f"{last_speaker}: {' '.join(last_utter)}")
                  last_speaker = spk
                  last_utter = [utt]
          else:
              # 話者ラベルが無い行はそのまま現在話者の発話として連結
              if last_speaker is None:
                  # 最初の行に話者が無い場合、Unknown扱い
                  last_speaker = "Unknown"
                  last_utter = [line.strip()]
              else:
                  last_utter.append(line.strip())
      if last_speaker is not None:
          merged.append(f"{last_speaker}: {' '.join(last_utter)}")
      return "\n".join(merged)

  merged_text = merge_same_speaker(inputs["normalized_text"])  # 直前ノードの出力
  outputs["merged_text"] = merged_text
  ```

---

### 3) LLM ノード: 観点別要約
目的: 指定テンプレに沿って、「クライアントから聞いた内容」「コンサルに伝えた内容」「決定事項」「アクションアイテム」を抽出しMarkdownで生成。

- 入力: `merged_text`, `topic`
- プロンプト例:
  ```
  あなたは議事録作成の専門家です。以下の会話ログから、指定フォーマットで要約を出力してください。
  - 主観は排除し、テキスト根拠に基づいて記載
  - 曖昧な点は「不明」と明記し、担当は可能な範囲で「推測：〇〇側」も付記

  入力:
  {{ merged_text }}

  出力フォーマット（Markdown）:
  ## クライアントから聞いた内容
  - ...
  
  ## クライアントに伝えた内容
  - ...
  
  ## ミーティング内で決定したこと
  - ...
  
  ## 今後のアクションアイテムと担当者
  - [タスク] — [担当者（確定/推測）] — [期限（あれば）]
  ```
- 出力: `minutes_md`

---

### 4) Markdown 整形（任意のTemplate/Code）
- 例: 先頭にタイトルやメタを付与
  ```python
  from datetime import datetime
  title = inputs.get("topic", "会議")
  now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
  md = f"# {title} 議事録\n\n生成時刻: {now}\n\n" + inputs["minutes_md"]
  outputs["minutes_final_md"] = md
  ```

---

## Google Drive 保存（Google Apps Script Web App 推奨）
Difyから直接Google Drive APIへ書き込むことも可能ですが、Apps ScriptのWeb Appを経由すると簡易です。

### A) Google Apps Script（Web App）
- スクリプト例（新規ファイル作成 / 指定フォルダに保存）:
  ```javascript
  function doPost(e) {
    const params = JSON.parse(e.postData.contents);
    const folderId = params.folderId; // 任意（無ければマイドライブ直下）
    const name = params.name || `minutes_${new Date().toISOString()}.md`;
    const content = params.content || '';

    const blob = Utilities.newBlob(content, 'text/markdown', name);
    let file;
    if (folderId) {
      const folder = DriveApp.getFolderById(folderId);
      file = folder.createFile(blob);
    } else {
      file = DriveApp.createFile(blob);
    }
    return ContentService.createTextOutput(JSON.stringify({
      fileId: file.getId(),
      url: file.getUrl(),
      name: file.getName()
    })).setMimeType(ContentService.MimeType.JSON);
  }
  ```
- デプロイ: 「デプロイ」→「新しいデプロイ」→種類: ウェブアプリ → アクセス: 全員（必要に応じて制限）
- 発行URLを控える（例: `https://script.google.com/.../exec`）

### B) Dify 側 HTTP Request ノード
- メソッド: POST
- URL: Web Appのexec URL
- ヘッダ: `Content-Type: application/json`
- ボディ例:
  ```json
  {
    "folderId": "<任意のフォルダID>",
    "name": "{{ topic }}_minutes.md",
    "content": "{{ minutes_final_md }}"
  }
  ```
- 出力: `drive_response`（`fileId`, `url` など）

---

## 代替: 直接 Google Drive API（サービスアカウント）
- サービスアカウント＋OAuth設定が必要。Apps Scriptに比べると初期設定の手間は増えるが、企業ポリシーに沿った統制が可能。
- DifyからHTTPリクエストで `files.create`（multipart/form-data）を呼び出す。

---

## テスト手順
1. サンプルのVTT/SRT/プレーンテキストを `transcript_text` に投入
2. ノードごとに出力を確認（`normalized_text` → `merged_text` → `minutes_md` → `minutes_final_md`）
3. Google Apps Script Web AppのURLを設定したHTTPノードを実行
4. DriveにMarkdownが生成され、URLが返ることを確認

---

## 備考
- `stripvtt.sh`/`merge_same_speaker.sh` はシェル環境依存のため、Difyでは上記Pythonロジックで同等機能を実現しています。
- 日本語話者名のコロンは「:」「：」双方に対応。
- 将来拡張: 話者 diarization の精緻化、箇条書き整形、Slack通知、Notion保存など。

