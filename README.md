# Taxi Trajectory Regression (PKDD 2015)

このプロジェクトは、**PKDD 2015: Taxi Service Trajectory Prediction** コンペティションの簡易版を再現したものです。

## 概要
タクシーの一部のGPS軌跡データから、**最終目的地（緯度・経度）** を予測します。

## 目的
- 時系列・地理空間データの扱いを学ぶ  
- ベースラインモデルとして **線形回帰** を実装  
- 評価指標として **Haversine距離（km）** を用いる

## データセット
- 出典：[Kaggle - PKDD 2015 Taxi Trajectory Prediction](https://www.kaggle.com/competitions/pkdd-15-predict-taxi-service-trajectory-i)  
- 対象地域：ポルトガル・ポルト市  
- 期間：2013年7月〜2014年6月  
- データ数：442台のタクシーによる1年間の走行軌跡

## ステップ
1. データの読み込みと前処理  
2. 特徴量エンジニアリング（出発地点・距離・時間特徴など）  
3. 線形回帰モデルの学習  
4. Haversine距離による評価

## ファイル構成
study/taxi_trajectory_regression/
├── taxi_regression.ipynb
└── README.md