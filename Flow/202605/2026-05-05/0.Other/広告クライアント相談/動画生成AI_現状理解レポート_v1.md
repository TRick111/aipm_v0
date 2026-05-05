# 動画生成AI 現状理解レポート v1

**作成日**: 2026-05-05
**対象 BL**: BL-0087（広告クライアント相談 / 動画生成AI 現状理解）
**目的**: 広告系クライアント（PR動画制作）からのAI相談に向け、土台となる「動画生成AIの現状」を体系的に整理する。クライアントの個別課題は未受領のため、本書は **業界俯瞰の地図** に徹する。

---

## エグゼクティブサマリー

- 動画生成AIは **2022年（研究プロトタイプ）→ 2023年（商用化開始）→ 2024年（破壊的ブレイクスルー＝Sora）→ 2025年（音声同時生成・実用品質）→ 2026年（用途別最適化＋業界再編）** という時系列で急進化した。
- 2026年5月時点で「総合力」のトップは **Google Veo 3.1**、「映像美」は **Runway Gen-4.5**、「コスパ・無料枠」は **Kuaishou Kling 3.0 / 2.6**、「物語性・音声同期」は **ByteDance Seedance 2.0**、「広告自動生成」は **Adobe Firefly Video / Amazon Ads AI Video Generator**。
- **OpenAI Sora 2 は 2026/4/26 にアプリ・Web 終了、API も 2026/9/24 に停止予定**。先行者でありながらコスト構造と訴訟リスクで撤退、業界の主導権は Google・中国勢・Runway・Adobe に分散した。
- モデルは **Latent Diffusion + DiT（Diffusion Transformer）** が事実上の標準アーキテクチャで、Sora 以降「spacetime patch」を transformer token とする方式が主流。
- サービス層は **(A) 基盤モデル（Sora/Veo/Kling 等）/ (B) クリエイター向けスタジオ（Runway/Pika/Luma/Adobe 等）/ (C) アバター・トーキングヘッド（HeyGen/Synthesia 等）/ (D) 広告特化（Creatify/Waymark/Amazon Ads 等）/ (E) 解説・短尺自動生成（NoLang/Vrew 等）** の5層に整理できる。
- 広告での実用性は **「30秒マスター動画→25バリエーション自動展開」「1日50パターンA/Bテスト」** という運用で、制作コスト 80% 削減レンジに到達。一方で **EU AI Act / 米FTC が AI 生成広告の開示義務** を課しており、法務・契約面の整備が必須。

---

## 第1部：動画生成AIモデル提供企業と主要モデル

### 1-1. プレイヤー一覧（2026年5月時点）

| 区分 | 提供元 | 国 | 代表モデル | 公開 / 更新 |
|---|---|---|---|---|
| **米テック大手** | OpenAI | 🇺🇸 | Sora / Sora 2（**終了予定**） | 2024/2 → 2025/9（Sora 2）→ 2026/4 終了 |
| | Google DeepMind | 🇺🇸 | Veo / Veo 2 / Veo 3 / Veo 3.1 | 2024/5 → 2025/5 (Veo 3) → 2026 |
| | Meta AI | 🇺🇸 | Make-A-Video（研究） | 2022/9 |
| | Adobe | 🇺🇸 | Firefly Video Model | 2024〜2026 |
| | Amazon | 🇺🇸 | Amazon Ads AI Video Generator | 2026/4 (AU 展開) |
| **米スタートアップ** | Runway | 🇺🇸 | Gen-1/2/3/4/4.5 | 2023/2 → 2026 |
| | Pika Labs | 🇺🇸 | Pika 1.0 / 2.0 / 2.5 | 2023〜2026 |
| | Luma AI | 🇺🇸 | Dream Machine | 2024/6〜 |
| | Stability AI | 🇬🇧 | Stable Video Diffusion (SVD) | 2023/11 |
| | Genmo | 🇺🇸 | Mochi 1（OSS） | 2024/10 |
| | Lightricks | 🇮🇱 | LTX-Video / LTX-2 | 2025〜2026/1 |
| | Haiper | 🇬🇧 | Haiper 2.0 | 2024〜 |
| **中国大手** | ByteDance | 🇨🇳 | Seedance 1.0 / 2.0（Dreamina / Jimeng AI） | 2024 → 2026/2 |
| | Kuaishou | 🇨🇳 | Kling 1.0/2.0/2.6/3.0/3.0 Omni | 2024/6 → 2026/2 |
| | Tencent | 🇨🇳 | HunyuanVideo / 1.5（OSS あり） | 2024 末〜2026 |
| | Alibaba | 🇨🇳 | Wan 2.1 / Happy Horse | 2025〜2026 |
| | MiniMax | 🇨🇳 | Hailuo（海螺） | 2024〜 |
| | Shengshu (生数科技) | 🇨🇳 | Vidu | 2024〜 |
| **OSS / 研究系** | THUDM (清華) | 🇨🇳 | CogVideo / CogVideoX | 2022 → 2024 |
| | Vchitect | 🇨🇳 | Latte（DiT） | 2024 |
| | SkyReels | 🇨🇳 | SkyReels V1 | 2025 |
| | MAGI / Waver | - | MAGI-1 / Waver 1.0 | 2025〜 |

