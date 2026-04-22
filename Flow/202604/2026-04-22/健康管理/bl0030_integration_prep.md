# BL-0030 AIOS自動連携 — 事前準備設計書（Vercel + Apple Health 経由）

- 対象タスク: BL-0030（睡眠データのAIOS自動連携、4/30 必達）
- 親比較ドキュメント: `sleep_device_final_comparison.md`
- 作成日: 2026-04-22
- ステータス: **デバイス確定待ち**だが、3 つの確定済前提があるので**事前準備を前倒し**

---

## 1. 確定済の前提（INBOX.md より）

| 項目 | 確定値 | 影響 |
|---|---|---|
| iPhone 所有 | あり | Apple Health 経由ルートが取れる |
| Webhook 受け口 | **Vercel**（既存ダッシュボードと同 team） | Next.js Route Handler / Vercel Functions で受信 |
| Health Auto Export 課金 | **$24.99 買い切り許容** | 自動化機能が解放される |
| デバイス | **保留**（Venu vs Vivoactive 6 の判断待ち） | 後で確定。Apple Health 経由ルートはどちらでも同じ |

→ デバイスが Vivoactive 6 / Venu 4 のどちらに転んでも、AIOS 連携の実装は**完全に同じ**。ここで全部組んでおけば、デバイス到着翌日には連携が回る状態を作れる。

---

## 2. 全体アーキテクチャ

```
┌──────────────┐
│ Garmin デバイス │ （Vivoactive 6 / Venu 4）
└──────┬───────┘
       │ BLE 自動同期
       ▼
┌──────────────────────────┐
│ iPhone: Garmin Connect アプリ │
│   設定: Apple Health 連携 ON   │
└──────┬───────────────────┘
       │ HealthKit 書き込み
       ▼
┌──────────────────────┐
│ iPhone: Apple Health     │
│   - sleep_analysis      │
│   - heart_rate          │
│   - heart_rate_variability │
│   - active_energy ...   │
└──────┬───────────────┘
       │ 自動エクスポート（cron-like）
       ▼
┌────────────────────────────┐
│ iPhone: Health Auto Export   │
│   Automations: REST API POST │
└──────┬─────────────────────┘
       │ HTTPS POST (JSON)
       ▼
┌────────────────────────────────┐
│ Vercel: /api/webhook/sleep        │
│   - シークレット検証               │
│   - JSON パース                   │
│   - GitHub API で aipm_v0 に commit │
└──────┬─────────────────────────┘
       │ git commit (octokit)
       ▼
┌──────────────────────────────────────┐
│ aipm_v0 リポジトリ (GitHub)              │
│   Flow/YYYYMM/YYYY-MM-DD/健康管理/        │
│     _sleep_pull.md  ← 自動生成          │
└──────────────────────────────────────┘
       │ 日次レビュー時に Finalize（手動）
       ▼
┌────────────────────────────────────────┐
│ Stock/ゴール管理/健康管理/sleep_log/         │
│   YYYY-MM.md  ← 確定版                   │
└────────────────────────────────────────┘
```

---

## 3. iPhone 側セットアップ手順（デバイス到着後・約 15 分）

### 3.1 Garmin Connect → Apple Health 連携を有効化
1. **Garmin Connect** アプリを開く
2. 右下「More」→「Settings」→「Apple Health」
3. **Enable Data Sharing** を ON
4. iOS のヘルスケア App 側で、Garmin Connect からの書き込み権限を全許可
5. 推奨ON項目: **Sleep**, **Heart Rate**, **Heart Rate Variability**, **Active Energy**, **Steps**, **Workouts**

> **注意**: Garmin → Apple Health の連携は **steps / workouts / heart rate / sleep が中心**。**体温（skin temperature）は Apple Health に同期されない**（Garmin Connect アプリ内のみで参照）。Venu 4 を選んでも、AIOS パイプラインに体温は流れない（→ §6 のデバイス決定材料で詳述）。

### 3.2 Health Auto Export のインストールと購入
1. App Store で「**Health Auto Export - JSON+CSV**」を検索しインストール
2. 起動時の HealthKit 権限プロンプトで全許可
3. **Settings → Subscription** から **Premium Lifetime $24.99** を購入
4. 「**Automations**」タブを開く

### 3.3 Automation の作成
1. 「**+ New Automation**」
2. 設定:
   - **Name**: `AIOS Sleep Push`
   - **Type**: REST API
   - **URL**: `https://<vercel-app>.vercel.app/api/webhook/sleep`
   - **Method**: POST
   - **Headers**: `X-Webhook-Secret: <ランダム文字列>` ※後述の Vercel 環境変数と一致させる
   - **Frequency**: **Manual** で動作確認 → OK なら **Daily 8:00 AM**
   - **Aggregate Data**: ON、**Aggregate Interval**: Day
   - **Metrics（出力対象）**:
     - `sleep_analysis`（睡眠ステージ含む）
     - `heart_rate`
     - `heart_rate_variability`
     - `active_energy`
     - `step_count`
     - （任意）`resting_heart_rate`, `respiratory_rate`
