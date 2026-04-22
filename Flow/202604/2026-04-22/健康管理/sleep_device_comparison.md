# 睡眠計測デバイス比較 — Oura Ring 4 vs Garmin

- 対象タスク: BL-0028（睡眠計測デバイスの購入）
- 後続タスク: BL-0029（睡眠記録運用開始）/ BL-0030（AIOS自動連携、4月末目標）
- 作成日: 2026-04-22

## 結論（先出し）

**推奨: Oura Ring 4（Silver, サイズは要計測）**

決め手は **AIOS自動連携の実現可能性**。Oura は公式 API（OAuth2、個人開発OK、無料）を提供しており、`GET /v2/usercollection/daily_sleep` で睡眠スコア・各睡眠ステージ・HRV を直接取得できる。一方 Garmin は **Health API が法人専用**で、個人申請は却下される。代替の非公式ライブラリ（python-garminconnect）は sleep エンドポイントで HTTP 404 が報告されており、Garmin 側の認証変更で壊れやすく、BL-0030 の安定運用に大きなリスクを抱える。

睡眠スコアの精度面でも Oura が優位（Brigham 病院の研究で PSG との4ステージ一致率 79%、Garmin は「中〜下位」評価）。装着感も指輪のほうが就寝時の違和感が少ない。Garmin はサブスク不要で 2 年目以降は安いが、3 年トータルでは Oura ¥76,400 vs Garmin Venu 4 (45mm) ¥79,800 とほぼ同等。

## 比較表

| 観点 | Oura Ring 4 | Garmin Venu 4 (45mm) | Garmin Vivoactive 6 |
|---|---|---|---|
| **公式API（個人OK）** | ◎ OAuth2 公式API。個人開発登録OK・無料。`daily_sleep` で睡眠スコア／各ステージ／HRV／体温を取得 | ✕ Health API は **法人専用**。個人申請は却下される | ✕ 同上（Garmin 共通） |
| **非公式API代替** | — | △ python-garminconnect。**sleep エンドポイントで HTTP 404 報告あり**、認証変更で壊れやすい | △ 同上 |
| **AIOS自動連携の実現性（BL-0030）** | ◎ 公式APIで cron→YAML/MD 書き込み構成が素直に組める | ✕ 法人申請が現実的でない／非公式は壊れる前提で運用が必要 | ✕ 同上 |
| **睡眠スコア精度** | ◎ PSG（医療機関の睡眠ポリグラフ）4ステージ一致率 79%。研究比較で最上位クラス | △ 「中〜下位」評価。特に REM 検出が弱い | △ 同上（Venu 4 と同等センサー帯） |
| **取得項目** | 睡眠時間/深い睡眠/REM/覚醒/HRV/体温/SpO2/心拍 | 睡眠時間/深い睡眠/REM/HRV/体温/SpO2/心拍/Sleep Coach | 睡眠時間/深い睡眠/REM/HRV/Sleep Coach（**体温センサーなし**） |
| **バッテリー** | 約 8 日 | 約 12 日（AMOLED 常時表示OFF時） | 約 11 日 |
| **装着感（就寝時）** | ◎ 指輪、軽量、就寝中ほぼ無自覚 | △ 腕時計サイズで就寝時に気になる場合あり | △ 同上 |
| **本体価格（日本、税込）** | ¥52,800〜（色・サイズで変動。Silver が最安） | ¥79,800（45mm）/ ¥67,099（41mm） | 約 ¥39,800（参考） |
| **サブスク** | ¥999/月 or **¥11,800/年**（初月無料） | 不要 | 不要 |
| **3年総コスト試算** | ¥52,800 + ¥11,800×2 = **¥76,400** | **¥79,800** | 約 ¥39,800 |
| **エコシステム** | Apple Health / Google Fit 連携可、API 安定 | Garmin Connect、Suica対応 | Garmin Connect |