### 1-2. 「有力モデル Top 7」と評価軸（2026年5月）

| モデル | 強み | 弱み | 評価 |
|---|---|---|---|
| **Google Veo 3.1** | プロンプト忠実度 / ネイティブ4K / 音声同時生成 / Gemini API 経由 | プロンプト記述に習熟必要 | **総合力 No.1** |
| **Runway Gen-4.5** | 映像美・カメラ操作・モーションブラシ・キャラ一貫性 / Artificial Analysis Elo 1247 でトップ | 価格、長尺はまだ短い | **クリエイター・映画寄り No.1** |
| **Kuaishou Kling 3.0 Omni** | 多シーン一貫性 / 5言語リップシンク / 無料枠が大きい / 月$5で3分動画 | 西側コンプラ懸念 | **コスパ・多言語 No.1** |
| **ByteDance Seedance 2.0** | 音声・動画統合生成 / 8言語 phoneme リップシンク / 24fps 2K | 海外アクセス限定的 | **物語・トーキング系 No.1** |
| **Tencent Hunyuan Video 1.5** | 8.3B param で高品質 / OSS | 商用展開は中国寄り | **OSS 系 高品質** |
| **Alibaba Wan 2.1** | T2V・I2V・編集・V2A 統合 / 多言語 | 知名度はまだ低い | **OSS 系 統合力 No.1** |
| **Lightricks LTX-2** | 4K/50fps/20秒 / OSS / 民生GPUで動く | スタジオ機能はこれから | **OSS 系 軽量 No.1** |

> **OpenAI Sora 2 は 2026/4/26 で終了**。理由は (1) 高解像度生成の計算コスト、(2) 学習データの法的論争、(3) コア事業（ChatGPT/エンタープライズ）への集中。後継は ChatGPT 内部統合か Enterprise API へ吸収予定だが正式発表なし。

### 1-3. アーキテクチャの分類

すべての主要モデルは下記の系譜にある。

```
Pixel-space Diffusion (旧)
  └─ Latent Diffusion Model (LDM)        ← Stable Video Diffusion
       └─ U-Net 系                        ← Lumiere, Make-A-Video 系
       └─ Diffusion Transformer (DiT) 系  ← Sora, Veo, Kling, Seedance, Mochi, LTX
            ├─ spacetime patch tokenization (Sora 流派)
            └─ spatio-temporal token + decomposed transformer (Latte 流派)
```

- **DiT が事実上の業界標準**。U-Net を Transformer に置き換え、可変解像度・可変尺・画像も同パイプラインで扱える。
- 2025〜2026 の主要進化軸：
  - **Multi-step consistency distillation**（推論の高速化）
  - **音声・映像の joint generation**（Veo 3, Sora 2, Kling 3 Omni, Seedance 2）
  - **Multi-shot subject consistency**（Kling 3）
  - **4K / 50fps / 20秒+**（LTX-2, Veo 3.1）

---

