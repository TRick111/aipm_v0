# 睡眠計測デバイス最終比較 — Garmin Venu 4 vs Vivoactive 6（Oura は参考）

- 対象タスク: BL-0028（睡眠計測デバイスの購入）
- 後続: BL-0029（記録運用、4/30）/ BL-0030（AIOS自動連携、4/30）
- 作成日: 2026-04-22
- 過程記録: `sleep_device_comparison.md`、`api_integration_notes.md`、`questions_to_user.md`
- **このファイルだけ読めば最終判断ができる**ことを目指す

---

## 1. 前提（ユーザー回答サマリ）

田中さんが `questions_to_user.md` で示した方針:

- **Q1=A** 自動連携は必達。**ただし API に固執せず、RPA / ブラウザ自動化も含めて検討したい**
- **Q2** Oura のサブスク（年¥11,800）が嫌で **Oura は除外**
- **Q3=A** 24 時間装着したい
- **Q6** 優先軸: **コスト > 連携 > 精度**

→ 候補は **Garmin Venu 4** と **Garmin Vivoactive 6** の 2 機種に絞る。連携手段は API 以外（Apple Health 経由 / RPA）で組み立てる。

---

## 2. 最終比較表（3 機種横並び）

| 観点 | **Garmin Vivoactive 6** ★候補A | **Garmin Venu 4 (45mm)** ★候補B | Oura Ring 4（参考・除外） |
|---|---|---|---|
| **本体価格（日本・税込）** | **¥39,800** | ¥79,800 | ¥52,800〜 |
| **5 年トータルコスト** ※1 | **¥49,800** | ¥89,800 | ¥131,800（本体+サブスク+交換） |
| **サブスク有無** | なし | なし | 年 ¥11,800（実質必須） |
| **バッテリー寿命（一回充電）** | 約 11 日 | 約 12 日 | 約 5〜8 日 |
| **本体寿命の目安** | 5〜7 年（バッテリー交換可） | 5〜7 年（バッテリー交換可） | 3〜4 年（バッテリー = 本体寿命） |
| **バッテリー交換** | 公式 ¥7,500〜12,000 | 同左（接着シール式で水没リスクあり） | ユーザー不可、Oura公式が交換サービス（料金非公開） |
| **睡眠精度（PSG 一致率）** | 約 65〜70%（Garmin 系平均） | 約 65〜70%（Garmin 系平均） | 79%（業界最上位） |
| **取得項目** | 睡眠時間/深い睡眠/REM/HRV/Sleep Coach | 同左 + **体温** + Smart Wake Alarm | 全部 + 体温 + SpO2 + 詳細スコア |
| **体温センサー** | **なし** | あり | あり |
| **HRV** | あり | あり | あり |
| **Smart Wake Alarm** | あり（30 分窓） | あり（30 分窓） | なし |
| **重さ** | **23g（軽い）** | 約 35g（45mm モデル） | 約 4g |
| **24 時間装着の快適性** | ◎（軽量で違和感少） | ○（腕時計サイズで人による） | ◎（指輪、ほぼ無自覚） |
| **防水・耐久** | 5 ATM（水泳OK・温水/サウナ NG）、Gorilla Glass 3 | 5 ATM、Gorilla Glass 3 | 100m 防水、Titanium 筐体 |
| **ディスプレイ** | AMOLED 1.2 インチ | AMOLED 1.4 インチ常時表示可 | なし（指輪） |
| **Suica 等** | あり | あり | なし |
| **公式 Health API** | ✕ 法人専用 | ✕ 法人専用 | ◎ 個人 OK・無料 |
| **python-garminconnect** | △ 2026-03 認証変更で**現在壊れた状態** | △ 同左 | — |
| **Apple Health 連携（睡眠ステージ含む）** | ◎ Garmin Connect v4.71 で完全連携 | ◎ 同左 | ◎ |
| **Health Auto Export 経由 Webhook** | ◎ 実用パス（Lifetime $24.99 買い切り） | ◎ 同左 | ◎ |
| **Selenium/Playwright スクレイピング** | ○ 実例あり、ブラウザ操作で bot detection 回避 | ○ 同左 | — |
| **手動 JSON 一括 export** | ○ Garmin Connect Web から可能 | ○ 同左 | ◎ API 直叩き |

※1 5 年 TCO はバッテリー交換 1 回（¥10,000）想定。Oura は 4 年で本体買い替え + サブスク 5 年分。

