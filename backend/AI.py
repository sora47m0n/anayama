import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import lightgbm as lgb
from supabase import create_client, Client

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 

def predict_gold_final():
    symbol = "GLD"
    print(f"🏆 {symbol} (Gold) 12/1の価格予測を開始します...")

    try:
        # キーチェック
        if "ここに" in SUPABASE_KEY:
            print("❌ エラー: SUPABASE_KEY を貼り付けてください！")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. 既存データを取得
        print("📥 データベースから既存データを取得中...")
        response = supabase.table('market_prices') \
            .select("*") \
            .eq('symbol', symbol) \
            .order('trade_date') \
            .execute()
        
        data = response.data
        if not data:
            print("❌ データが見つかりません。")
            return

        # 2. データ加工
        df = pd.DataFrame(data)
        cols = ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close_price', 'volume']
        for c in cols: df[c] = df[c].astype(float)
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        last_date_in_db = df['trade_date'].iloc[-1]
        print(f"✅ 最終データ日付: {last_date_in_db.strftime('%Y-%m-%d')}")

        # 3. 特徴量作成
        df['TargetPrice'] = df['adjusted_close_price']
        df['SMA_5'] = df['TargetPrice'].rolling(5).mean()
        df['SMA_25'] = df['TargetPrice'].rolling(25).mean()
        df['Price_Change'] = df['TargetPrice'].pct_change()
        df['Range'] = df['high_price'] - df['low_price']
        
        df['NextDay_Diff'] = df['TargetPrice'].shift(-1) - df['TargetPrice']
        
        features = ['SMA_5', 'SMA_25', 'Price_Change', 'Range', 'volume']
        train_df = df.dropna(subset=features + ['NextDay_Diff'])

        # 4. モデル学習
        print("🤖 AIモデル学習中...")
        model = lgb.LGBMRegressor(random_state=42, verbosity=-1)
        model.fit(train_df[features], train_df['NextDay_Diff'])
        
        # 5. 予測実行
        latest_row = df.iloc[[-1]].copy()
        pred_diff = model.predict(latest_row[features].fillna(0))[0]
        
        current_price = latest_row['TargetPrice'].iloc[0]
        predicted_price = current_price + pred_diff
        
        # 日付計算
        target_date = last_date_in_db + timedelta(days=1)
        while target_date.weekday() >= 5: 
            target_date += timedelta(days=1)
            
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        print("\n" + "="*45)
        print(f"🔮 {symbol} 予測結果 (送信データ)")
        print("="*45)
        print(f"銘柄コード     : {symbol}")
        print(f"予測対象日     : {target_date_str}")
        print(f"AI予測終値     : {predicted_price:.4f}")
        print("="*45 + "\n")

        # 6. 結果をDB保存 (★ここを修正しました★)
        insert_data = {
            "stock_code": symbol,
            "target_date": target_date_str,
            "predicted_close": round(predicted_price, 4)
        }
        
        # insert ではなく upsert を使い、stock_code と target_date が被ったら上書きする設定にします
        supabase.table('prediction_results').upsert(
            insert_data, 
            on_conflict="stock_code, target_date"
        ).execute()
        
        print("💾 予測結果を上書き保存しました！")
        print("🎉 全ての工程が完了しました。")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    predict_gold_final()