## 第2部：動画生成サービスの分類と地図

### 2-1. レイヤー別に5層で整理

```
[A] 基盤モデル提供層
    Sora API (~9/24終了), Veo (Gemini API), Kling API,
    Runway API, Stability AI, Replicate, Hugging Face Inference

[B] クリエイター向け統合スタジオ
    Runway, Pika, Luma Dream Machine, Haiper, Genmo,
    Adobe Firefly Video, CapCut/Dreamina, Magic Hour, ComfyUI

[C] アバター・トーキングヘッド系
    HeyGen, Synthesia, D-ID, Colossyan, OmniHuman,
    AvaMo（日本）

[D] 広告・マーケ特化
    Creatify, Waymark, Amazon Ads AI Video Generator,
    AdCreative.ai, invideo, Pictory

[E] 解説・短尺・国内向け
    NoLang（東大発）, Vrew（VoyagerX, 韓国発・日本展開）,
    その他 ScaleX 系記事に列挙される国内 13〜22 サービス
```

### 2-2. 各レイヤーの特徴

#### [A] 基盤モデル層
- 売り：最高品質 / プロンプト→生映像の生成力
- 顧客：開発者、上位サービスベンダー
- 課金：従量（クリップ/秒単位）。Veo は Gemini API 経由の従量課金、Runway は SaaS+API。

#### [B] クリエイター向け統合スタジオ
- 売り：UIで触れる / カメラ制御・モーションブラシ・キャラ一貫性などの「演出」機能
- 顧客：プロ/セミプロ動画クリエイター、デザイナー
- **Runway Gen-4.5** が映像美のフラッグシップ。**Adobe Firefly Video** は Premiere Pro 内でタイムラインに直挿入でき、Kling 3.0 / 3.0 Omni を 2026/4 から内蔵（Adobe NAB 2026 発表）。

#### [C] アバター・トーキングヘッド系
- 売り：人物アバターに台本を喋らせる、リップシンク、多言語ローカライズ
- 顧客：研修動画、社内コミュニケーション、SNS マーケ、国際展開
- **Synthesia** が Fortune 500 の事実上のデファクト。**HeyGen** はマーケ・SNS 寄りで Avatar IV エンジンが微表情・ジェスチャ強化。**OmniHuman** は1枚画像＋音声からアバター動画。日本では **AvaMo**（オフショアカンパニー、月3,900円）が個人向けに参入。
- ※Hour One は Wix 買収後にディスコン。

#### [D] 広告・マーケ特化
- 売り：商品画像/LP→広告動画の自動化、A/B バリエーション量産
- 顧客：EC、中小企業、運用型広告チーム
- **Amazon Ads AI Video Generator** は 2026/4 に豪州で先行展開、商品 ASIN から動画広告を自動生成。**Creatify** は SNS 広告フォーマット特化。**Waymark** は地域中小ビジネス向け。

#### [E] 解説・短尺・国内向け
- 売り：日本語に最適化、テキスト/PDF/Web ページから解説動画を自動生成、既存の動画編集 UX に近い
- 顧客：BtoB マーケ、教育、社内コミュニケーション
- **NoLang**（東大発・株式会社Mavericks、2024/7 開始、ユーザー13万超、法人50社超、2025/7「NoLang 4.0」+ API、18言語対応）。**Vrew**（VoyagerX、2020〜、テキストエディタ感覚で動画編集）。

### 2-3. 「商用利用 / 著作権」の分類軸（重要）

広告クライアントを支援する場合、モデル/サービスの選定は **品質よりまず権利** で絞り込むべき。

