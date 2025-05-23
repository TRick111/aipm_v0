# HACCP アプリ開発 ユースケース一覧案（詳細付き）

## ペルソナ一覧

-   従業員
-   店舗オーナー
-   システム管理者

---

## 1. 従業員向けユースケース

-   温度記録入力（写真撮影・手動入力）
-   【詳細】冷蔵庫・冷凍庫の温度を、写真撮影または手動で入力し、記録する。入力時に設備を選択し、必要に応じて複数設備を連続入力できる。
-   記録履歴の閲覧
-   【詳細】自分が入力した温度記録の履歴を日付・設備ごとに一覧で確認できる。
-   アラート確認・対応
-   【詳細】自分に関連する設備で発生したアラート（基準値外・未記録）を一覧で確認し、必要に応じてコメントや対応内容を入力する。
-   ログイン（合言葉認証）
-   【詳細】所属店舗の合言葉（パスワード）を入力して従業員画面にログインする。
-   ログアウト
-   【詳細】従業員画面から安全にログアウトする。
-   入力時の確認画面表示
-   【詳細】温度記録入力後、確認画面で内容を見直し、修正または確定できる。

---

## 2. 店舗オーナー向けユースケース

-   設備管理（冷蔵庫・冷凍庫の登録・編集・削除、基準値設定）
-   【詳細】店舗に設置されている冷蔵庫・冷凍庫の情報を登録・編集・削除できる。各設備ごとに温度の基準値を設定する。
-   アラート管理（表示されたアラートの確認・対応）
-   【詳細】店舗内で発生したアラート（基準値外・未記録）を一覧で確認し、必要に応じて対応内容やコメントを記録する。
-   カレンダーから日付指定で記録確認
-   【詳細】カレンダー UI から特定の日付を選択し、その日の温度記録やアラート状況を確認できる。
-   記録データの修正（監査ログ付き）
-   【詳細】過去の温度記録データを修正し、修正内容は監査ログとして記録される。
-   店舗情報編集
-   【詳細】店舗名、住所、連絡先などの店舗情報を編集できる。
-   ログイン（ID/パスワード）
-   【詳細】店舗オーナー用の ID とパスワードで管理画面にログインする。
-   ログアウト
-   【詳細】管理画面から安全にログアウトする。
-   設定変更（通知先 LINE など）
-   【詳細】アラート通知先の LINE アカウントや通知方法などを設定・変更できる。

---

## 3. システム管理者向けユースケース

-   店舗グループ管理（追加・編集・削除）
-   【詳細】複数の店舗グループを追加・編集・削除できる。グループごとに管理者や基本情報を設定。
-   マスター管理（店舗数上限・各種マスター情報の管理）
-   【詳細】店舗数の上限や、設備種別などのマスター情報を管理・編集できる。
-   メンテナンス通知送信
-   【詳細】全店舗または特定店舗グループに対して、メンテナンスやお知らせ通知を送信できる。
-   システム全体設定
-   【詳細】システム全体の動作設定やセキュリティポリシーなどを管理できる。
-   アクセスログ閲覧
-   【詳細】ユーザーの操作履歴やシステムへのアクセスログを検索・閲覧できる。
-   ログイン（メール＋ 2 段階認証）
-   【詳細】システム管理者用のメールアドレスとパスワード、認証アプリによる 2 段階認証でログインする。
-   ログアウト
-   【詳細】管理画面から安全にログアウトする。

---
