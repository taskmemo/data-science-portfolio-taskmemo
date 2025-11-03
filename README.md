# 🚕 Taxi Trajectory Regression (PKDD 2015)

このプロジェクトは、PKDD 2015 の Taxi Service Trajectory Prediction コンペティションの再現・学習用実装です。与えられたタクシー軌跡の一部から最終目的地（緯度・経度）を予測します。

## 概要
- 目的: 時系列・地理空間データの取り扱いを学び、ベースラインから改善までのワークフローを示す。  
- 手法: 特徴量エンジニアリング（出発地点、部分距離、時間特徴など）→ 回帰モデル（線形回帰、RandomForest、XGBoost、LightGBM）→ 評価は Haversine 距離（km）。

## ファイル構成（主要）
- taxi_trajectory.ipynb — データ読み込み、EDA、特徴量作成、モデル学習、ハイパーパラメータチューニング（Optuna）を含むノートブック
- data/ — データファイル配置場所（下記参照）
- meta.md — データ説明とノート
- README.md — 本ファイル

## データ
ノートブックは以下のパスにある CSV を想定します（相対パス/絶対パスはノートブック内の読み込みコードを参照）。
- data/train.csv
- data/test.csv
- data/metaData_taxistandsID_name_GPSlocation.csv

ノートブックでは、POLYLINE カラム（文字列化された [lon, lat] の配列）を ast.literal_eval でリスト化して特徴を作成します。

## 依存関係
主要ライブラリ:
- python >= 3.8
- pandas, numpy
- scikit-learn
- xgboost
- lightgbm
- optuna
- matplotlib

## 実行手順（再現）
1. data フォルダに train.csv / test.csv / metaData... を配置する。  
2. 仮想環境を作成し、上記依存関係をインストールする。  
```bash
uv init 
uv add pandas numpy scikit-learn xgboost lightgbm optuna matplotlib
```
3. JupyterLab / Jupyter Notebook で taxi_trajectory.ipynb を開き、順にセルを実行する。  
   - ノートブックはサンプリング、特徴量作成、モデル学習、クロスバリデーション、Optuna によるチューニングまで含む。  
4. 最終的な submission CSV はノートブック内で以下に保存される（該当セルを確認）:
   - data/taxi_trajectory_submission.csv

## 主要な実験結果（ノートブックより）
- ベースライン（RandomForestRegressor）によるサンプル実験:  
  - public score: 3.84330 km  
  - private score: 4.03655 km

- LightGBM + Optuna チューニング後:
  - Mean error : 2.668 ± 0.033 km
  
## ノート（実装上のポイント）
- 部分距離: テストデータの分布から 30 ステップまでの距離を特徴量として使用。  
- Haversine 距離を評価指標として使用（学習には直接は使わないが評価で重要）。  
- CALL_TYPE / TIMESTAMP から追加特徴を作成（ワンホット、時間帯、曜日、時間帯×曜日 の集約特徴など）。  
- カテゴリ変数のハンドリングやスケーリングはモデルに応じて分岐している（線形モデルは標準化、決定木系は不要）。

## 今後の改善案 / TODO
- モデル改善: LightGBM/XGBoost の本格チューニング、特徴量拡張（位置クラスタ・ランドマーク情報・外部データ）  
- 実験管理: MLflow 等で実験を追跡・管理する  
- パフォーマンス: データ読み込み・前処理の高速化（並列化、バッチ処理）  
- ドキュメント: requirements.txt と簡易実行スクリプト（run_pipeline.py 等）を追加

## ライセンス / 出典
- データ出典: Kaggle - PKDD 2015 Taxi Trajectory Prediction  
- 実装は学習目的の参照実装です。必要に応じてライセンス情報を追加してください。