| 観点 | 内容 | 注意点 |
|---|---|---|
| **学習データの来歴** | Adobe Firefly は Adobe Stock + ライセンス済データ中心（"commercially safe" を主張）。Sora/Runway/Kling 等は不透明・係争中の領域 | 大手ナショナルクライアント案件は Firefly や ライセンス保証付きを推奨 |
| **生成物の著作権** | 文化庁（日本）：人が意図と工夫を持って関与すれば著作権が認められうる。完全自動生成は認められない可能性 | プロンプトと選別を「人の創作的寄与」として記録に残す |
| **商用利用可否** | Pika 等は Pro プラン（$70/月）以上で商用可。無料/個人プランは不可のことが多い | サービスごとに「プランごとの商用可否」を契約時にチェック |
| **AI 生成表示義務** | EU AI Act：AI 生成広告の開示義務。米 FTC：AI 証言・推薦の開示義務 | 字幕・概要欄・契約書での開示文言テンプレを準備 |
| **肖像権・声優・タレント** | アバター系で実在人物を再現する場合、本人同意・出演契約の改訂が必要 | 「学習元・出力先・商用範囲」の3点を契約に明記 |

---

## 第3部：時系列（2022〜2026）

### 2022 — 研究プロトタイプ期
- **2022 春〜夏**：CogVideo（清華・THUDM）— 大規模 text-to-video の先駆け。
- **2022/9**：Meta **Make-A-Video** — 短尺アニメをテキストから生成。
- **2022/9**：Google Brain **Phenaki** — より長く一貫性のある映像生成の概念実証。
- **2022/10**：Google **Imagen Video** — 高解像度 text-to-video の早期実験。
- 状態：「数秒の不気味な動く絵」レベル。一般公開なし。

### 2023 — 商用化開始
- **2023/2**：**Runway Gen-1** — 商用 video-to-video。
- **2023/6**：**Runway Gen-2** — text-to-video 公開。**動画生成 SaaS の幕開け**。
- **2023/夏**：**Pika Labs** が Discord ベースで急拡大、クリエイターコミュニティが熱狂。
- **2023/11/21**：Stability AI **Stable Video Diffusion** — 初の主要 OSS 動画生成モデル、GitHub 公開。

### 2024 — ブレイクスルー期
- **2024/1/23**：Google Research **Lumiere** 発表（U-Net、時間一貫性で高評価）。
- **2024/2/15**：**OpenAI Sora 初公開**。クオリティと長さ（最大1分）で業界が騒然、生成AI動画の公衆認知が決定的に高まる。
- **2024/5/14**：Google **Veo** 発表（I/O）— text/image/video 入力対応。
- **2024/6**：Kuaishou **Kling 1.0**（中国勢の本格参入の合図）。
- **2024/6**：Luma AI **Dream Machine** 公開。
- **2024/夏〜秋**：Runway **Gen-3 Alpha**、Pika **1.0**、MiniMax **Hailuo**、Shengshu **Vidu** が相次ぎ登場。
- **2024/10**：Genmo **Mochi 1** オープンソース化（10B param、AsymmDiT）。
- **2024/末**：**Tencent HunyuanVideo**（13B、OSS）、**OpenAI Sora 一般公開**（ChatGPT Plus/Pro、米加）。

### 2025 — 実用品質と音声統合
- **2025/前半**：**Alibaba Wan 2.1**（T2V/I2V/編集/V2A 統合 OSS）、**Lightricks LTX-Video** 公開。
- **2025/5/20**：**Google Veo 3** — **映像と音声/音声合成を1パイプラインで生成する初の主要モデル**。
- **2025/9/30**：**OpenAI Sora 2** — リアリティ・一貫性・長尺ストーリー強化、リップシンク/環境音/ダイアログ。
- **2025/末**：**Kling 2.6**（音声・映像同時生成）、**HunyuanVideo 1.5**。

### 2026 — 用途別最適化と業界再編
- **2026/1**：Lightricks **LTX-2**（4K/50fps/20秒、19B param、OSS、民生 GPU）。
- **2026/2**：**ByteDance Seedance 2.0**（Dreamina/Jimeng）— 8言語 phoneme リップシンク、unified multimodal audio-video。
- **2026/2**：**Kling 3.0**（multi-shot subject consistency）。同 2025/12 に Kling 2.6 で音声同時生成を獲得済。
- **2026/2**：Alibaba **Happy Horse** — 一部ベンチマークで Seedance 超えと報告。
- **2026/3/24**：**OpenAI、Sora の終了をXで発表**。
- **2026/4/15**：Adobe NAB 2026 — Firefly に **Kling 3.0 / 3.0 Omni を内蔵**、Premiere Pro の Generative AI パネル統合、"Quick Cut" など。
- **2026/4/26**：**Sora の Web/アプリ終了**。
- **2026/4**：**Amazon Ads AI Video Generator** が豪州で広告主向けに公開。
- **2026/9/24**（予定）：**Sora API 完全終了**。
- **2026/2〜春**：「中国旧正月 AI 戦争」— ByteDance/Alibaba/Tencent/Baidu/Kuaishou がモデルや無料クーポンを一斉ローンチ。
- **(参考)** Veo 3.1、Runway Gen-4.5 が 2026/Q1 までに総合・映像美の双璧として確立。