※ Oura は本体 1 ヶ月分のサブスクが付属、2 ヶ月目以降が課金対象。年額換算で計算。
※ Garmin は本体購入のみで全機能利用可（API は別問題）。

## 各候補の評価コメント

### Oura Ring 4（推奨）
- **強み**: 公式APIが個人開発者に開放されており、無料・OAuth2 という"普通のWebAPI"として叩ける。BL-0030 の自動連携は、cron で日次スコアを `Stock/ゴール管理/健康管理/sleep_log/` に書き出すだけで済む。睡眠精度も研究で最上位。
- **弱み**: サブスク必須（年 ¥11,800）。指輪サイズの事前計測が必要（無料の Sizing Kit 取り寄せ推奨）。
- **想定運用**: 就寝時のみ装着でもよし、24h 装着でストレス・体温も記録してもよし。

### Garmin Venu 4（次点だが非推奨）
- **強み**: 体温センサーありで睡眠の指標は揃う。Suica 対応で日常使いも便利。サブスク不要。
- **弱み**: **API が事実上閉じている**。BL-0030 を 4 月末で安定構築するには非公式ライブラリに頼るしかなく、運用後に壊れるリスクが高い。睡眠精度も Oura に劣る（特に REM）。本体価格も高め。

### Garmin Vivoactive 6（コスト重視の代替）
- 体温センサーがなく、Venu 4 より睡眠機能が一段下。API 制約は同じ。**今回の用途（睡眠＋自動連携）では選択肢にならない**。

## API/連携の詳細

→ `api_integration_notes.md` を参照。

## 購入リンク

### 推奨: Oura Ring 4
- **公式（推奨）**: https://ouraring.com/ja/store/rings/oura-ring-4/silver
  - 公式購入のメリット: 無料 Sizing Kit を先に送ってもらえる（サイズ間違い回避）／初月サブスク無料／保証が確実
  - 価格.com 参考: https://kakaku.com/item/K0001700775/
- 楽天: https://item.rakuten.co.jp/pocketalk/or4/
- ソースネクスト（国内代理）: https://www.sourcenext.com/product/ouraring/

### 次点（API制約を理解した上で選ぶ場合）
- Garmin Venu 4 45mm 公式: https://www.garmin.co.jp/products/wearables/venu-4-45-black/
  - 価格.com: https://kakaku.com/item/J0000048924/

## 推奨アクション

1. **Oura 公式サイトで Sizing Kit を無料注文**（到着まで数日 → サイズ確定 → 本体注文）
2. Sizing Kit を待つ間に BL-0030 のための **Oura Developer 登録**を済ませておく（OAuth2 アプリ作成、Personal Access Token は廃止済みなので OAuth2 フロー必須）
3. デバイス到着後 24-48h はキャリブレーション期間として割り切り、BL-0029（記録運用）開始

## リスクと前提

- **指輪サイズ**: Sizing Kit を使わずに購入するとサイズ違いで返品交換のリスク。発注前に Kit 取り寄せ推奨（数日のロスは許容範囲）。
- **充電習慣**: 8 日に 1 回・約 60-80 分の充電。シャワー/着替え時にスタンドへ置く運用で十分。
- **OAuth2 サーバ**: ローカル単独運用なら redirect URI を `http://localhost` で十分。AIOS 側で Token 永続化と更新を組み込む必要あり（BL-0030 のスコープ）。

---

# 2026-04-22 追加検討: 長期コスト・耐久性・連携性の再評価

ユーザー指摘: 「Oura はバッテリー寿命があり 2〜3 年で買い替えになるのでは？長期コストで Garmin が有利では？」

## A. バッテリー寿命・交換可否

