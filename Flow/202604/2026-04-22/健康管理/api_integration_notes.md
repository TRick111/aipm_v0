# AIOS自動連携 実現可能性メモ（BL-0030 の事前検討）

- 対象: BL-0030「睡眠データのAIOS自動連携」（期限 2026-04-30）
- 親比較ドキュメント: `sleep_device_comparison.md`
- 作成日: 2026-04-22

## 結論

- **Oura Ring 4**: 公式 Web API（OAuth2）で安定的に取得可能。**AIOS 側の実装は cron + Python スクリプトで 1〜2 日**で組める見込み。
- **Garmin**: 公式 API は法人専用。非公式 python-garminconnect が唯一の手段だが、**sleep エンドポイントで HTTP 404 報告あり**＋ Garmin の認証変更で随時壊れる前提の運用が必要。期限 4/30 に間に合わせるならリスク大。

## 1. Oura Ring 4 の連携設計案

### 1.1 認証
- 公式: `https://developer.ouraring.com/`
- **Personal Access Token は廃止済み**。OAuth2 必須。
- 個人利用でも開発者登録可（無料）。redirect URI に `http://localhost:<port>` を指定すれば、ローカル単独運用で完結。

### 1.2 主要エンドポイント（v2）
| 用途 | エンドポイント |
|---|---|
| 睡眠スコア（日次） | `GET /v2/usercollection/daily_sleep?start_date=...&end_date=...` |
| 各睡眠ステージ詳細 | `GET /v2/usercollection/sleep` |
| Readiness | `GET /v2/usercollection/daily_readiness` |
| Activity | `GET /v2/usercollection/daily_activity` |
| HRV/SpO2 | `GET /v2/usercollection/sleep` 内に含まれる |

### 1.3 取得できる主な指標（睡眠）
- `score`（総合睡眠スコア 0-100）
- `total_sleep_duration` / `deep_sleep_duration` / `rem_sleep_duration` / `light_sleep_duration` / `awake_time`
- `average_hrv` / `lowest_heart_rate` / `average_breath`
- `bedtime_start` / `bedtime_end`

### 1.4 AIOS への取り込み案（叩き台）
```
[cron 毎朝 8:00]
  └─ scripts/oura_pull.py
       ├─ OAuth2 token を ~/.config/oura/token.json から読む（自動リフレッシュ）
       ├─ daily_sleep + sleep を前日分取得
       └─ Stock/ゴール管理/健康管理/sleep_log/YYYY-MM.md にテーブル追記
            （Stock 直接更新は AIOS ルール 2.1 に反するため、
             実装時は Flow/YYYYMM/YYYY-MM-DD/健康管理/_sleep_pull.md に出力 →
             日次レビューで Finalize する形が望ましい）
```

### 1.5 想定工数
- OAuth2 アプリ登録: 30 分
- Pull スクリプト実装: 半日
- AIOS Flow への書き込みフォーマット決定 + 出力テンプレ: 半日
- cron / launchd 登録 + 動作確認: 半日
- **合計: 1〜2 日**

### 1.6 リスク
- OAuth2 トークンのリフレッシュ失敗時のリカバリー（再認証フロー）。ローカル単独運用なら `oura_pull.py --reauth` で手動実行する程度で十分。
- サブスク切れ → スコア未算出。年額更新を BL に登録しておく必要あり。

---

## 2. Garmin の連携設計案（参考、非推奨）

### 2.1 公式 Health API
- **法人専用**。個人申請は明確に却下される運用。
- 仮に承認されても商用前提のため、個人プロジェクトでは現実的でない。

### 2.2 非公式 python-garminconnect
- リポジトリ: https://github.com/cyberjunky/python-garminconnect
- Garmin Connect モバイルアプリの SSO フローを模倣して Bearer Token を取得。
- **既知の問題**: `get_sleep_data()` で HTTP 404 が報告されるケースあり（Issue 207 周辺）。`get_heart_rates()` 等は動くが、肝心の睡眠が不安定。
- Garmin が認証フローを更新すると即時に壊れる（過去にも garth ベースの実装が動かなくなった経緯あり）。

### 2.3 もし Garmin を選んだ場合の現実的選択肢
| 選択肢 | コメント |
|---|---|
| python-garminconnect 直叩き | 4 月末までに動く保証なし。動いても運用後に壊れる前提でメンテ覚悟 |
| Health Auto Export 等 iPhone アプリ経由 | Apple Health に流して、そこから export → AIOS、という遠回り。アプリ依存・手動同期が残る |
| Terra / Spike / Thryve など API アグリゲータ | 月額課金（$50〜/月オーダー）。個人利用には過剰 |

### 2.4 想定工数
- 非公式ライブラリ動作確認: 1 日（404 再現の有無で運命が分かれる）
- 仮に動いた場合の取り込み実装: Oura と同等 1〜2 日
- **合計: 2〜3 日 ＋ 継続的な保守コスト**

---

## 3. 比較サマリ（AIOS連携観点のみ）

| | Oura Ring 4 | Garmin（任意機種） |
|---|---|---|
| 公式APIで個人OK | ◎ | ✕ |
| 認証 | OAuth2（標準的） | 非公式SSO模倣 |
| 睡眠データ取得の安定性 | ◎ | △ |
| BL-0030 を 4/30 に間に合わせる確度 | 高 | 低 |
| 長期保守コスト | 低 | 高 |

## 4. 推奨

**Oura Ring 4 を採用し、BL-0030 を以下の段取りで進める:**

1. デバイス到着前に Oura Developer 登録 + OAuth2 アプリ作成（事前準備）
2. デバイス到着後、Oura アプリで初期セットアップ（数日で個人ベースライン算出）
3. `scripts/oura_pull.py` を実装し、Flow への書き出しを確認
4. cron 登録、Stock への Finalize 運用を `aios/ops/05_finalize_to_stock.mdc` に従って整備
5. BL-0029 の記録運用と並行して、BL-0030 を完了

## 参考リンク

- Oura Developer: https://developer.ouraring.com/
- Oura API v2 docs: https://cloud.ouraring.com/v2/docs
- Oura Help — The Oura API: https://support.ouraring.com/hc/en-us/articles/4415266939155-The-Oura-API
- Garmin Health API: https://developer.garmin.com/gc-developer-program/health-api/
- python-garminconnect: https://github.com/cyberjunky/python-garminconnect