---

## 第4部：広告・PR動画への適用観点（クライアント相談の前さばき）

> クライアントの具体課題はまだ受領していないが、相談の典型パターンに対し「どこを掘れるか」の見取り図を作っておく。

### 4-1. 想定される相談類型と対応モデル/サービス

| 相談類型 | 推奨レイヤー | 第一候補 | 第二候補 |
|---|---|---|---|
| 「タレント風アバターで多言語 PR を量産したい」 | [C] アバター | Synthesia / HeyGen Avatar IV | OmniHuman, AvaMo |
| 「商品画像から SNS 広告動画を月100本作りたい」 | [D] 広告特化 | Creatify / Amazon Ads AI Video Generator | Waymark, AdCreative |
| 「クライアントブランドの世界観で 30秒 CM を作りたい」 | [B] スタジオ | Runway Gen-4.5 / Adobe Firefly Video（Premiere 統合） | Veo 3.1（Gemini API） |
| 「商品紹介・解説動画を日本語で自動生成したい」 | [E] 国内 | NoLang 4.0 / Vrew | invideo, Pictory |
| 「コスト最優先で大量バリエーションを試したい」 | [B]/[A] 中国系 | Kling 3.0（無料枠＋月$5で3分） | Hailuo, Seedance 2.0 |
| 「制作工程に組み込みたい（既存 Premiere 環境）」 | [B] | Adobe Firefly Video（Quick Cut, 内蔵 Kling） | Runway（API + プラグイン） |

### 4-2. 「制作会社が押さえるべき」5観点

1. **権利クリーン度** — Adobe Firefly や、ライセンス保証を打ち出すサービスを「ナショナルクライアント案件の最終納品ライン」に据える。Kling/Sora 系は試作・社内のみで使う運用も可。
2. **ブランド一貫性** — 2026年は「ブランドガイドライン・カラーパレット・過去成功作」をエンタープライズAIにアップして使うのが標準。Adobe Firefly の Custom Models、Synthesia のブランドアセット機能などが該当。
3. **マスター→バリエーション展開** — 30秒・16:9 を1本作って、AI で 15〜25 本のフォーマット違いに展開する運用フローが業界標準化。
4. **A/B テスト前提のスケール** — 「50パターン同時に生成 → 運用結果で評価」が現実的になった。クリエイター個人の感覚ではなく、運用データで決めるワークフローが要点。
5. **AI 表示義務とクライアント契約** — EU AI Act、米 FTC、日本でも文化庁の指針整理が進む。**「AI 利用の開示」「学習データ来歴」「生成物の著作権帰属」「禁止用途」をクライアント契約のテンプレに明記**しておくと、後の事故が防げる。

### 4-3. 「クライアントから出やすい質問」想定リスト

- Q. 自社タレント・モデルの肖像をどこまで AI で再利用できる？
- Q. 既存の TVCM 素材を学習させて、自社専用モデルを作れる？（→ Firefly Custom Models / Runway Custom Models）
- Q. 海外展開向けに 18言語 でナレーション差し替えしたい（→ NoLang 18言語、Synthesia/HeyGen 多言語）
- Q. 大手代理店・媒体（YouTube / Meta / TikTok / CTV）の入稿規定を満たす？（→ 1080p min / 4K preferred、プロ音声ミックスで標準対応可）
- Q. 「AI で作りました」と表示する義務はある？（→ EU/US は明確に Yes、日本も実質 Yes 寄り）
- Q. プロンプト・元素材・生成物の権利は誰のもの？（→ サービス利用規約と、社内・クライアント契約で二段構え）
- Q. インハウス内製化と外部発注、どちらが合理的？（→ 用途別。広告 D 層・解説 E 層は内製化しやすい。CM/B層は当面プロの介在が必要）