---

## 3. ユーザー優先軸でのスコア（10 点満点）

田中さんの優先順位 **コスト > 連携 > 精度** に重み付け（コスト ×3 / 連携 ×2 / 精度 ×1）:

| 軸 | Vivoactive 6 | Venu 4 |
|---|---|---|
| **コスト**（5 年 TCO） | 10（最安 ¥49,800） | 7（+¥40,000） |
| **連携性**（Apple Health + RPA 含む） | 8 | 8 |
| **精度・センサー**（体温有無含む） | 7（体温なし） | 8（体温あり） |
| **加重合計** | **10×3 + 8×2 + 7×1 = 53 / 60** | **7×3 + 8×2 + 8×1 = 45 / 60** |

→ **Vivoactive 6 が Q6 の優先軸に最も整合**。

---

## 4. RPA / ブラウザ自動化の現実的な実装案

両機種で API 以外の自動化ルートは共通。以下の 4 つの選択肢を比較:

| 方法 | 自動化度 | 安定性 | 実装工数 | 4/30 間に合う | 月額コスト | 備考 |
|---|---|---|---|---|---|---|
| **A. Apple Health + Health Auto Export → Webhook** | ◎ | ◎ | **半日** | ✅ | $24.99 買い切り | iPhone 必須、最も簡単で堅い |
| **B. Selenium/Playwright で Garmin Connect Web スクレイピング** | ◎ | △ | 1〜2 日 | ✅ | 0 | UI 変更で壊れる、メンテ要 |
| **C. 月 1 手動 JSON エクスポート + Python パース** | ✕ | ◎ | 30 分 | ✅ | 0 | 反映が月 1 遅延 |
| **D. python-garminconnect 復旧待ち** | ◎ | ✕ | 0（待ち） | ✗ | 0 | 復旧時期不明、賭け |

### 4.1 推奨ルート: A（Apple Health 経由）

**フロー**:
```
[Garmin デバイス]
   └─ BLE 同期（自動）
[iPhone: Garmin Connect アプリ]
   └─ Settings → Apple Health → 睡眠データを書き出し有効化（一度だけ設定）
[Apple Health（HealthKit）]
   ├─ 睡眠時間/各ステージ/HRV/心拍 を取り込み
   └─ Garmin Connect v4.71 から sleep stages も含めて連携
[iPhone: Health Auto Export アプリ（買い切り版 Lifetime $24.99）]
   └─ 自動化: 「Sleep Analysis」を毎朝 AIOS Webhook へ POST
[AIOS 側: webhook 受け口]
   └─ JSON を Flow/YYYYMM/YYYY-MM-DD/健康管理/_sleep_pull.md に書き出し
   └─ 日次レビューで Stock へ Finalize
```

**実装工数（半日想定）**:
- Garmin Connect → Apple Health 連携設定: 5 分（iPhone 操作のみ）
- Health Auto Export 購入 + Sleep Analysis automation 設定: 30 分
- AIOS 側 Webhook サーバー（FastAPI 等）: 2〜3 時間
  - macOS ローカルで `uvicorn` 常駐 or Cloudflare Workers にデプロイ
- JSON → Markdown 変換とファイル書き出し: 1 時間
- 動作確認: 1 時間

**最小構成コード雛形**:
```python
# scripts/sleep_webhook.py
from fastapi import FastAPI, Request
from pathlib import Path
from datetime import datetime
import json

app = FastAPI()

@app.post("/sleep")
async def receive(req: Request):
    body = await req.json()
    today = datetime.now().strftime("%Y-%m-%d")
    yyyymm = today[:7].replace("-", "")
    out_dir = Path(f"Flow/{yyyymm}/{today}/健康管理")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "_sleep_pull.md"
    # Health Auto Export の payload 仕様に従いパース
    sleep = next((m for m in body["data"]["metrics"] if m["name"] == "sleep_analysis"), None)
    if not sleep:
        return {"status": "no_sleep_data"}
    # ...パース処理...
    out_file.write_text(f"# 睡眠データ {today}\n\n```json\n{json.dumps(sleep, indent=2, ensure_ascii=False)}\n```\n")
    return {"status": "ok", "file": str(out_file)}
```

### 4.2 バックアップルート: B（Selenium スクレイピング）

