import pandas as pd
import numpy as np
from datetime import datetime
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from supabase import create_client, Client

# --- 1. Supabase接続設定 ---
# Supabaseのダッシュボード > Settings > API から取得できる情報を設定してください
SUPABASE_URL = "https://zwnqbpunabqgnhkiutbj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3bnFicHVuYWJxZ25oa2l1dGJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgzNTQ0NjMsImV4cCI6MjA4MzkzMDQ2M30.c1YKLmb6mRvhENUsgcydInSgizcpMZfiypjQJu-5ocI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def predict_stock_price(symbol):
    # --- 2. データ取得 (Supabase API経由) ---
    # market_pricesテーブルから指定条件でデータを取得
    try:
        response = supabase.table('market_prices') \
            .select('trade_date, close_price') \
            .eq('symbol', symbol) \
            .gte('trade_date', '2024-11-01') \
            .lte('trade_date', '2025-11-30') \
            .order('trade_date') \
            .execute()
        
        # データが空、または不足している場合のチェック
        if not response.data or len(response.data) < 30:
            return {"error": "Insufficient data or symbol not found"}

        # レスポンス(JSONリスト)をDataFrameに変換
        df = pd.DataFrame(response.data)
        
        # カラム名をロジックに合わせて変更 (close_price -> Close)
        df.rename(columns={'close_price': 'Close'}, inplace=True)
        
        # データ型を調整（Supabaseからの戻り値は文字列の場合があるため）
        df['Close'] = df['Close'].astype(float)
        df['trade_date'] = pd.to_datetime(df['trade_date'])

    except Exception as e:
        return {"error": f"Data fetch error: {str(e)}"}

    # --- 3. 特徴量エンジニアリング (前回と同様) ---
    # 計算用ベース
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_25'] = df['Close'].rolling(window=25).mean()

    # AI学習用特徴量
    df['SMA_5_Rate'] = (df['Close'] - df['SMA_5']) / df['SMA_5']
    df['SMA_25_Rate'] = (df['Close'] - df['SMA_25']) / df['SMA_25']
    df['Diff_PrevDay'] = df['Close'].diff()

    # 正解ラベル（翌日の変動幅）
    df['Target_Diff'] = df['Close'].shift(-1) - df['Close']

    # 最新の行（11/30分）は翌日の正解がないため、予測用に切り出す
    latest_data_row = df.iloc[[-1]].copy()
    
    # 学習用データ（欠損値を除去）
    train_df = df.dropna(subset=['SMA_5_Rate', 'SMA_25_Rate', 'Diff_PrevDay', 'Target_Diff'])

    # --- 4. 学習モデルの定義と学習 ---
    features = ['SMA_5_Rate', 'SMA_25_Rate', 'Diff_PrevDay']
    X = train_df[features]
    y = train_df['Target_Diff']

    # データ分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=False)

    model = lgb.LGBMRegressor(
        objective='regression',
        n_estimators=100,
        learning_rate=0.05,
        random_state=42,
        verbosity=-1
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])

    # --- 5. 予測処理 ---
    # a) 過去1週間分の再現予測
    past_week_data = df.tail(7).copy()
    past_week_features = past_week_data[features]
    past_week_pred_diff = model.predict(past_week_features)
    past_week_data['predicted_close'] = past_week_data['Close'] + past_week_pred_diff

    # b) 翌日(12/01)の予測
    next_day_features = latest_data_row[features]
    predicted_diff = model.predict(next_day_features)[0]
    predicted_close_1201 = float(latest_data_row['Close'].iloc[0] + predicted_diff)
    
    # 日付型を文字列に変換（JSONシリアライズ対策）
    target_date_1201_str = "2025-12-01" 

    # --- 6. 結果のDB保存 (prediction_results) ---
    insert_data = {
        "stock_code": symbol,
        "target_date": target_date_1201_str,
        "predicted_close": predicted_close_1201,
        # created_at はSupabase側でデフォルト値(now())設定があれば省略可。
        # 必要ならここで "created_at": datetime.now().isoformat() を追加
    }

    try:
        supabase.table('prediction_results').insert(insert_data).execute()
    except Exception as e:
        print(f"Insert error: {e}")
        # 保存エラーでも予測結果は返す
    
    # --- 7. フロントエンド返却用データの整形 ---
    # 日付を文字列化してJSON互換にする
    past_week_data['trade_date'] = past_week_data['trade_date'].dt.strftime('%Y-%m-%d')
    history_json = past_week_data[['trade_date', 'Close', 'predicted_close']].to_dict(orient='records')
    
    return {
        "symbol": symbol,
        "prediction_12_01": {
            "date": target_date_1201_str,
            "predicted_close": predicted_close_1201
        },
        "history": history_json
    }

# 実行例
if __name__ == "__main__":
    # テスト実行
    result = predict_stock_price('7203') # トヨタ自動車の例
    print(result)