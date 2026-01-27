import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import lightgbm as lgb
from supabase import create_client

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg"  # 環境変数から読む（直書きしない）

def predict_silver_with_deviation():
    symbol = "1542.T"
    cutoff_date = "2025-11-28"          # 学習に使う最終日
    end_date_str = "2025-12-03"         # ここまで予測を出す（営業日ベース）

    print(f"{symbol} (Silver) 予測: 移動平均乖離率を追加して分析します...")

    try:
        if not SUPABASE_KEY:
            print("❌ エラー: 環境変数 SUPABASE_SERVICE_ROLE_KEY が未設定です")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 1. データ取得
        print("📥 データを取得中...")
        response = (
            supabase.table("market_prices")
            .select("*")
            .eq("symbol", symbol)
            .order("trade_date")
            .execute()
        )

        data = response.data
        if not data:
            print("❌ データが見つかりません。")
            return

        # 2. データ加工
        df = pd.DataFrame(data)
        cols = ["open_price", "high_price", "low_price", "close_price", "adjusted_close_price", "volume"]
        for c in cols:
            df[c] = df[c].astype(float)
        df["trade_date"] = pd.to_datetime(df["trade_date"])

        cutoff = pd.to_datetime(cutoff_date)
        end_date = pd.to_datetime(end_date_str)

        # 日付フィルタリング（学習用）
        df = df[df["trade_date"] <= cutoff].copy()
        if df.empty:
            print("❌ cutoff_date 以前のデータがありません。")
            return

        # 3. 特徴量作成
        def recompute_features(_df: pd.DataFrame) -> pd.DataFrame:
            _df = _df.sort_values("trade_date").reset_index(drop=True)
            _df["TargetPrice"] = _df["adjusted_close_price"]
            _df["SMA_5"] = _df["TargetPrice"].rolling(5).mean()
            _df["SMA_25"] = _df["TargetPrice"].rolling(25).mean()
            _df["Dev_Rate_5"] = (_df["TargetPrice"] - _df["SMA_5"]) / _df["SMA_5"]
            _df["Dev_Rate_25"] = (_df["TargetPrice"] - _df["SMA_25"]) / _df["SMA_25"]
            _df["Price_Change"] = _df["TargetPrice"].pct_change()
            _df["Range"] = _df["high_price"] - _df["low_price"]
            _df["NextDay_Diff"] = _df["TargetPrice"].shift(-1) - _df["TargetPrice"]
            return _df

        df = recompute_features(df)

        features = ["SMA_5", "SMA_25", "Dev_Rate_5", "Dev_Rate_25", "Price_Change", "Range", "volume"]

        # 欠損除去（学習用）
        train_df = df.dropna(subset=features + ["NextDay_Diff"])
        if train_df.empty:
            print("❌ 学習データが不足しています（移動平均などでNaNが多い）")
            return

        # 4. モデル学習
        print("🤖 AIモデル学習中 (乖離率を考慮)...")
        model = lgb.LGBMRegressor(random_state=42, verbosity=-1)
        model.fit(train_df[features], train_df["NextDay_Diff"])

        # 未来日の volume/high/low は未知なので仮置き（最小実装）
        last_known_volume = float(df["volume"].dropna().iloc[-1]) if df["volume"].notna().any() else 0.0

        # 次営業日計算
        def next_business_day(d: pd.Timestamp) -> pd.Timestamp:
            d = d + timedelta(days=1)
            while d.weekday() >= 5:  # 土日スキップ
                d = d + timedelta(days=1)
            return d

        # 5. 予測（12/3まで連続）
        print(f"📈 連続予測を開始（～ {end_date_str}）...")
        while True:
            last_date_in_db = df["trade_date"].iloc[-1]
            target_date = next_business_day(last_date_in_db)

            if target_date > end_date:
                break

            latest_row = df.iloc[[-1]].copy()

            # 予測入力
            X = latest_row[features].copy().fillna(0)
            pred_diff = model.predict(X)[0]

            current_price = float(latest_row["TargetPrice"].iloc[0])
            predicted_price = current_price + float(pred_diff)
            target_date_str = target_date.strftime("%Y-%m-%d")

            # 画面表示
            dev5 = float(latest_row["Dev_Rate_5"].iloc[0]) * 100 if pd.notna(latest_row["Dev_Rate_5"].iloc[0]) else 0.0
            dev25 = float(latest_row["Dev_Rate_25"].iloc[0]) * 100 if pd.notna(latest_row["Dev_Rate_25"].iloc[0]) else 0.0

            print("\n" + "=" * 50)
            print(f"🔮 {symbol} 予測 ({target_date_str})")
            print("=" * 50)
            print(f"基準日         : {last_date_in_db.strftime('%Y-%m-%d')}")
            print(f"現在価格       : ${current_price:.2f}")
            print(f"5日線乖離率    : {dev5:+.2f}%")
            print(f"25日線乖離率   : {dev25:+.2f}%")
            print("-" * 50)
            print(f"AI予測変動     : {pred_diff:+.4f}")
            print(f"AI予測終値     : ${predicted_price:.4f}")
            print("=" * 50)

            # 6. 保存（毎日 upsert）
            insert_data = {
                "stock_code": symbol,
                "target_date": target_date_str,
                "predicted_close": round(float(predicted_price), 4),
            }
            supabase.table("prediction_results").upsert(
                insert_data, on_conflict="stock_code, target_date"
            ).execute()
            print("✅ 保存しました")

            # 7. 次の日の特徴量に使うため、予測結果を df に追加（OHLC/volumeは仮置き）
            new_row = {
                "trade_date": target_date,
                "open_price": predicted_price,
                "high_price": predicted_price,
                "low_price": predicted_price,
                "close_price": predicted_price,
                "adjusted_close_price": predicted_price,
                "volume": last_known_volume,
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # 特徴量再計算（次ループの入力を作る）
            df = recompute_features(df)

        print("\n🎉 12/3 までの予測を保存しました！")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    predict_silver_with_deviation()