3. **Test Now** で 1 回手動実行 → Vercel ログで受信を確認

---

## 4. Vercel 側実装

### 4.1 デプロイ方針

田中さんの指示: 「既存ダッシュボードと同 team」

- **Option A: 既存ダッシュボードプロジェクトに API Route を追加**（最小工数）
  - `app/api/webhook/sleep/route.ts` を 1 ファイル追加するだけ
  - 既存の Next.js App Router 設定をそのまま使える
- **Option B: 新規 Vercel プロジェクト `aios-webhook`**（責任分界明確）
  - シンプルな Next.js 14 App Router プロジェクトを新規作成
  - 既存ダッシュボードと疎結合
  - 失敗してもダッシュボードに影響なし

→ **推奨: Option B**。BL-0031（LINE連携）, BL-0026（OMI議事録）, 将来の AIOS 周辺 webhook 群もここに集約できる。

### 4.2 雛形コード（Next.js 15 App Router）

`app/api/webhook/sleep/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { Octokit } from "@octokit/rest";

export const runtime = "nodejs"; // octokit を使うため node ランタイム

const REPO_OWNER = "TRick111";       // GitHub username
const REPO_NAME = "aipm_v0";         // リポジトリ名
const BRANCH = "main";

export async function POST(req: NextRequest) {
  // 1. 認証
  const secret = req.headers.get("x-webhook-secret");
  if (secret !== process.env.WEBHOOK_SECRET) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  // 2. JSON パース
  let body: any;
  try {
    body = await req.json();
  } catch (e) {
    return NextResponse.json({ error: "invalid_json" }, { status: 400 });
  }

  // 3. ファイルパス決定（前日分を取り込む想定。実行時刻=朝なので date は今日）
  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const yyyymm = today.slice(0, 7).replace("-", "");
  const path = `Flow/${yyyymm}/${today}/健康管理/_sleep_pull.md`;

  // 4. Markdown 生成
  const md = renderSleepMarkdown(today, body);

  // 5. GitHub に commit
  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

  // 既存ファイル取得（あれば SHA を取って上書き、なければ新規作成）
  let sha: string | undefined;
  try {
    const existing = await octokit.repos.getContent({
      owner: REPO_OWNER, repo: REPO_NAME, path, ref: BRANCH,
    });
    if (!Array.isArray(existing.data) && "sha" in existing.data) {
      sha = existing.data.sha;
    }
  } catch (e: any) {
    if (e.status !== 404) throw e;
  }

  await octokit.repos.createOrUpdateFileContents({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    path,
    message: `chore(health): sleep auto-pull ${today}`,
    content: Buffer.from(md, "utf-8").toString("base64"),
    branch: BRANCH,
    sha,
  });

  return NextResponse.json({ status: "ok", path });
}

function renderSleepMarkdown(date: string, body: any): string {
  // Health Auto Export の payload は body.data.metrics 配列形式
  const metrics: any[] = body?.data?.metrics ?? [];
  const sleep = metrics.find((m) => m.name === "sleep_analysis");
  const hrv = metrics.find((m) => m.name === "heart_rate_variability");
  const hr = metrics.find((m) => m.name === "heart_rate");

  // sleep_analysis の data は時間帯ごとのレコード配列
  const sleepRecords = sleep?.data ?? [];

  // 簡易集計（実際の payload 仕様確認後に調整）
  const totalSec = sleepRecords.reduce((sum: number, r: any) => sum + (r.qty ?? 0), 0);
  const totalH = (totalSec / 3600).toFixed(2);

  return [
    `# 睡眠データ（自動取得） ${date}`,
    ``,
    `- 取得元: Garmin → Apple Health → Health Auto Export → Vercel`,
    `- 取得時刻: ${new Date().toISOString()}`,
    ``,
    `## 主要指標`,
    ``,
    `- 総睡眠時間: ${totalH} h`,
    `- HRV (avg): ${hrv?.data?.[0]?.qty ?? "n/a"}`,
    `- 心拍 (avg): ${hr?.data?.[0]?.qty ?? "n/a"}`,
    ``,
    `## 生データ（後で集計用）`,
    ``,
    "```json",
    JSON.stringify(body, null, 2),
    "```",
    ``,
  ].join("\n");
}
```

`package.json` 追加依存:

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@octokit/rest": "^21.0.0"
  }
}
```

### 4.3 環境変数（Vercel ダッシュボード or `vercel env`）

