import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import lightgbm as lgb
from supabase import create_client, Client

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 


def predict_silver_dec1():
    symbol = "SLV"
    # 予測の基準日（この日までのデータを使って、翌日を予測する）
    cutoff_date = "2025-11-28" 
    
    print(f"🥈 {symbol} (Silver) の価格予測を開始します...")
    print(f"🎯 ターゲット: {cutoff_date} の翌営業日 (2025/12/01) を予測")

    try:
        # キーチェック
        if "ここに" in SUPABASE_KEY:
            print("❌ エラー: SUPABASE_KEY を貼り付けてください！")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. データを取得 (日付順)
        print("📥 データベースからデータを取得中...")
        response = supabase.table('market_prices') \
            .select("*") \
            .eq('symbol', symbol) \
            .order('trade_date') \
            .execute()
        
        data = response.data
        if not data:
            print(f"❌ {symbol} のデータが見つかりません。")
            return

        # 2. データ加工
        df = pd.DataFrame(data)
        cols = ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close_price', 'volume']
        for c in cols: df[c] = df[c].astype(float)
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        # ★重要: データが未来まであっても、強制的に 2025-11-28 で区切る★
        df = df[df['trade_date'] <= cutoff_date].copy()
        
        if df.empty:
            print(f"❌ {cutoff_date} 以前のデータがありません。")
            return

        last_date_in_db = df['trade_date'].iloc[-1]
        print(f"✅ 使用するデータの最終日: {last_date_in_db.strftime('%Y-%m-%d')}")

        # 3. 特徴量作成 (GLDと同じロジック)
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
        
        # 5. 予測実行 (2025-11-28 の行を使用)
        latest_row = df.iloc[[-1]].copy()
        pred_diff = model.predict(latest_row[features].fillna(0))[0]
        
        current_price = latest_row['TargetPrice'].iloc[0]
        predicted_price = current_price + pred_diff
        
        # 日付計算 (11/28の次は自動的に12/01になる)
        target_date = last_date_in_db + timedelta(days=1)
        while target_date.weekday() >= 5: # 土日スキップ
            target_date += timedelta(days=1)
            
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # 強制確認
        if target_date_str != "2025-12-01":
            print(f"⚠️ 注意: 計算された日付が {target_date_str} ですが、そのまま保存します。")

        print("\n" + "="*45)
        print(f"🔮 {symbol} 予測結果")
        print("="*45)
        print(f"銘柄コード     : {symbol}")
        print(f"基準日(データ) : {last_date_in_db.strftime('%Y-%m-%d')}")
        print(f"予測対象日     : {target_date_str}")
        print(f"AI予測終値     : {predicted_price:.4f}")
        print(f"(参考: 現在価格 ${current_price:.2f} 変動 {pred_diff:+.4f})")
        print("="*45 + "\n")

        # 6. 結果をDB保存 (upsert)
        insert_data = {
            "stock_code": symbol,
            "target_date": target_date_str,
            "predicted_close": round(predicted_price, 4)
        }
        
        supabase.table('prediction_results').upsert(
            insert_data, 
            on_conflict="stock_code, target_date"
        ).execute()
        
        print("💾 予測結果を保存しました！")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    predict_silver_dec1()