iPhone を持っていない場合 or Apple Health 連携で十分なデータが流れない場合の代替。
- 実例: https://github.com/gordwest/GarminConnect-Selenium
- 個人ブログ: https://buckeye17.github.io/Scraping-Garmin/
- 実装工数: 1〜2 日（ログイン処理 + Sleep ページ遷移 + FIT/JSON ダウンロード + パース）

### 4.3 最終保証: C（月 1 手動）

最悪、A も B も組めなければ月 1 で `https://www.garmin.com/en-US/account/datamanagement/` から JSON 一括ダウンロード → ローカルでパース。月 1 反映でも記録自体は残せる。

---

## 5. AI の最終推奨

### 推奨機種: **Garmin Vivoactive 6** （¥39,800）

**理由**:
1. **Q6（コスト最優先）に最も整合**。5 年 TCO で Venu 4 比 ¥40,000 安、Oura 比 ¥82,000 安。
2. **Q3（24h 装着）に強い**。23g の軽量・薄型で就寝時の違和感が小さい。Venu 4 (35g) より明確に有利。
3. **Q1（自動連携）も Apple Health 経由で実現可能**。Venu 4 と同じルートが使える。
4. 睡眠機能の基本（深い睡眠/REM/HRV/Sleep Coach/Smart Wake Alarm）は揃う。

### Venu 4 を選ぶべきケース

以下のいずれかに該当するなら Venu 4 (¥79,800) を選ぶ価値あり:
- **体温センサーが具体的に欲しい用途がある**（体調不良の早期検知、季節適応の可視化など）
- **AMOLED 大画面 + 常時表示**を日常使い時に重視する
- **¥40,000 の差額を「センサー追加 + 質感」に払うのが惜しくない**

田中さんは Q6 でコストを最優先、健康管理プロジェクトは「体重 + 睡眠の質」が中心で **体温トレンドは必須でない** と判断。よって **Vivoactive 6 を推奨**。

### 体温センサー必要性の判断軸（2 行で）
- 男性ユーザーで月経周期トラッキング不要 + 体調不良は自覚できる範囲で対応 → **不要**（→ Vivoactive 6）
- 季節性の不調・自律神経乱れを定量的に追いたい / 風邪の超早期検知をしたい → **欲しい**（→ Venu 4）

### 購入リンク

**最推奨: Garmin Vivoactive 6**
- 公式日本: https://www.garmin.co.jp/products/wearables/vivoactive-6/
- 価格.com 比較: https://kakaku.com/keitai/wearable-device/itemlist.aspx?pdf_se=62
- Amazon.co.jp 検索: `Garmin Vivoactive 6` で検索

**代替: Garmin Venu 4 (45mm)**
- 公式日本: https://www.garmin.co.jp/products/wearables/venu-4-45-black/
- 価格.com: https://kakaku.com/item/J0000048924/

---

## 6. 4/30 までの最小実装計画（BL-0029 + BL-0030）

| 日付 | アクション | 担当 |
|---|---|---|
| 2026-04-22 | デバイス確定 → 公式 or Amazon で発注 | 田中さん |
| 2026-04-23〜25 | デバイス到着、初期セットアップ、Garmin Connect インストール | 田中さん |
| 2026-04-23〜26 | Apple Health 連携 ON、Health Auto Export 購入 + 設定 | 田中さん（10 分） |
| 2026-04-23〜27 | AIOS 側 Webhook サーバー実装（FastAPI 雛形） | AI（実装指示があれば） |
| 2026-04-26〜28 | 試運転：1 晩計測 → Apple Health → Webhook → Flow 書き出し確認 | 田中さん + AI |
| 2026-04-29 | BL-0029 記録運用開始（毎朝 1 件は自動でデータが流れる状態） | — |
| 2026-04-30 | BL-0030 完了確認（連続 2-3 日分のデータが Flow に蓄積、Finalize 手順整備） | AI |

**前提確認事項（次の質問票で確認したい）**:
- iPhone を所持しているか（Apple Health 経由の前提）
- Webhook サーバーの設置先（macOS ローカル常駐 / Cloudflare Workers / Vercel など）
- $24.99 の Health Auto Export 買い切り購入の許容（サブスクではないので Q2 と矛盾しない）

---

## 7. 過程資料

- 初版比較（Oura 推奨時）: `sleep_device_comparison.md`
- API 連携詳細: `api_integration_notes.md`
- ユーザー回答記録: `questions_to_user.md`

---

---

## 7.5 2026-04-22 田中さんメモ: Venu傾向で保留中