| キー | 値 | 取得方法 |
|---|---|---|
| `WEBHOOK_SECRET` | ランダム文字列（32 文字程度） | `openssl rand -hex 16` |
| `GITHUB_TOKEN` | GitHub Personal Access Token (fine-grained, repo scope = aipm_v0 read+write) | https://github.com/settings/personal-access-tokens |

### 4.4 デプロイ
```bash
# Option B: 新規プロジェクトの場合
mkdir aios-webhook && cd aios-webhook
npx create-next-app@latest . --typescript --app --no-tailwind --no-eslint
npm install @octokit/rest
# app/api/webhook/sleep/route.ts を上記のコードで作成
vercel link    # 既存 team に紐付け
vercel env add WEBHOOK_SECRET production
vercel env add GITHUB_TOKEN production
vercel --prod
```

---

## 5. データ保存先の選択肢

田中さんからの相談: 「DB候補: Neon? Notion? Supabase? とりあえず提案」

### 5.1 推奨: **A. GitHub Commit（DB なし）**

**理由**:
- AIOS は Markdown / YAML 中心の運用
- 既存 Flow → Stock の Finalize ワークフローにそのまま乗る
- DB セットアップ不要・追加コスト 0
- バージョン管理されるので過去データの遡及が容易
- 障害発生時のデバッグも `git log` で完結

**デメリット**:
- 集計ダッシュボードを後から作る場合は別途 SQL 化が必要
- GitHub API のレート制限（5000 req/h、認証済み）にぶつかる可能性は低い（日次 1 回 push なら全く問題なし）

### 5.2 サブの選択肢

| 選択肢 | 強み | 弱み | 推奨度 |
|---|---|---|---|
| **B. Vercel Postgres / Neon** | 構造化分析・SQL 集計・既存ダッシュボードと統合可 | DB スキーマ管理が必要、Free tier に制約 | ◎ 将来的に集計ダッシュボード化するなら最適 |
| **C. Vercel Blob** | 受信生データを丸ごと保存 | 集計用途には不向き | △ A のバックアップとしてはあり |
| **D. Vercel KV (Upstash Redis)** | 軽量、過去 N 日のキャッシュ向き | データ永続性は GitHub に劣る | △ サブとしてのみ |
| **E. Notion API** | 田中さんが普段使う場合は見やすい | API レート制限厳しめ、構造制約 | △ 田中さんの主たる作業環境次第 |
| **F. Supabase** | Auth / Realtime も使える | 単機能には過剰 | ✕ 今回不要 |

### 5.3 現実的な構成案

**フェーズ1（4/30 必達）**: A のみ（GitHub commit）
**フェーズ2（後日）**: 集計ダッシュボード化したくなったら B（Neon）を追加し、同じ Webhook で両方に書き込む

### 5.4 既存 RestaurantAILab ダッシュボードとの統合可能性

田中さんが Vercel を選んだ理由が「既存ダッシュボードと同 team」なら、将来的に **健康管理ダッシュボード**を同じプロジェクトに同居させる選択肢もあり。その場合は B（Neon）を採用してデータベース層を共通化するのが筋。

---

## 6. デバイス決定の判断材料追加 — 体温データの Apple Health 非同期問題

### 6.1 発見

調査の結果、**Garmin → Apple Health の同期項目は steps / workouts / heart rate / sleep が中心**で、**体温（skin temperature / wrist temperature）は Apple Health に同期されない**ことが判明（Garmin 公式サポート + 複数の連携ガイドで確認）。

### 6.2 これが意味すること

| | Vivoactive 6 | Venu 4 |
|---|---|---|
| 体温センサー | なし | あり |
| 体温データの Garmin Connect アプリ表示 | — | ◎ トレンド表示・ベースライン比較 |
| **体温データの Apple Health 同期** | — | **✕ 流れない** |
| **体温データの AIOS 取り込み** | — | **✕ 不可（Apple Health 経由では）** |

→ **Venu 4 を選んでも、体温データは AIOS パイプラインに乗らない**。Garmin Connect アプリ内で体温トレンドを「目で見る」ことはできるが、AIOS 側で体重・睡眠と並べて分析することはできない。

### 6.3 Venu 4 を選ぶ意義が残るケース

- **Garmin Connect アプリ内で体温を毎日チェックする**ことに価値を感じる
- **AMOLED 大画面 + 常時表示**を日常使いで重視する
- **体重 ¥40,000 の差額を「センサーの安心感・所有感」に払うのが許容**

逆に、**「AIOS にすべてのデータを集約したい」**が動機なら、体温センサーの差額¥40,000 はパイプライン上活かされない。

### 6.4 体温データを AIOS に流す回避策（参考）

