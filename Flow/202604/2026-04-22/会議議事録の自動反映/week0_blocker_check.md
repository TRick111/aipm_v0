# Week 0 ブロッカー確認 結果 (BL-0063)

実施日: 2026-04-22
対象設計ドキュメント: omi_aios_integration_design.md
実施者: AIPM エージェント（Claude Opus 4.7）

---

## 1. Cockpit CLI 大容量 --instruction 検証

**結果: PASS**

### 実測条件
- 呼び出し形: `subprocess.run([...], shell=False, text=True)`（設計ドキュメント 99-115 行の `dispatch_to_cockpit()` と同一形）
- cockpit binary: `/Users/rikutanaka/.agi-tools/data/cockpit/master/cockpit`
- `--instruction` 長さ: **14,203 bytes (UTF-8)** — MasterIndex.yaml 全文 14,110 bytes + 検証トレーラー 93 bytes
- macOS ARG_MAX (1,048,576 bytes) の約 1.35%、十分に余裕あり
- `--directory /tmp --agent-type terminal --command "echo OK" --name "OMI Week0 arg-size test"`

### 出力
```
returncode = 0
stdout: {"ok":true,"data":{"id":"94ecbf03","name":"OMI Week0 arg-size test",
         "directory":"/tmp","instruction":"version: 1\n# MasterIndex.yaml（AI専用）...",
         "agentType":"terminal","status":"running","createdAt":"2026-04-22T..."}}
```
- `ok: true` / `taskId: 94ecbf03` を取得 → Cockpit が instruction 全文を保持した状態で task 生成成功
- instruction 内の日本語（YAML コメント・summary・keywords）も欠落なく保存確認
- 後処理として `./cockpit task complete 94ecbf03` を即実行しクリーンアップ済み（`{"ok":true,"data":{"id":"94ecbf03"}}`）

### 含意
- **Week 1 実装への影響なし**。`src/dispatcher.py::dispatch_to_cockpit()` は設計ドキュメント通り subprocess + list-form でそのまま進められる
- stdin 渡し・tempfile+`--instruction-file` のような代替設計は不要
- MasterIndex が将来 10〜100 倍に成長しても ARG_MAX には余裕があるが、`src/aios_context.py` の 50,000 字 truncate ガード（設計 206 行）は維持推奨
- 引用符エスケープは subprocess list-form で不要（設計 150 行の想定どおり）

---

## 2. OMI transcript サンプル取得

**ステータス: 田中さん手動アクションが必要（エージェントでは実施不可）**

理由: OMI のメモリデータは OMI Cloud / OMI アプリ内のプライベートデータで、
エージェントから API 経由での取得パスは未整備（これ自体が本 BL のゴール）。

### 田中さんへの依頼事項

以下を **Week 1 着手前** に 1 回だけ実施してください。

1. OMI アプリ（iPhone）または OMI ダッシュボード（<https://h.omi.me>）にサインイン
2. 過去に記録された「メモリ」を 1 件開き、**日本語の transcript テキスト**をコピー
   - 目安: 200 文字以上
   - 理想: 独り言・会話混在・句読点ゆらぎが含まれるもの
   - 秘匿情報を含む場合は伏字可（"○○" 等）。句読点と表記ゆらぎさえ残っていれば regex 設計に十分
3. コピーしたテキストを下記パスに保存
   - `~/aipm_v0/Flow/202604/2026-04-22/会議議事録の自動反映/omi_transcript_sample.txt`
4. 保存完了後、Cockpit タスク（本作業）に「サンプル保存完了」と返信

### サンプル取得後のエージェント側アクション
- `trigger.py` の regex を確定（設計 217-225 行のトリガー句セット「エージェント、」「OMIへ、」「タスク依頼。」「AIOSに、」を基準に、実サンプルの句読点／表記ゆらぎを吸収する形で最終化）
- サンプルを使った regex 単体テストを `tests/test_trigger.py` に同梱

### 補足（regex 未確定でも Week 1 着手可能か）
着手自体は可能だが、`trigger.py` の最終決定は **サンプル取得後** にずらす方が安全。
Week 1 スプリントでは以下の順で進められる:
1. pyproject / FastAPI skeleton / auth / idempotency / aios_context / dispatcher / prompt 先行実装
2. サンプル到着待機中は仮 regex（例: `^(エージェント|OMIへ|タスク依頼|AIOSに)[、。,]?`）で localhost E2E テスト
3. サンプル到着 → regex 確定 → 差し替え

---

## 3. Tailscale 使用状況

**インストール: yes**（想定外の発見。設計時点では未使用前提 → 見直し可）
**Funnel 可能: 要管理画面確認（技術的には可、ACL/HTTPS cert 未設定の可能性）**
**推奨: Tailscale Funnel（cloudflared より設計ドキュメントの想定構成に一致、インストール・アカウント追加が不要）**

### 実測

#### インストール状況
- `which tailscale` → not found（PATH 未通し）
- ただし `/Applications/Tailscale.app` が存在（App Store 版）
- 実バイナリ: `/Applications/Tailscale.app/Contents/MacOS/Tailscale` (version **1.96.2**, commit d916d86519, go1.26.1)
- Week 1 で CLI を常用するなら `sudo ln -s /Applications/Tailscale.app/Contents/MacOS/Tailscale /usr/local/bin/tailscale` 推奨（または Makefile 内で絶対パス参照）