---

## 第5部：このレポートの使い方と次アクション

### 使い方
- **第1部**：モデル/企業の地図。クライアントに「主要プレイヤー」を説明する時の出典。
- **第2部**：レイヤー分類。クライアントの相談を **どのレイヤーの問題か** で振り分けるフレーム。
- **第3部**：時系列。クライアントが「なぜいま」と聞いたときの説明根拠。
- **第4部**：適用観点。具体相談を受けた瞬間に「どのサービス候補を検討するか」の初動ガイド。

### 次に深掘りすべき論点（クライアント課題が来てから判断）
1. クライアントの **PR動画の用途**（CM/SNS/解説/社内）と **既存制作フロー**（Premiere/After Effects 中心か、撮影中心か）。
2. クライアントの **ブランド権利体制**（タレント契約、肖像権、楽曲権利）。
3. **本数・頻度・予算**の現実値（→ B層スタジオ vs D層広告特化の選定軸）。
4. **多言語/海外展開**の有無（→ Synthesia/HeyGen/NoLang/Kling の選定）。
5. **生成物の著作権・開示**に関するクライアント側のポリシー有無（→ 法務同席の要否を判断）。

### 想定される追加 BL（このレポート確認後の田中さん判断次第）
- BL: 広告クライアント案件の課題ヒアリング設計（質問票 + 90分セッション設計）
- BL: 主要サービス（Runway / Veo / Adobe Firefly / Kling / HeyGen / NoLang）の **実機ベンチマーク実施計画**
- BL: AI 生成広告の **法務チェックリスト**（EU AI Act / FTC / 文化庁指針 / 肖像権 / 楽曲）の整備

---

## 付録 A：用語集

| 用語 | 意味 |
|---|---|
| T2V (Text-to-Video) | テキストプロンプトから動画を生成 |
| I2V (Image-to-Video) | 静止画 + プロンプトで動画化 |
| V2V (Video-to-Video) | 既存動画にスタイル/モーション転送 |
| V2A (Video-to-Audio) | 動画から効果音/BGM を生成 |
| Lip-Sync | 音声に合わせて口の動きを合成 |
| LDM (Latent Diffusion Model) | 圧縮された潜在空間で拡散を行う方式 |
| DiT (Diffusion Transformer) | U-Net の代わりに Transformer を使う拡散モデル |
| Spacetime Patch | 時空間に分割した動画パッチ。Sora 流派の token 単位 |
| Multi-shot Consistency | 複数カット間で被写体の一貫性を保つ機能 |
| Joint Audio-Video Generation | 映像と音声を1モデルで同時生成 |

## 付録 B：本レポートが参照した主要ソース

### 比較・市場
- Pinggy: Best Video Generation AI Models in 2026 — https://pinggy.io/blog/best_video_generation_ai_models/
- Pixflow: Best AI Video Generator in 2026 — https://pixflow.net/blog/best-ai-video-generator/
- DataCamp: Top 10 Video Generation Models of 2026 — https://www.datacamp.com/blog/top-video-generation-models
- Atlas Cloud: Best AI Video Generation Models in 2026 — https://www.atlascloud.ai/blog/guides/best-ai-video-generation-models-2026
- TeamDay.ai: Best AI Video Models 2026 (17 ranked) — https://www.teamday.ai/blog/best-ai-video-models-2026
- LaoZhang AI: Sora 2 vs Veo 3.1 vs Runway — https://blog.laozhang.ai/en/posts/best-ai-video-model

