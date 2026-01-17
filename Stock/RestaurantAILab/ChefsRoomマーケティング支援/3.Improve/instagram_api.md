# Instagram Graph API における動画メトリクス取得に関する詳細レポート（2025 年時点）

## 1. 概要

Instagram Graph API は、Meta（旧 Facebook）が提供する Instagram ビジネスおよびクリエイターアカウント向けの公式 API です。これにより、外部のアプリケーションから Instagram のデータにアクセスし、コンテンツの投稿、コメント管理、DM 対応、インサイト（分析指標）取得などが可能になります。

本レポートでは、特に Instagram 上の動画コンテンツ（フィード動画、リール、IGTV など）において、どのようなメトリクス（分析指標）が Graph API で取得可能なのかを詳述します。

---

## 2. API で取得可能な主な動画メトリクス

以下のメトリクスは、`/{ig-media-id}/insights` エンドポイントを使用して取得可能です（対象：ビジネス or クリエイターアカウントで投稿された動画）

### 🎥 動画メディア対応メトリクス一覧（主にリール動画に最適化）

| メトリクス名         | 説明                                | 備考                                |
| -------------------- | ----------------------------------- | ----------------------------------- |
| `plays`              | 動画の再生回数（3 秒以上）          | Reels・フィード共通                 |
| `reach`              | 動画を視聴したユニークアカウント数  |                                     |
| `impressions`        | 動画が画面に表示された総回数        |                                     |
| `likes`              | いいねの数                          |                                     |
| `comments`           | コメントの数                        |                                     |
| `saves`              | 保存された回数                      |                                     |
| `shares`             | 他のユーザーへの共有回数            | リール向け                          |
| `average_watch_time` | 視聴 1 回あたりの平均視聴時間（秒） | 主にリールで取得可能                |
| `completion_rate`    | 最後まで視聴された割合（完視聴率）  | 主にリールで取得可能                |
| `forward_taps`       | 次のリールへスワイプした回数        | インタラクション分析用（非公式）    |
| `backward_taps`      | 前のリールへ戻った回数              |                                     |
| `drop_off_points`    | 離脱が多かった時間帯                | グラフ形式で提供（非公開 API 含む） |

### 🔗 公式ドキュメント参照元：