### 状態
- **デバイス確定: 保留**
- 田中さんのコメント: 「Venuが欲しいけど、一旦考えを寝かせる」
- 残り 3 つの前提は確定済（iPhone あり / Webhook = Vercel / Health Auto Export $24.99 OK）
- BL-0030 の事前準備は前倒しで進行中 → `bl0030_integration_prep.md`

### 新データポイント（決定材料の追加）

調査の結果、**Garmin → Apple Health の同期項目は steps / workouts / heart rate / sleep が中心**で、**体温（skin temperature / wrist temperature）は Apple Health に同期されない**ことが判明（Garmin 公式サポート + 複数ガイドで確認）。

これが Vivoactive 6 vs Venu 4 の判断に与える影響:

| | Vivoactive 6 | Venu 4 |
|---|---|---|
| 体温センサー | なし | あり |
| Garmin Connect アプリ内で体温トレンド表示 | — | ◎ |
| **Apple Health に体温が流れる** | — | **✕ 流れない** |
| **AIOS パイプラインに体温が乗る** | — | **✕ 乗らない**（追加実装が必要） |

→ **Venu 4 を選んでも、AIOS の睡眠分析に体温データは追加されない**。
→ Venu 4 の体温センサーが活きるのは「Garmin Connect アプリで毎日体温トレンドを目で見る」用途のみ。
→ もし「AIOS にすべてのデータを集約したい」が動機の Venu 検討なら、その動機は成立しない。

### Venu 4 を選ぶ意義が残るケース
- Garmin Connect アプリ内で体温トレンドをチェックしたい
- AMOLED 大画面 + 常時表示を日常使いで重視
- ¥40,000 の差額を「センサーの安心感・所有感・画面の質」に払うのが許容

### 体温データを AIOS に流したい場合の追加コスト（参考）
- Selenium/Playwright で Garmin Connect Web をスクレイピング → 1〜2 日工数
- python-garminconnect の復旧待ち → 不確実
- 月 1 手動 JSON エクスポート → 月 5 分 + 反映遅延

→ いずれも 4/30 の最小構成からは外れる。デバイス到着後の余裕がある時期に追加検討。

### 推奨（変わらず）
**Vivoactive 6**（Q6 優先軸: コスト > 連携 > 精度 に最適）

ただし田中さんの「Venu が欲しい」という感情的な引力（モノとしての魅力、所有感、画面）は**論理だけで否定すべきものではない**。寝かせて翌日以降に再判断するのは妥当な進め方。

---

## 8. 主要ソース

- [Garmin Vivoactive 6 review — Tom's Guide](https://www.tomsguide.com/wellness/smartwatches/i-wore-the-garmin-vivoactive-6-for-a-month-and-it-has-nearly-everything-i-want-in-a-smartwatch)
- [Garmin Vivoactive 6 review — Live Science](https://www.livescience.com/health/exercise/garmin-vivoactive-6-review)
- [Garmin Venu 4 vs Vivoactive 6 — Woman & Home](https://www.womanandhome.com/health-wellbeing/fitness/garmin-venu-vs-vivoactive/)
- [Garmin Connect → Apple Health sleep stages 連携 — NotebookCheck](https://www.notebookcheck.net/Garmin-Connect-begins-sharing-more-sleep-data-with-Apple-Health-after-new-iOS-app-update.753484.0.html)
- [Sharing Garmin Connect Data With Apple Health — Garmin Support](https://support.garmin.com/en-US/?faq=lK5FPB9iPF5PXFkIpFlFPA)
- [Health Auto Export pricing — HealthyApps](https://www.healthyapps.dev/health-auto-export-pricing)
- [Health Auto Export Automations — HealthyApps Help](https://help.healthyapps.dev/en/health-auto-export/automations/)
- [Garmin Connect Selenium scraping example — buckeye17](https://buckeye17.github.io/Scraping-Garmin/)
- [GarminConnect-Selenium — GitHub](https://github.com/gordwest/GarminConnect-Selenium)
- [python-garminconnect — GitHub](https://github.com/cyberjunky/python-garminconnect)
- [Garmin Vivoactive 6 公式 — Garmin Japan](https://www.garmin.co.jp/products/wearables/vivoactive-6/)
- [Garmin Venu 4 公式 — Garmin Japan](https://www.garmin.co.jp/products/wearables/venu-4-45-black/)