#### tailnet 状態
```
ログインアカウント: auk1in1a1kart@gmail.com
tailnet (MagicDNS): tailad7d87.ts.net
Self node:
  - DNSName: rikus-mac-mini-3.tailad7d87.ts.net
  - HostName: Riku's Mac mini (3)
  - Tailscale IP: 100.105.5.39
  - OS: macOS
  - Status: active（現在ログイン中のこの Mac）

Peers:
  - 100.81.170.72   iphone-15        iOS     idle
  - 100.126.168.73  rikus-mac-mini   macOS   offline (182d)
  - 100.82.126.9    rikus-matebook   windows offline (2d)
```

#### Funnel / Serve
- `tailscale funnel status` → `No serve config`（=現時点で何もマップされていない、初期状態）
- `tailscale serve status` → `No serve config`
- Funnel コマンド自体は CLI に存在し、サブコマンド実行も可能
- 未解決: 管理画面（admin.tailscale.com）側で **Funnel が ACL で許可されているか**、および **HTTPS 証明書が有効化されているか** は CLI からは確認不可。実際に `tailscale funnel 443 http://localhost:8787` を試行するか、管理画面で確認するのが確実

### 含意（Tailscale Funnel vs cloudflared）

| 項目 | Tailscale Funnel | cloudflared |
|---|---|---|
| 追加インフラ | 不要（既存の tailnet を流用） | Cloudflare アカウント・`cloudflared` インストール必要 |
| エンドポイント URL | `https://rikus-mac-mini-3.tailad7d87.ts.net:443/omi/webhook` | `https://<random>.trycloudflare.com/omi/webhook` または独自ドメイン |
| 認証の追加層 | デフォルトでは公開（X-OMI-Secret 必須） | 同上（Cloudflare Access を噛ませれば 2 段にできる） |
| 管理画面設定 | ACL で Funnel 有効化 + HTTPS 証明書発行が必要 | Cloudflare 側の Zero Trust 設定 |
| 設計ドキュメント整合 | ◎ 192 行で想定済み | 229 行で fallback 扱い |

設計ドキュメント 192 行の想定どおり **Tailscale Funnel を第一候補**として進める。
Week 1 ステップ 3（外部公開）で実際に `tailscale funnel 443 http://localhost:8787` を実行、
ACL エラー／証明書エラーが出た場合は:
1. admin.tailscale.com の Access Controls で `funnel` 属性を付与
2. DNS > HTTPS Certificates を Enable
3. それでも解決しない場合に限り cloudflared へフォールバック

### 追加メモ（Mac mini の複数ノード）
- tailnet に `rikus-mac-mini` (offline 182d) と `rikus-mac-mini-3` (active) の 2 台が登録済み
- `rikus-mac-mini` は長期オフライン（古い Mac / 初期化時の残骸？）→ Week 1 時点で削除推奨（Funnel 発行 URL の曖昧性排除のため）
- omi-bridge は **`rikus-mac-mini-3`** 上で動作する前提

---

## 総合判定

**Week 1 着手可否: OK**（設計見直し不要）

### 根拠
| Week 0 検証項目 | 結果 | Week 1 への影響 |
|---|---|---|
| ① Cockpit `--instruction` 14KB 受理 | PASS (returncode 0, taskId 取得) | 設計通り subprocess list-form で進行可 |
| ② OMI transcript サンプル | 田中さん手動タスク（regex 確定のみ一時ブロック） | skeleton 実装は並行進行可 |
| ③ Tailscale 使用状況 | 想定外にインストール済み・active | 外部公開手段は Funnel 第一候補で確定（cloudflared 不要） |

### Week 1 着手順（推奨）
1. `~/code/omi-bridge/` を `git init` し、pyproject + skeleton を生成
2. `src/main.py` / `src/auth.py` / `src/idempotency.py` / `src/aios_context.py` / `src/dispatcher.py` / `src/prompt.py` 先行実装
3. **田中さんからの OMI transcript サンプル到着を待って** `src/trigger.py` を最終化
4. localhost E2E テスト（curl で POST）→ 生成物が `Flow/202604/2026-04-22/omi_inbox/` に着地することを確認
5. Tailscale Funnel で 443 → 8787 マップ（ACL / cert 未設定ならその場で admin console で有効化）
6. OMI アプリで webhook URL `https://rikus-mac-mini-3.tailad7d87.ts.net/omi/webhook` を登録

### 見直しが必要な点
**設計ドキュメント本体の変更は不要**。ただし Week 1 実装時に以下を README.md へ反映:
- Tailscale バイナリは `/Applications/Tailscale.app/Contents/MacOS/Tailscale` を絶対パス参照（Makefile 内）
- あるいは `make setup` で `/usr/local/bin/tailscale` への symlink を作成
- tailnet suffix（`tailad7d87.ts.net`）と MagicDNS ホスト名（`rikus-mac-mini-3`）を `.env.example` にコメントで記載

---

## 次のアクション（田中さん向け）

1. **OMI transcript サンプルの取得**（上記「2. 田中さんへの依頼事項」参照）
2. サンプル保存完了後、Cockpit タスク上で「サンプル保存完了」と返信 → このタスクを `complete`
3. 続けて `/codex` または本エージェントに「Week 1 着手」を依頼

以上、3 項目の結論は確定。Week 1 着手前の追加ブロッカーは無し。
