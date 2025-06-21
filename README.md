# Minimalist Anime Style Converter

このプログラムは、Civitaiの「Minimalist Anime Style」LoRAモデルを使用して、任意のイラストをミニマリスト画風に変換するPythonアプリケーションです。

## 特徴

- Stable Diffusion 1.5 + LoRAを使用したimg2img変換
- 自動的なLoRAモデルのダウンロードと検証
- GPU/MPS/CPU対応（自動検出）
- Dockerによる簡単な環境構築
- コマンドライン引数による細かい調整

## 必要な環境

- Docker & Docker Compose
- （オプション）NVIDIA GPU + CUDA（高速化のため）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <このリポジトリのURL>
cd minimalist_anime_converter
```

### 2. 必要なディレクトリの作成

```bash
mkdir -p input output models
```

### 3. Dockerイメージのビルド

```bash
docker-compose build
```

## 使用方法

### 基本的な使用方法

1. 変換したい画像を `input` フォルダに配置
2. 以下のコマンドで変換を実行：

```bash
docker-compose run --rm minimalist-anime-converter python main.py /app/input/your_image.jpg -o /app/output/converted_image.jpg
```

### コマンドライン引数

```bash
python main.py <入力画像パス> [オプション]

必須引数:
  input                 入力画像のパス

オプション引数:
  -o, --output         出力画像のパス（指定しない場合は自動生成）
  -s, --strength       変換の強度 (0.0-1.0, デフォルト: 0.75)
  -g, --guidance-scale ガイダンススケール (デフォルト: 7.5)
  -n, --num-steps      推論ステップ数 (デフォルト: 20)
  -d, --device         使用デバイス (auto, cuda, mps, cpu)
```

### 使用例

```bash
# 基本的な変換
docker-compose run --rm minimalist-anime-converter python main.py /app/input/anime_girl.jpg

# 変換強度を調整（より強い変換）
docker-compose run --rm minimalist-anime-converter python main.py /app/input/anime_girl.jpg -s 0.9

# 高品質設定（時間がかかります）
docker-compose run --rm minimalist-anime-converter python main.py /app/input/anime_girl.jpg -n 50 -g 10.0

# 出力パスを指定
docker-compose run --rm minimalist-anime-converter python main.py /app/input/anime_girl.jpg -o /app/output/minimalist_result.jpg

# 変換強度やステップ数を調整
docker-compose run --rm minimalist-anime-converter python main.py /app/input/your_image.jpg -s 0.8 -n 30 -g 10.0 -o /app/output/result.jpg
```

## GPU使用について

NVIDIA GPUを使用する場合は、以下の手順を実行してください：

1. NVIDIA Container Toolkitをインストール
2. `docker-compose.yml`のGPU設定のコメントアウトを解除
3. 以下のコマンドでGPU対応版を実行：

```bash
docker-compose run --rm minimalist-anime-converter python main.py /app/input/your_image.jpg -d cuda
```

## パラメータの調整

### strength（変換強度）
- `0.1-0.3`: 軽微な変換（元の画像の特徴を保持）
- `0.5-0.7`: 中程度の変換（バランスの取れた結果）
- `0.8-1.0`: 強い変換（大幅にスタイルを変更）

### guidance_scale（ガイダンススケール）
- `5.0-7.5`: 自然な結果
- `7.5-12.0`: より強いプロンプト従属性
- `12.0+`: 過度に強調された結果（アーティファクトの可能性）

### num_inference_steps（推論ステップ数）
- `10-20`: 高速だが品質は中程度
- `20-30`: バランスの取れた品質と速度
- `50+`: 高品質だが時間がかかる

## トラブルシューティング

### メモリ不足エラー
- より小さな画像を使用する
- `--strength`を下げる
- CPUモードを使用する（`-d cpu`）

### LoRAモデルのダウンロードエラー
- インターネット接続を確認
- `models`フォルダの権限を確認
- 手動でモデルをダウンロードして配置

### 変換結果が期待と異なる
- `--strength`パラメータを調整
- `--guidance-scale`を変更
- より多くの推論ステップを使用（`-n 50`など）

## ファイル構成

```
minimalist_anime_converter/
├── main.py              # メインプログラム
├── requirements.txt     # Python依存関係
├── Dockerfile          # Dockerイメージ定義
├── docker-compose.yml  # Docker Compose設定
├── README.md           # このファイル
├── input/              # 入力画像フォルダ
├── output/             # 出力画像フォルダ
└── models/             # ダウンロードされたモデル
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

使用しているLoRAモデル「Minimalist Anime Style」は[Civitai](https://civitai.com/models/24833/minimalist-anime-style)で公開されており、作者はhortacreatorです。

## 注意事項

- 初回実行時は、Stable Diffusionモデル（約4GB）とLoRAモデル（約144MB）のダウンロードが必要です
- GPU使用時は大量のVRAMを消費します（8GB以上推奨）
- 生成される画像の品質は入力画像と設定パラメータに依存します
- xformersは依存関係の問題により除外されています（メモリ効率化は attention slicing で対応）