### 時系列・歴史
- Wikipedia: Sora (text-to-video model) — https://en.wikipedia.org/wiki/Sora_(text-to-video_model)
- Wikipedia: Text-to-video model — https://en.wikipedia.org/wiki/Text-to-video_model
- LearnOpenCV: Video Generation — VDM to Veo2 and Sora — https://learnopencv.com/video-generation-models/
- Imagine.art: Evolution of AI Video Generation — https://www.imagine.art/blogs/evolution-of-ai-video-generation
- VC Cafe: Rapid Evolution of Generative AI Video — https://www.vccafe.com/2024/01/17/the-rapid-evolution-of-generative-ai-video-footage/

### 中国勢
- Second Talent: 7 Best Chinese AI Video Generation Tools — https://www.secondtalent.com/resources/chinese-ai-video-generation-tools/
- CNBC: Alibaba RynnBrain, ByteDance Seedance 2.0 — https://www.cnbc.com/2026/02/14/new-china-ai-models-alibaba-bytedance-seedance-kuaishou-kling.html

### OSS
- Hyperstack: 7 Best Open Source Video Generation Models — https://www.hyperstack.cloud/blog/case-study/best-open-source-video-generation-models
- Hugging Face: State of open video generation models — https://huggingface.co/blog/video_gen
- ComfyOnline: open source video generation comparisons — https://www.comfyonline.app/blog/open-source-video-generation-models-comparisons

### アーキテクチャ
- Lil'Log: Diffusion Models for Video Generation — https://lilianweng.github.io/posts/2024-04-12-diffusion-video/
- OpenAI: Video generation models as world simulators — https://openai.com/index/video-generation-models-as-world-simulators/
- Latte (TMLR 2025) — https://github.com/Vchitect/Latte
- Lightly: Diffusion Transformers Explained — https://www.lightly.ai/blog/diffusion-transformers-dit

### Sora 終了
- OpenAI Help Center: Sora discontinuation — https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation
- MindStudio: Why OpenAI Killed Sora — https://www.mindstudio.ai/blog/why-openai-killed-sora-ai-video-generation-future
- Podcastvideos: OpenAI Shuts Down Sora 2 — https://www.podcastvideos.com/articles/openai-sora-discontinued-disney-deal-veo-update/

### アバター・広告
- Synthesia: HeyGen Alternatives — https://www.synthesia.io/post/heygen-alternatives-competitors
- WaveSpeedAI: HeyGen vs Synthesia 2026 — https://wavespeed.ai/blog/posts/heygen-vs-synthesia-comparison-2026/
- Digen: AI Video Generation for Marketing 2026 — https://resource.digen.ai/ai-video-generation-for-marketing-2026/
- Cometly: 9 Best AI Marketing Video Generators for Ads — https://www.cometly.com/post/ai-marketing-video-generator
- AdCreate: How to Make Commercial Ads with AI in 2026 — https://adcreate.com/blog/how-to-make-commercial-ads-ai-2026

### 日本国内
- NoLang 公式 — https://no-lang.com/
- PR TIMES: NoLang 4.0 リリース — https://prtimes.jp/main/html/rd/p/000000010.000129953.html
- Vrew 公式 — https://vrew.ai/ja/
- ScaleX: 動画生成AIサービス13選 — https://scale-x.co.jp/column/1080/
- AI-Market: 動画生成AIサービス22選 — https://ai-market.jp/services/video-generative-ai/
- DOT SCENE: 生成AI動画の著作権 — https://dotscene.co.jp/media-ai-film/ai-video-copyright/
- AI 経営総合研究所: 動画生成AI 商用利用ガイド — https://ai-keiei.shift-ai.co.jp/video-generation-ai-commercial-use-guide-2025/

### Adobe
- Adobe Blog: Firefly + Premiere 2026/4 アップデート — https://blog.adobe.com/en/publish/2026/04/15/adobe-extends-leadership-video-unleashing-new-ai-powered-creation-firefly-reinventing-color-editors-in-premiere

---

**作成者**: Claude (mt-cli 経由)
**所要**: 主要ソース約25件の web search を直列・並列で実施しサマリ
**レビュー状態**: 未レビュー（review_state=unreviewed）
**次の更新トリガー**: クライアントから具体課題ヒアリング後 / Sora API 終了（2026/9/24）後の市場再整理時
