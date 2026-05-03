# タイ語会話 音声サンプル — BL-0043 用

**作成日**: 2026-05-03
**作成者**: AI (mt cockpit-task-f2830076)
**用途**: BL-0043 — タイ語 STT (Speech-to-Text) / TTS (Text-to-Speech) 検証用のサンプル音声

---

## 1. ファイル一覧

| # | ファイル名 | 想定内容 | 容量 |
|:-:|---|---|---|
| 01 | `01_30 Essential Thai Phrases for Everyday Conversation｜Speak Thai Naturally.mp3` | 日常会話の30フレーズ。ネイティブ寄りの自然発話 | 約 1.9 MB |
| 02 | `02_5 Tips for learning to speak Thai in 6 Months.mp3` | タイ語学習の Tips、英・タイ混在の解説調 | 約 1.5 MB |
| 03 | `03_Thai Listening & Reading Practice｜My Weekend Routine (Easy Thai Story).mp3` | 「週末ルーティン」を題材にした優しいタイ語ストーリー | 約 1.6 MB |
| 04 | `04_Thai Listening Practice｜EP.1｜Beginner.mp3` | 初級向けリスニング教材 (EP.1) | 約 1.4 MB |

各ファイルの仕様:
- フォーマット: **MP3 / 16 kHz / モノラル / VBR (lame -q:a 4)**
- 由来: YouTube 検索 (`thai conversation natural daily` / `thai language listening practice short`) → `yt-dlp` で audio 抽出 → `ffmpeg` で 16kHz mono mp3 化
- ライセンス: 各動画の YouTube ライセンスに従う (**STT/TTS の社内検証目的**でのみ利用、再配布不可)
- 取得日時: 2026-05-03 09:50 頃

---

## 2. 想定する検証フロー (次アクション)

### Phase A — STT (Speech-to-Text) 精度比較

候補エンジン:
- **OpenAI Whisper** (`whisper-1` / `gpt-4o-mini-transcribe` API、もしくは Local `whisper.cpp medium`)
- **Azure Speech to Text** (Thai locale: `th-TH`)
- **Google Cloud Speech-to-Text** (`th-TH`)
- **Deepgram Nova-3** (Thai サポート)

評価項目:
1. **CER (Character Error Rate)** をネイティブ筆記訳と比較
2. 専門語・敬語・子音末などタイ語特有の難所が拾えるか
3. 単価・レイテンシ・バッチ処理の違い

### Phase B — TTS (Text-to-Speech) サンプル生成・比較

候補エンジン:
- **Azure Neural TTS** (`th-TH-PremwadeeNeural` / `th-TH-NiwatNeural`)
- **ElevenLabs** (Thai multilingual voice, v3)
- **Google Cloud TTS** (`th-TH-Neural2-C/D`)
- **OpenAI tts-1-hd** (multilingual)

評価項目:
1. **MOS (Mean Opinion Score) 風主観評価**: なめらかさ・声色・感情・敬語ニュアンス
2. 商品紹介・あいさつ・ホスピタリティ語彙の自然さ
3. 単価 / 1k 文字あたりコスト

### Phase C — 統合シナリオ (Voice Beauty Advisor 用)

サンプル音声を入力に、STT で書き起こし → そのテキストを TTS で再合成 → 元音声との聞き比べ。
JBeauty 美容アドバイザー POC (BL-0070 / BL-0041) で実装するパイプラインの素振り。

---

## 3. 注意事項

- 4 件すべて **学習・解説寄り**の音声で、純粋な「ネイティブ同士の自然会話」とは差がある。**フェーズ A の追加サンプル**として、タイドラマ抜粋・Podcast (e.g. `Cleverly Thai`, `Comprehensible Thai`) なども検討余地あり
- 著作権・利用規約: 検証 (内部評価) 目的に限り利用。検証ログや公開資料に音声を埋め込まない
- 商用 POC (BL-0041) で使う本番音声は、別途ライセンス整理か Pon さん側で素材調達

---

## 4. 関連 BL / 関連ファイル

- **BL-0043**: タイ語テキストのスピーチ対応確認 (本タスクの親 BL)
- **BL-0042**: タイ語テキストの確認 (ペア BL、テキスト品質チェック)
- **BL-0070**: JBeauty 要件一覧 (実利用先)
- **BL-0041**: バーチャル美容アドバイザー POC (実利用先)
- 関連プロジェクト: `~/RestaurantAILab/voice-beauty-advisor/`
