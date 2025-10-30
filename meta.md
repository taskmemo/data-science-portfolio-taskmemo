## data description
### dataset shape
train:  (1710670, 9)
test:  (320, 9)
location:  (63, 4)

## table description
| カラム名 | 型 | 説明 |
|---|---:|---|
| TRIP_ID | int | 各旅行の一意の識別子 |
| CALL_TYPE | object | サービス要求方法。A=中央から発送、B=特定のスタンドでの直接要求、C=その他（路上等） |
| ORIGIN_CALL | float64 / NULL | CALL_TYPE='A' の場合に顧客を識別する電話番号ID。その他はNULL |
| ORIGIN_STAND | float64 / NULL | CALL_TYPE='B' の場合に乗車の出発スタンドID。その他はNULL |
| TAXI_ID | int64 | 乗車を行ったタクシー運転手の一意識別子 |
| TIMESTAMP | int64 | 旅行の開始時刻を表すUnixタイムスタンプ（秒単位） |
| DAYTYPE | object | 曜日タイプ。B=祝日など特別日、C=タイプBの前日、A=通常日（平日・週末等） |
| MISSING_DATA | bool | GPSデータが完全ならFALSE、1つ以上の位置が欠落している場合はTRUE |
| POLYLINE | object | 15秒ごとの[経度, 緯度]ペアのリストを文字列化したもの（先頭と末尾は[]）。最初が開始点、最後が目的地 |

## solution process
- データ整形
    - 特徴量の生成
        - 座標リストを分割して、出発点と目的地を抽出
        - ステップ数
        - 移動距離
        - 移動時間
        - 平均速度（移動距離 / 移動時間）
    - 欠損値・外れ値の処理
        - POLYLINEが空のデータを削除
        - 移動距離が0のデータを削除
- モデル構築
    - 目的変数: 最終地点の緯度・経度
    - 説明変数: 上記で作成した特徴量（ベースモデルでは特徴量の選択はしない）
    - モデル: RandomForestRegressor, LinearRegression

