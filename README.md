# 🎯 Data Science Portfolio – Regression Analysis

このリポジトリは、データサイエンス学習および実務力向上を目的としたポートフォリオ集です。  
各テーマでは、**課題設定 → データ分析 → モデル構築 → 評価・考察** のプロセスを一貫して実践しています。

本ページでは、`regression_analysis` ディレクトリ内で行った  
**重回帰分析（Multiple Linear Regression）** のプロジェクト概要をまとめます。

---

## 📘 プロジェクト概要

### 🎯 目的
複数の説明変数を用いて、目的変数（数値データ）を精度良く予測する重回帰モデルを構築する。  
線形関係の理解を通じて、データ構造の把握・特徴量設計・モデル評価手法を体系的に学ぶことを目的としています。

### 使用データセット
- UCI Machine Learning Repository の "Automobile" データセットを利用（Notebook: `multiple_linear_regression.ipynb`）。
- データは Notebook 内で `ucimlrepo.fetch_ucirepo(id=10)` により読み込み。

### 前処理と特徴量エンジニアリング（要点）
- 欠損値: `normalized-losses` を平均で補完し、残る欠損は削除。  
- 外れ値: IQR 法で各数値変数の外れ値を検出・除去（可視化関数を用いて確認）。  
- スケーリング: 標準化（StandardScaler）を適用してモデル学習に供することを基本とする。  
- 多重共線性対策:
  - VIF（variance inflation factor）を算出して問題のある特徴を検討。
  - 高相関（|r| > 0.85）に基づき冗長な特徴を削除（例: `city-mpg`, `horsepower`, `num-of-cylinders`, `length`, `wheel-base` を削除して代表変数を残す方針）。

### モデルと評価
- 実装モデル:
  - 線形回帰 (LinearRegression)
  - Ridge 回帰 (Ridge)
  - RidgeCV による α の自動選択
- 評価:
  - ホールドアウト（train/test split）による R²
  - K-Fold Cross-Validation（5-fold）での平均 R² と標準偏差
- 比較と可視化は Notebook 内の `evaluate_and_visualize_models` にて実行。生成画像:
  - `correlation_matrix.png`（相関行列）
  - `model_comparison.png`（モデル比較の棒グラフ）

### 主要な結果（Notebook の結論より）
- 初期の線形回帰では学習データに対して過学習の兆候あり（例: 学習 R² 高く、テスト R² 低い）。  
- 特徴削減＋正則化の導入で改善を確認:
  - 初期（過学習）例: R²(train) ≈ 0.835, R²(test) ≈ 0.335
  - RidgeCV により最適化したモデル（alpha ≈ 10.0 の例）:  
    - R²(train) ≈ 0.813  
    - R²(test) ≈ 0.593  
    - 5-fold CV 平均 R² ≈ 0.638 ± 0.191
- 結論: 多重共線性の除去と L2 正則化（Ridge/RidgeCV）により汎化性能が改善。

### 再現方法（簡易手順）
1. リポジトリをクローンして作業環境（Python、必要ライブラリ）を用意。  
2. `multiple_linear_regression.ipynb` を Jupyter で開き、セル順に実行する。  
3. 実行により上記の画像ファイル（`correlation_matrix.png`, `model_comparison.png`）が出力され、各セルで R² 等の結果が表示される。

### 今後の改善案
- Lasso や ElasticNet の検討で変数選択を自動化する。  
- PCA を用いた次元削減と解釈性のバランス検討。  
- 外れ値の取り扱いをケース別に分け、ロバストな手法を検証。