### Oura Ring 4
- **公称サイクル**: 730 充電サイクルで容量 80% を維持。週 1 回充電（5〜8 日持ち）なら **約 14 年分のサイクル数**だが、リチウムポリマーの自然劣化があるため実態はもっと短い。
- **実測の劣化**: 2024 年の実調査で、**1 年経過後**にランタイム中央値が 7.2 日 → 5.8 日（**19% 減**）。89% の個体が ≥6 日を維持。
- **end-of-life 判定**: 1 充電あたり ≤4 日 ＋ 充電時間 >90 分 になったら寿命扱い → Oura Support に連絡。
- **平均寿命**: 軽い使用（睡眠中心）なら 4 年超、24h 装着 + 重いアクティビティ記録だと 2 年弱。**現実的には 3〜4 年で買い替え or バッテリー交換が必要**になる想定が妥当。
- **交換可否**: ユーザーによる交換は不可（密閉構造）。**Oura 公式が Gen 3 / Ring 4 向けに「certified battery replacement」サービスを提供**しているが、料金は公開されていない（要問い合わせ）。
- **本体寿命**: チタン/セラミック筐体・センサー・ハプティックは 5 年超持つ。寿命を決めるのは事実上バッテリー。

### Garmin Venu 4 / Vivoactive 6
- **本体寿命**: 一般に **5 年程度**は問題なく使える（Garmin 公式コメント / ユーザー実感）。長く使えば 10 年以上の事例も。
- **バッテリー劣化**: リチウムは 500 サイクルで 20% 減。日常使用（GPS 多用しない）で 2〜3 年で体感劣化、5 年程度で交換検討。
- **交換可否・費用**:
  - Garmin 公式サービス: **$50〜80（約 ¥7,500〜12,000）**
  - 第三者修理店: $30〜50（約 ¥4,500〜7,500）
  - DIY: $10〜20（約 ¥1,500〜3,000、ただし防水保証は失う）
  - **注意**: Venu は接着シール式背面で開けにくく、開封後に防水性能を失うリスクあり。**実質的には公式サービス推奨**。
- **耐久**: 5 ATM 防水（水泳OK、温水/サウナNG）、Gorilla Glass 3 / 5 採用で日常使用は十分耐える。

### バッテリー比較サマリ
| | Oura Ring 4 | Garmin Venu 4 |
|---|---|---|
| 体感の買い替えサイクル | 3〜4 年 | 5〜7 年（バッテリー交換すれば延命可） |
| ユーザー交換 | 不可 | 一応可（防水保証喪失） |
| 公式交換サービス | あり（料金非公開） | あり（¥7,500〜12,000） |
| 本体寿命の決定要因 | バッテリー（=本体寿命） | バッテリー（交換可能なので筐体寿命） |

→ **ユーザーの懸念は正しい**。Oura の「ハードウェア寿命 = バッテリー寿命」は構造的なデメリット。Garmin はバッテリー交換で延命できる分、長期コストは有利。

## B. 5 年トータルコスト試算

### 前提
- 為替・サブスク料金は 2026-04 時点の日本価格をベース
- Oura: 本体 ¥52,800 + サブスク ¥11,800/年（初月無料は無視）
- Garmin Venu 4 (45mm): ¥79,800、サブスク不要
- Garmin Vivoactive 6: ¥39,800、サブスク不要、ただし**体温センサーなし**（睡眠用途で不利）

### シナリオ1: バッテリー交換しない / バッテリー寿命で買い替え
| | Oura Ring 4 | Garmin Venu 4 | Garmin Vivoactive 6 |
|---|---|---|---|
| 本体（5 年で 1 台 or 2 台） | ¥52,800 × 2台 = ¥105,600（4年で買い替え想定） | ¥79,800 × 1台 | ¥39,800 × 1台 |
| サブスク（5 年） | ¥11,800 × 5 = ¥59,000 | 0 | 0 |
| **5 年合計** | **¥164,600** | **¥79,800** | **¥39,800** |