Apple Health 経由ではダメだが、以下のルートなら可能:
- (1) Garmin Connect Web を Selenium/Playwright でスクレイピング → 体温セクションから取得
- (2) python-garminconnect が復旧したら API 経由で取得
- (3) Garmin の手動 JSON エクスポートに体温が含まれているなら月 1 で取り込み

ただしいずれも追加実装コストが大きく、4/30 期限の最小構成からは外れる。

---

## 7. 動作確認の手順（デバイス到着後）

| # | アクション | 確認方法 | 期待結果 |
|---|---|---|---|
| 1 | Garmin デバイスを充電 + 初期セットアップ | デバイス画面で確認 | Garmin Connect とペアリング完了 |
| 2 | 1 晩装着して睡眠計測 | 翌朝 Garmin Connect アプリ | 睡眠データ表示 |
| 3 | Garmin Connect → Apple Health 連携 ON | iOS ヘルスケア > 睡眠分析 | Garmin からのレコードが表示される |
| 4 | Health Auto Export で **Test Now** 実行 | Vercel ダッシュボード > Logs | POST 200 OK が記録される |
| 5 | aipm_v0 リポジトリを `git pull` | `Flow/YYYYMM/YYYY-MM-DD/健康管理/_sleep_pull.md` | ファイル生成・睡眠データ記載 |
| 6 | Health Auto Export を Daily 8:00 AM 自動化 | 翌日 ファイル生成確認 | 毎朝自動で commit が走る |
| 7 | BL-0030 完了報告 | 連続 2 日分のデータが Flow に蓄積 | DONE |

### 失敗時の切り分け
- **Vercel ログに何も来ない** → Health Auto Export の URL or ネットワーク問題
- **401** → `WEBHOOK_SECRET` 不一致
- **500** → `GITHUB_TOKEN` の権限不足 or リポジトリ名誤り
- **commit はされるが内容が空** → Health Auto Export の Aggregate 設定漏れ or Apple Health に Garmin データが流れていない

---

## 8. デバイス到着待ちの間にできること（着手可能タスク）

| # | タスク | 担当 | 工数 | ブロッカー |
|---|---|---|---|---|
| 1 | Vercel プロジェクト `aios-webhook` 作成（Option B） | 田中さん or AI | 30 分 | Vercel team へのアクセス |
| 2 | 上記 route.ts の実装と動作確認（mock JSON で POST） | AI | 2 時間 | プロジェクト作成済みであること |
| 3 | GitHub PAT 発行（aipm_v0 への repo:contents:write） | 田中さん | 5 分 | なし |
| 4 | `WEBHOOK_SECRET` 生成 + Vercel 環境変数登録 | 田中さん | 5 分 | プロジェクト作成済みであること |
| 5 | Health Auto Export の事前購入（$24.99） | 田中さん | 3 分 | iOS App Store ログイン |
| 6 | mock JSON で Vercel エンドポイントを叩く E2E テスト | AI | 30 分 | 1〜4 完了 |
| 7 | Stock/ゴール管理/健康管理/ に sleep_log/ ディレクトリと月次テンプレ準備 | AI | 30 分 | なし |

→ **デバイス到着前に 1〜7 を全部済ませておけば、到着翌日から自動連携が動く**。

---

## 9. 4/30 までの最小スケジュール（更新版）

| 日付 | アクション |
|---|---|
| 2026-04-22 | デバイス決定保留 / Vercel プロジェクト準備着手 |
| 2026-04-23〜25 | デバイス確定・発注・到着 |
| 2026-04-23〜25（並行） | Vercel webhook 実装 + mock テスト完了 |
| 2026-04-26 | Garmin 初期セットアップ + Apple Health 連携 ON |
| 2026-04-27 | Health Auto Export 設定 + Test Now で疎通確認 |
| 2026-04-28 | 1 晩計測 → 翌朝 Daily 自動化を有効化 |
| 2026-04-29 | 自動 commit 動作確認、BL-0029 記録運用開始 |
| 2026-04-30 | BL-0030 完了報告（2 日分のデータ蓄積） |

---

## 10. 主要ソース

- [Sharing Garmin Connect Data With Apple Health — Garmin Support](https://support.garmin.com/en-US/?faq=lK5FPB9iPF5PXFkIpFlFPA)
- [Garmin skin temperature feature — Garmin Support](https://support.garmin.com/en-US/?faq=RDXq6E5Iaq9rD1l1kTObf6)
- [Health Auto Export pricing](https://www.healthyapps.dev/health-auto-export-pricing)
- [Health Auto Export Automations](https://help.healthyapps.dev/en/health-auto-export/automations/)
- [Building API in Next.js — Vercel docs](https://nextjs.org/blog/building-apis-with-nextjs)
- [Octokit (GitHub REST API client) — GitHub](https://github.com/octokit/rest.js)
- [GitHub fine-grained PAT 設定 — GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