-   [https://developers.facebook.com/docs/graph-api/reference/video/video_insights/#metrics](https://developers.facebook.com/docs/graph-api/reference/video/video_insights/#metrics)
-   [https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights/](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights/)

---

## 3. メトリクスの取得方法

### 3.1 エンドポイント例：

```http
GET https://graph.facebook.com/v17.0/{media_id}/insights
  ?metric=plays,reach,impressions,likes,comments,saves,average_watch_time,completion_rate
  &access_token={ACCESS_TOKEN}
```

### 3.2 必要スコープ（権限）

-   `instagram_basic`
-   `instagram_manage_insights`
-   `pages_show_list`
-   `instagram_graph_user_media`

API コールを成功させるには、Facebook アプリ審査で上記スコープの承認が必要です。

---

## 4. 注意事項

-   **対象制限**：取得対象は「自分が管理する Instagram ビジネス／クリエイターアカウントの投稿」のみに限られます。他人の投稿やパーソナルアカウントの動画は対象外です。
-   **更新頻度**：一部メトリクス（例：再生回数、リーチ）はリアルタイムではなく、24〜48 時間の遅延がある可能性があります。
-   **小規模アカウント制限**：フォロワー数が 100 未満のアカウントでは、インサイト取得自体が制限されることがあります。
-   **一部指標の非公開化**：ユーザーのプライバシー保護の観点から、2023 年以降、一部インタラクションメトリクス（ストーリーズの個別返信など）は API で取得できません。

---

## 5. API 機能の変遷

| 年   | 主な変更内容                                                                                                |
| ---- | ----------------------------------------------------------------------------------------------------------- |
| 2018 | Graph API v3.0 公開。従来の Instagram Legacy API は段階的に廃止へ。いいね・フォロー・コメント自動化は禁止。 |
| 2020 | Legacy API 完全廃止（3 月）。Graph API に一本化。                                                           |
| 2021 | Content Publishing API 公開（Instagram API 経由での自動投稿が公式対応）。                                   |
| 2022 | Reels API が Graph API で正式サポート開始（投稿・インサイト対応）。                                         |
| 2023 | ストーリーズ投稿 API が公式に開放。DM API も正式公開。                                                      |
| 2024 | Basic Display API が終了予定。すべての利用が Graph API に統一へ。                                           |

---

## 6. 今後の展望

Meta は Instagram API を「ビジネス向け活用」へと大きくシフトしており、動画インサイトの拡充や AI 連携機能の可能性が期待されます。

-   より詳細な視聴維持データの開放
-   自動応答連携の強化（DM・コメント）
-   コンバージョン指標との連携（広告とオーガニック投稿の統合）

---

## 7. まとめ

Instagram Graph API は、動画投稿のパフォーマンスを数値で可視化する強力なツールです。とくにリールに特化したメトリクスが整備されてきており、マーケティング戦略や投稿改善サイクルに有効活用できます。今後のアップデートにも注目しつつ、適切な権限管理とポリシー遵守のもとで活用を進めていくことが重要です。

# Instagram Graph API における動画メトリクス取得に関する詳細レポート（2025 年時点）

## 1. 概要

Instagram Graph API は、Meta（旧 Facebook）が提供する Instagram ビジネスおよびクリエイターアカウント向けの公式 API です。これにより、外部のアプリケーションから Instagram のデータにアクセスし、コンテンツの投稿、コメント管理、DM 対応、インサイト（分析指標）取得などが可能になります。

本レポートでは、特に Instagram 上の動画コンテンツ（フィード動画、リール、IGTV など）において、どのようなメトリクス（分析指標）が Graph API で取得可能なのかを詳述します。

---

## 2. API で取得可能な主な動画メトリクス

以下のメトリクスは、`/{ig-media-id}/insights` エンドポイントを使用して取得可能です（対象：ビジネス or クリエイターアカウントで投稿された動画）

### 🎥 動画メディア対応メトリクス一覧（主にリール動画に最適化）

| メトリクス名         | 説明                                | 備考                                |
| -------------------- | ----------------------------------- | ----------------------------------- |
| `plays`              | 動画の再生回数（3 秒以上）          | Reels・フィード共通                 |
| `reach`              | 動画を視聴したユニークアカウント数  |                                     |
| `impressions`        | 動画が画面に表示された総回数        |                                     |
| `likes`              | いいねの数                          |                                     |
| `comments`           | コメントの数                        |                                     |
| `saves`              | 保存された回数                      |                                     |
| `shares`             | 他のユーザーへの共有回数            | リール向け                          |
| `average_watch_time` | 視聴 1 回あたりの平均視聴時間（秒） | 主にリールで取得可能                |
| `completion_rate`    | 最後まで視聴された割合（完視聴率）  | 主にリールで取得可能                |
| `forward_taps`       | 次のリールへスワイプした回数        | インタラクション分析用（非公式）    |
| `backward_taps`      | 前のリールへ戻った回数              |                                     |
| `drop_off_points`    | 離脱が多かった時間帯                | グラフ形式で提供（非公開 API 含む） |

### 🔗 公式ドキュメント参照元：

-   [https://developers.facebook.com/docs/graph-api/reference/video/video_insights/#metrics](https://developers.facebook.com/docs/graph-api/reference/video/video_insights/#metrics)
-   [https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights/](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights/)

---

## 3. メトリクスの取得方法

### 3.1 エンドポイント例：

```http
GET https://graph.facebook.com/v17.0/{media_id}/insights
  ?metric=plays,reach,impressions,likes,comments,saves,average_watch_time,completion_rate
  &access_token={ACCESS_TOKEN}
```

### 3.2 必要スコープ（権限）

-   `instagram_basic`
-   `instagram_manage_insights`
-   `pages_show_list`
-   `instagram_graph_user_media`

API コールを成功させるには、Facebook アプリ審査で上記スコープの承認が必要です。

---

## 4. 注意事項

-   **対象制限**：取得対象は「自分が管理する Instagram ビジネス／クリエイターアカウントの投稿」のみに限られます。他人の投稿やパーソナルアカウントの動画は対象外です。
-   **更新頻度**：一部メトリクス（例：再生回数、リーチ）はリアルタイムではなく、24〜48 時間の遅延がある可能性があります。
-   **小規模アカウント制限**：フォロワー数が 100 未満のアカウントでは、インサイト取得自体が制限されることがあります。
-   **一部指標の非公開化**：ユーザーのプライバシー保護の観点から、2023 年以降、一部インタラクションメトリクス（ストーリーズの個別返信など）は API で取得できません。

---

## 5. API 機能の変遷

| 年   | 主な変更内容                                                                                                |
| ---- | ----------------------------------------------------------------------------------------------------------- |
| 2018 | Graph API v3.0 公開。従来の Instagram Legacy API は段階的に廃止へ。いいね・フォロー・コメント自動化は禁止。 |
| 2020 | Legacy API 完全廃止（3 月）。Graph API に一本化。                                                           |
| 2021 | Content Publishing API 公開（Instagram API 経由での自動投稿が公式対応）。                                   |
| 2022 | Reels API が Graph API で正式サポート開始（投稿・インサイト対応）。                                         |
| 2023 | ストーリーズ投稿 API が公式に開放。DM API も正式公開。                                                      |
| 2024 | Basic Display API が終了予定。すべての利用が Graph API に統一へ。                                           |

---

## 6. 今後の展望

Meta は Instagram API を「ビジネス向け活用」へと大きくシフトしており、動画インサイトの拡充や AI 連携機能の可能性が期待されます。

-   より詳細な視聴維持データの開放
-   自動応答連携の強化（DM・コメント）
-   コンバージョン指標との連携（広告とオーガニック投稿の統合）

---

## 7. まとめ

Instagram Graph API は、動画投稿のパフォーマンスを数値で可視化する強力なツールです。とくにリールに特化したメトリクスが整備されてきており、マーケティング戦略や投稿改善サイクルに有効活用できます。今後のアップデートにも注目しつつ、適切な権限管理とポリシー遵守のもとで活用を進めていくことが重要です。