### シナリオ2: バッテリー交換で延命
| | Oura Ring 4 | Garmin Venu 4 | Garmin Vivoactive 6 |
|---|---|---|---|
| 本体 | ¥52,800 | ¥79,800 | ¥39,800 |
| バッテリー交換（4 年目想定） | ¥??? 公式料金非公開、仮に ¥20,000 と置く | ¥10,000（公式中央値） | ¥10,000 |
| サブスク（5 年） | ¥59,000 | 0 | 0 |
| **5 年合計** | **¥131,800（仮定値含む）** | **¥89,800** | **¥49,800** |

### コスト差（5 年・シナリオ2基準）
- Oura vs Venu 4: **+¥42,000（Oura が高い）** = 月割 ¥700
- Oura vs Vivoactive 6: **+¥82,000（Oura が高い）** = 月割 ¥1,367

→ **5 年で見ると Oura は ¥4〜8 万円高い**。これは無視できない差。

## C. API 連携性の再評価

### Garmin の現状（2026-04 時点・要注意）
- **公式 Health API**: 法人専用（変わらず）
- **python-garminconnect**: **2026-03-28 に garth 認証が deprecate され壊れた状態**。Garmin が aggressive bot detection を導入し、既知の Python HTTP ライブラリは全てブロック。Issue #332 に 40 件超の動作不能報告。
- **Garmin 自身が $7/月サブスクを開始**し、サードパーティアクセスを意図的に絞る方針が見える（今後も改善見込み薄）
- **手動エクスポート**: Garmin Connect Web の Sleep ページから FIT 形式で個別ダウンロード可。一括は JSON で全データ一括ダウンロード可（数十 MB）。CSV 直接エクスポートはなし。
- **GarminDB / GarminSleepAnalytics**: 内部で python-garminconnect 系 or FIT パースに依存。前者は同様に壊れている。後者は手動 DL の FIT を解析する用途。

### 現実的な Garmin 運用パターン
| 運用 | 自動化度 | 手間 | 4/30 までの実現性 |
|---|---|---|---|
| 公式 Health API | ◎ | 0 | ✕ 法人申請却下 |
| python-garminconnect 等で自動取得 | ◎ | 0 | ✕ 現在動かない |
| **月 1 回手動エクスポート + パーススクリプト** | △ | 月数分 | ○ 実現可能 |
| **毎日手動エクスポート** | ✕ | 毎日数分 | △ 続かない可能性 |

→ Garmin を選ぶ場合の現実解は **「月 1 回手動エクスポートして AIOS にバッチ取り込み」**。日次の睡眠スコア反映は遅延 1 ヶ月。

### Oura の現状
- 公式 OAuth2 API、個人開発者登録無料、エンドポイントは安定（v2 で 3 年以上運用実績）
- 4/30 までに自動連携完成可能性: **高**

## D. 総合再判定

### 3 軸スコア（10 点満点、5 年視点）

| 軸 | Oura Ring 4 | Garmin Venu 4 |
|---|---|---|
| 長期コスト | 6（5 年で +¥4〜8 万、サブスクの心理的負担あり） | 9（明確に安く、所有感あり） |
| AIOS 自動連携性（BL-0030） | 9（公式 API、4/30 余裕で間に合う） | 3（自動は事実上不可、月 1 手動が現実解） |
| 実用性（睡眠精度・装着感） | 9（精度最上位、就寝時の違和感ゼロ） | 7（精度中位、腕時計は人による） |
| **重み付け合計**（連携 ×2、コスト ×1、実用 ×1） | **9+9+9+9 = 36 / 40** | **3+3+9+7 = 22 / 40** |

※ 重み付けは BL-0030 がプロジェクトのゴール（4 月末必達）であることを反映し、連携性を 2 倍。

### 結論

**前回判定を維持: Oura Ring 4 推奨。**

ただし、コスト差は **明確に存在する** ことをユーザーが認識した上で選ぶべき。

**判定が変わるケース**:
1. **BL-0030（自動連携）を「nice-to-have」「諦めても良い」「月 1 手動でも可」と再定義**できるなら → Garmin Venu 4 が合理的
2. **5 年で +¥4〜8 万円の差を許容できない**かつ自動連携も諦められるなら → Garmin Vivoactive 6（最安、ただし体温センサーなしで睡眠機能が一段下）

