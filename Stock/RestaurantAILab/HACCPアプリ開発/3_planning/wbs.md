# HACCP アプリ開発 - 作業分解構造図 (WBS)

**プロジェクト期間:** 2025-05-01 - 2025-06-30  
**プロジェクトマネージャー:** 田中  
**作成日:** 2025-05-15  
**最終更新日:** 2025-05-17

## 1. プロジェクト概要

HACCP 温度記録アプリ（ハサッカーアプリ）の開発プロジェクト。衛生管理に必要な温度記録をモバイル/ウェブで行えるサービスを構築する。

## 2. 主要デリバラブル

-   ハサッカーアプリ（Web & モバイル）
-   管理者ダッシュボード
-   API & インフラ構築
-   ドキュメント一式

## 3. WBS 階層

```
1. 計画
   1.1 プロジェクト準備
       1.1.1 要求の整理 {due: 2025-04-15}   ✅
       1.1.2 要件定義書の作成 {due: 2025-04-16}   ✅
       1.1.3 システム構成方針作成 {due: 2025-04-17}   ✅
       1.1.4 タスク一覧化 {due: 2025-04-18}   ✅
       1.1.5 開発環境のセットアップ {due: 2025-04-19}   ✅
       1.1.6 AWS 環境の初期セットアップ {due: 2025-04-20}   ✅
       1.1.7 Git レポジトリの作成 {due: 2025-04-21}   ✅
   1.2 要件分析・設計
       1.2.1 システムアーキテクチャの設計 {due: 2025-04-22}   ✅
       1.2.2 使用ライブラリ・フレームワーク選定 {due: 2025-04-23}   ✅
       1.2.3 データベース設計 {due: 2025-04-24}   ✅
       1.2.4 API 設計 {due: 2025-04-25}   ✅
       1.2.5 セキュリティ設計 {due: 2025-04-26}

2. 開発
   2.1 バックエンド開発
       2.1.1 データベース構築 {due: 2025-05-11}   ✅
           2.1.1.1 Aurora DB 作成   ✅
           2.1.1.2 各種テーブル作成   ✅ {comment: 全テーブル作成・API routeデバッグ・店舗グループAPI/フロント統合完了, done: 2025-05-22}
           2.1.1.3 ユーザー・ロール作成   ⏳
           2.1.1.4 Prisma マイグレーション実行   ⏳
           2.1.1.5 初期データ投入   ⏳
           2.1.1.6 自動バックアップ設定   ✅
           2.1.1.7 リストア手順検証
       2.1.2 認証・権限管理 {due: 2025-05-18}
           2.1.2.1 LINE 認証連携実装
           2.1.2.2 メール/パスワード認証実装
           2.1.2.3 2 段階認証実装   ✅
           2.1.2.4 ロールベース権限管理実装   ✅
           2.1.2.5 認証チェックミドルウェア   ✅
       2.1.3 店舗・設備管理 API {due: 2025-05-23}   ✅
           2.1.3.1 店舗グループ管理 API 実装   ✅ {comment: フロントエンド統合も完了, done: 2025-05-22}
           2.1.3.2 店舗管理 API 実装   ✅
           2.1.3.3 設備管理 API 実装   ✅
       2.1.4 温度記録機能 {due: 2025-05-30}
           2.1.4.1 温度記録 API 実装
           2.1.4.2 写真アップロード処理実装
           2.1.4.3 音声→テキスト変換処理実装
           2.1.4.4 手動入力処理実装
           2.1.4.5 画像 30 日保持ジョブ実装
           2.1.4.6 カレンダー検索 API 実装
       2.1.5 アラート・通知機能 {due: 2025-06-04}
           2.1.5.1 基準値外アラート実装
           2.1.5.2 未記録アラート実装
           2.1.5.3 LINE 通知送信機能実装
           2.1.5.4 アクションガイダンス表示機能
       2.1.6 監査・アクセスログ機能 {due: 2025-06-07}
           2.1.6.1 ログイン操作ログ実装
           2.1.6.2 温度入力ログ実装
           2.1.6.3 データ修正ログ実装
       2.1.7 セキュリティ対策 {due: 2025-06-10}
           2.1.7.1 パスワードハッシュ化実装
           2.1.7.2 データベース暗号化実装
           2.1.7.3 HTTPS 有効化確認
   2.2 フロントエンド開発
       2.2.1 モックアップフェーズ (v0) {due: 2025-05-03}   ✅
           2.2.1.1 ワイヤーフレーム作成   ✅
           2.2.1.2 モックアップ作成   ✅
           2.2.1.3 UI/UX レビュー   ✅
       2.2.2 モノレポ構成移行 {due: 2025-05-08}   ✅
           2.2.2.1 TurboRepo/PNPM Workspace 設定   ✅
           2.2.2.2 モックアップをモノレポへ移行   ✅
       2.2.3 コンポーネント実装フェーズ {due: 2025-06-15}
           2.2.3.1 共通コンポーネント実装
               2.2.3.1.1 ログイン・認証画面
               2.2.3.1.2 ナビゲーション・メニュー
               2.2.3.1.3 エラーハンドリング
               2.2.3.1.4 レスポンシブデザイン
           2.2.3.2 店舗オーナー向け画面
               2.2.3.2.1 ダッシュボード画面
               2.2.3.2.2 店舗グループ管理画面
               2.2.3.2.3 店舗管理画面
               2.2.3.2.4 設備管理画面
               2.2.3.2.5 従業員管理画面
               2.2.3.2.6 データ確認・閲覧画面
               2.2.3.2.7 アラート設定画面
           2.2.3.3 従業員向け画面
               2.2.3.3.1 温度記録入力画面
               2.2.3.3.2 記録履歴確認画面
               2.2.3.3.3 アラート表示機能
           2.2.3.4 システム管理者向け画面
               2.2.3.4.1 管理者ダッシュボード
               2.2.3.4.2 システム設定画面
               2.2.3.4.3 ユーザー管理画面
               2.2.3.4.4 ログ閲覧画面
           2.2.3.5 モバイルUIでの表示・操作確認
           2.2.3.6 参照付きアイテム（店舗・設備等）削除時の挙動チェック   ✅
           2.2.3.7 管理者ダッシュボードと従業員入力画面のUIの統一
           2.2.3.8 温度入力UIのブラッシュアップ（デフォルト値設定など）
       2.2.4 カレンダー・履歴機能 {due: 2025-06-20}
           2.2.4.1 カレンダー UI 実装
           2.2.4.2 一括入力機能実装
   2.3 AWS インフラ構築
       2.3.1 AWS アカウント・組織設定 {due: 2025-05-12}   ✅
       2.3.2 IAM ロール・ポリシー設計 {due: 2025-05-13}   ⏳
       2.3.3 VPC & サブネット設計 {due: 2025-05-14}   ✅ {done: 2025-05-22}
       2.3.4 S3 バケット作成 {due: 2025-05-15}   ⏳
       2.3.5 RDS Proxy 設定 {due: 2025-05-16}   [-] {comment: 現時点では不要と判断}
       2.3.6 CloudWatch ログ & メトリクス設定 {due: 2025-05-17}   ⏳
       2.3.7 SNS / SES 設定 {due: 2025-05-18}
       2.3.8 Secrets Manager 設定 {due: 2025-05-19}
   2.4 CI/CD
       2.4.1 GitHub Actions ワークフロー作成 {due: 2025-05-26}
       2.4.2 テスト・ビルド・デプロイパイプライン {due: 2025-05-28}
       2.4.3 IaC (AWS CDK/Terraform) 化 {due: 2025-05-30}
   2.5 本番環境構築
       2.5.1 GitHubレポジトリをShefsRoomに移管
       2.5.2 Vercel実装をShefsRoomに移管
       2.5.3 各種権限設定の確認
       2.5.4 本番用DBの構築
       2.5.5 本番用S3バケットの構築
       2.5.6 本番用User Pool作成

3. テスト
   3.1 単体テスト
   3.2 統合テスト
   3.3 UI/UX テスト
   3.4 負荷テスト
   3.5 セキュリティテスト

4. ドキュメント作成
   4.1 設計書
   4.2運用マニュアル
   4.3 テスト結果報告書
   4.4 バックアップ・リストア手順書
   4.5 セキュリティ対策実施報告書
```

## 4. 進捗状況

-   インフラ構築フェーズ進行中
-   データベース構築と API 実装に並行して取り組み中
-   API route のデバッグが必要

## 5. 更新履歴

-   2025-05-15: 初版作成
-   2025-05-17: 進捗状況更新（インフラ構築、データベース構築の進捗を反映）
