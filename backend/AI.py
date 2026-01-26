import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import lightgbm as lgb
from supabase import create_client, Client

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 

def predict_silver_with_deviation():
    symbol = "1542.T"
    cutoff_date = "2025-11-28" 
    
    print(f" {symbol} (Silver) 予測: 移動平均乖離率を追加して分析します...")


    try:
        # キーチェック
        if "ここに" in SUPABASE_KEY:
            print(" エラー: SUPABASE_KEY を貼り付けてください！")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. データ取得
        print(" データを取得中...")
        response = supabase.table('market_prices').select("*").eq('symbol', symbol).order('trade_date').execute()
        
        data = response.data
        if not data:
            print("データが見つかりません。")
            return

        # 2. データ加工
        df = pd.DataFrame(data)
        cols = ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close_price', 'volume']
        for c in cols: df[c] = df[c].astype(float)
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        # 日付フィルタリング
        df = df[df['trade_date'] <= cutoff_date].copy()
        last_date_in_db = df['trade_date'].iloc[-1]
        
        # 3. 特徴量作成 (★ここに乖離率を追加★)
        df['TargetPrice'] = df['adjusted_close_price']
        
        # 移動平均
        df['SMA_5'] = df['TargetPrice'].rolling(5).mean()
        df['SMA_25'] = df['TargetPrice'].rolling(25).mean()
        
        # ★追加: 移動平均乖離率 (%)
        # (現在値 - 移動平均) / 移動平均
        df['Dev_Rate_5'] = (df['TargetPrice'] - df['SMA_5']) / df['SMA_5']
        df['Dev_Rate_25'] = (df['TargetPrice'] - df['SMA_25']) / df['SMA_25']

        # 既存の特徴量
        df['Price_Change'] = df['TargetPrice'].pct_change()
        df['Range'] = df['high_price'] - df['low_price']
        
        # 目的変数
        df['NextDay_Diff'] = df['TargetPrice'].shift(-1) - df['TargetPrice']
        
        # ★特徴量リストに乖離率を追加
        features = ['SMA_5', 'SMA_25', 'Dev_Rate_5', 'Dev_Rate_25', 'Price_Change', 'Range', 'volume']
        
        # 欠損除去
        train_df = df.dropna(subset=features + ['NextDay_Diff'])

        # 4. モデル学習
        print(" AIモデル学習中 (乖離率を考慮)...")
        model = lgb.LGBMRegressor(random_state=42, verbosity=-1)
        model.fit(train_df[features], train_df['NextDay_Diff'])
        
        # 5. 予測実行11
        latest_row = df.iloc[[-1]].copy()
        pred_diff = model.predict(latest_row[features].fillna(0))[0]
        
        current_price = latest_row['TargetPrice'].iloc[0]
        predicted_price = current_price + pred_diff
        
        # 日付計算
        target_date = last_date_in_db + timedelta(days=1)
        while target_date.weekday() >= 5: 
            target_date += timedelta(days=1)
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # 乖離率の状況を表示
        dev5 = latest_row['Dev_Rate_5'].iloc[0] * 100
        dev25 = latest_row['Dev_Rate_25'].iloc[0] * 100

        print("\n" + "="*50)
        print(f"🔮 {symbol} 詳細分析結果")
        print("="*50)
        print(f"基準日         : {last_date_in_db.strftime('%Y-%m-%d')}")
        print(f"現在価格       : ${current_price:.2f}")
        print(f"5日線乖離率    : {dev5:+.2f}%  ({'買われすぎ' if dev5 > 0 else '売られすぎ'})")
        print(f"25日線乖離率   : {dev25:+.2f}% ({'買われすぎ' if dev25 > 0 else '売られすぎ'})")
        print("-" * 50)
        print(f"予測対象日     : {target_date_str}")
        print(f"AI予測変動     : {pred_diff:+.4f}")
        print(f"AI予測終値     : ${predicted_price:.4f}")
        print("="*50 + "\n")

        # 6. 保存
        insert_data = {
            "stock_code": symbol,
            "target_date": target_date_str,
            "predicted_close": round(predicted_price, 4)
        }
        supabase.table('prediction_results').upsert(insert_data, on_conflict="stock_code, target_date").execute()
        print(" 分析結果を保存しました！")

    except Exception as e:
        print(f" エラー: {e}")

if __name__ == "__main__":
    predict_silver_with_deviation()