これらは健康管理プロジェクトのゴール（睡眠データ AIOS 自動連携）を維持するか否かの判断であり、**ユーザー本人の意思確認が必要**。確認事項は `questions_to_user.md` に整理した。

## E. 推奨アクション（更新版）

1. **まず `questions_to_user.md` の確認事項に回答してもらう**
2. 回答に応じて最終機種を確定:
   - 自動連携を維持 → Oura Ring 4
   - 自動連携を諦める or 月 1 手動で可 → Garmin（Venu 4 推奨、コスト最重視なら Vivoactive 6）
3. 機種確定後、Sizing Kit 取り寄せ（Oura の場合）or 公式ストアで発注

## ソース

- [Oura Ring Review 2026 — Sleep Foundation](https://www.sleepfoundation.org/best-sleep-trackers/oura-ring-review)
- [Oura Ring 4 Review (2026) — The Body Blueprint](https://thebodyblueprint.com/oura-ring-4-review/)
- [Oura vs Garmin full comparison — Wareable](https://www.wareable.com/features/oura-ring-vs-garmin-full-comparison)
- [Oura Ring vs Garmin sleep tracker comparison 2026 — Optimize Biomarkers](https://optimizebiomarkers.com/sleep-compare/oura-ring-vs-garmin)
- [Oura Developer Docs](https://developer.ouraring.com/docs/)
- [Garmin Health API — Garmin Developers](https://developer.garmin.com/gc-developer-program/health-api/)
- [python-garminconnect — GitHub](https://github.com/cyberjunky/python-garminconnect)
- [Garmin Venu 4 vs Vivoactive 6 — Woman & Home](https://www.womanandhome.com/health-wellbeing/fitness/garmin-venu-vs-vivoactive/)
- [Oura Ring 4 日本発売 — Impress Watch](https://www.watch.impress.co.jp/docs/news/2031851.html)
- [Garmin Venu 4 日本価格 — Garmin Japan](https://www.garmin.co.jp/products/wearables/venu-4-45-black/)

---

# 2026-04-22 最終確定: Oura Ring 4

ユーザー回答（`questions_to_user.md` Q1）: **A（必達）**
→ BL-0030（4/30 必達）の前提が確定したため、**Oura Ring 4 で発注を進める**。

## 1. Sizing Kit 発注手順（最優先・本日中に実施）

本体到着まで合計 1〜2 週間かかるので、**Sizing Kit を最速で発注**する。

### 発注先（公式日本ストア・無料）
- **Sizing Kit 単体ページ**: https://ouraring.com/ja/sizing
- **本体購入時に Sizing Kit を選ぶ場合**: https://ouraring.com/ja/store/rings/oura-ring-4/silver の購入フローで「サイズが分からない」を選ぶと無料 Kit が先に発送される

### 必要情報
- 配送先住所（日本国内可、DHL 配送）
- メールアドレス（注文確認・追跡用）
- 支払い: **Sizing Kit 自体は無料**（送料込み）。本体を後日注文する際にカード/Apple Pay 等で決済。

### 到着までの目安
- 注文から **約 1 週間で到着**（DHL）。実例では「土曜朝注文 → 翌週木曜到着」
- Kit には複数サイズのプラスチック製試着リングが入っている
- **24 時間装着して**、日中・就寝中の両方でフィット感を確認（指は朝晩でサイズが変わるため）

### サイズ確定後
- 本体注文 → さらに **約 1 週間で到着**
- **合計タイムライン**: 4/22 発注 → 4/29 頃 Kit 到着 → 4/30 サイズ確定 → 5/7 頃 本体到着
  → BL-0029（4/30）の記録運用開始は数日遅延するが、**BL-0030（4/30 自動連携）は本体無しでも準備可能**（次節）。

## 2. BL-0030（AIOS 自動連携）の前倒し準備

Sizing Kit / 本体到着待ちの間に、**先に AIOS 連携の足場を組んでおく**。本体到着次第すぐに動かせる状態にする。

### 2.1 Oura Developer 登録（10 分）
1. https://cloud.ouraring.com/oauth/applications にアクセス
2. Oura アカウントを作成（本体購入時に作るアカウントと同じものを使う）
3. ログイン後、右上「Create A New Application」

### 2.2 認証方式の選択
**選択肢 A: Personal Access Token（PAT）— 推奨（単一ユーザー利用）**
- 自分のデータを自分のスクリプトから取得するだけなら、PAT が圧倒的に楽
- developer dashboard の「Personal Access Tokens」から発行 → 1 行の Bearer トークン
- スクリプトは `Authorization: Bearer <token>` を付けるだけ

**選択肢 B: OAuth2 アプリ — 複数ユーザー対応や本格運用向け**
- アプリ登録時に以下を入力:
  - Application Name: `aios-sleep-pull`
  - Redirect URIs: `http://localhost:8000/callback`
  - Website: 任意（GitHub 個人ページ等で可）
- 発行された Client ID / Client Secret を保存
- 認可 URL: `https://cloud.ouraring.com/oauth/authorize`
- トークン URL: `https://api.ouraring.com/oauth/token`

→ **個人運用なら PAT で十分**。BL-0030 のスコープでは PAT を選ぶ。

### 2.3 サンプル取得スクリプト（雛形）

`aios_v0` リポジトリ内、想定パス: `scripts/oura_pull.py`

```python
#!/usr/bin/env python3
"""Oura Ring から前日分の睡眠データを取得して Flow に書き出す。"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path
import requests

OURA_TOKEN = os.environ["OURA_PAT"]  # ~/.config/oura/token を export
BASE = "https://api.ouraring.com/v2/usercollection"
HEADERS = {"Authorization": f"Bearer {OURA_TOKEN}"}

def fetch(endpoint: str, day: date) -> dict:
    r = requests.get(
        f"{BASE}/{endpoint}",
        headers=HEADERS,
        params={"start_date": day.isoformat(), "end_date": day.isoformat()},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def main() -> int:
    target = date.today() - timedelta(days=1)
    daily = fetch("daily_sleep", target)
    detail = fetch("sleep", target)

    if not daily.get("data"):
        print(f"no data for {target}", file=sys.stderr)
        return 1

    d = daily["data"][0]
    score = d["score"]
    contributors = d.get("contributors", {})

    sleep = detail["data"][0] if detail.get("data") else {}
    total_h = round(sleep.get("total_sleep_duration", 0) / 3600, 2)
    deep_h = round(sleep.get("deep_sleep_duration", 0) / 3600, 2)
    rem_h = round(sleep.get("rem_sleep_duration", 0) / 3600, 2)
    hrv = sleep.get("average_hrv")

    yyyymm = target.strftime("%Y%m")
    out_dir = Path(f"Flow/{yyyymm}/{target.isoformat()}/健康管理")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "_sleep_pull.md"

    out_file.write_text(
        f"# 睡眠データ（自動取得） {target.isoformat()}\n\n"
        f"- 睡眠スコア: {score}\n"
        f"- 総睡眠時間: {total_h} h\n"
        f"- 深い睡眠: {deep_h} h\n"
        f"- REM 睡眠: {rem_h} h\n"
        f"- 平均 HRV: {hrv}\n"
        f"- 寄与因子: {contributors}\n",
        encoding="utf-8",
    )
    print(f"wrote {out_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 2.4 cron 登録（macOS launchd 推奨）
`~/Library/LaunchAgents/com.aios.oura-pull.plist` で毎朝 8:00 に実行。
- BL-0030 の本実装で雛形→本番化する。

### 2.5 Stock 反映ルール
- AIOS ルール 2.1 により、Stock 直接書き込みは禁止 → スクリプトは Flow に書き出す
- 日次レビュー時に `Stock/ゴール管理/健康管理/sleep_log/YYYY-MM.md` へ Finalize（aios/ops/05）

### 2.6 Sizing Kit 待ちの間にやるべきタスク
| やること | 所要 | 完了条件 |
|---|---|---|
| Oura Developer アカウント作成 | 5 分 | dashboard ログイン可 |
| PAT 発行 | 1 分 | トークン取得・`~/.config/oura/token` 保存 |
| `oura_pull.py` をリポジトリに追加 | 30 分 | `python scripts/oura_pull.py` がエラーなく走る（データなし応答でOK） |
| launchd plist 雛形 | 15 分 | `launchctl list` で登録確認 |
| Stock 反映ルール / Finalize 手順を README に記載 | 30 分 | `Stock/ゴール管理/健康管理/README.md` に追記 |

→ **本体到着前に AIOS 側の準備が完了する状態**を作る。本体到着 → アカウント連携 → 1 晩計測 → 翌朝 cron で初回データ取得、という流れ。

## 3. 確定アクションリスト（時系列）

| 日付 | アクション | 担当 |
|---|---|---|
| 2026-04-22 | Sizing Kit 発注 | 田中さん |
| 2026-04-22 | Oura Developer 登録 / PAT 発行 | 田中さん（5 分） |
| 2026-04-22〜29 | `oura_pull.py` + launchd 雛形作成 | AI（指示があれば実装可） |
| 〜2026-04-29 | Sizing Kit 到着 → 24h 試着 | 田中さん |
| 2026-04-30 | サイズ確定 → 本体注文 | 田中さん |
| 〜2026-05-07 | 本体到着 → 初期セットアップ → 計測開始（BL-0029 開始） | 田中さん |
| 2026-05-08 | 初回 cron 実行 → AIOS にデータ流入確認（BL-0030 完了） | AI + 田中さん |

## 4. 残課題（質問票）

`questions_to_user.md` の Q4（サイズ把握）/ Q5（装着指）は **Sizing Kit 到着後**に確定する想定。Q2/Q3/Q6 は方針整理用なので、空き時間に回答してもらえばよい。

---

### 追加ソース（2026-04-22 追加検討用）
- [Oura Ring 4 Battery Life — Oura Help](https://support.ouraring.com/hc/en-us/articles/35694051065235-Oura-Ring-4-Battery-Life)
- [Oura Ring battery replacement guide — History Tools](https://www.historytools.org/how-to/oura-ring-battery-replacement)
- [Garmin watch battery replacement complete guide — WalkingSolar](https://walkingsolar.com/can-garmin-watch-batteries-be-replaced/)
- [Life Expectancy for the Rechargeable Battery — Garmin Support](https://support.garmin.com/en-GB/?faq=MRS4iKokKE7I2TT6AwsxG7)
- [Sleep data export from Garmin Connect — Garmin Forums](https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-connect-web/119054/sleep-data-export-from-garmin-connect)
- [GarminDB — GitHub](https://github.com/tcgoetz/GarminDB)
- [python-garminconnect Issue tracker — GitHub](https://github.com/cyberjunky/python-garminconnect/issues)

### 追加ソース（2026-04-22 最終確定: Oura 発注手順）
- [Oura Sizing 公式 — How to size your new Oura Ring（日本語）](https://ouraring.com/ja/sizing)
- [Oura API Authentication](https://cloud.ouraring.com/docs/authentication)
- [Oura API v2 docs](https://cloud.ouraring.com/v2/docs)
- [Build a sleep tracking app using Oura — Medium](https://medium.com/@pgzmnk/build-a-sleep-tracking-app-using-oura-part-1-interface-the-oura-cloud-api-cf71a3b981d6)
- [python-ouraring — GitHub](https://github.com/turing-complet/python-ouraring)
