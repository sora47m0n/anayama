import yfinance as yf
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 

def run_silver_import():
    symbol = "SLV"
    etf_name = "iShares Silver Trust"
    
    print(f"🚀 {symbol} (Silver) の完全インポートを開始します...")

    # キーチェック
    if "ここに" in SUPABASE_KEY:
        print("❌ エラー: SUPABASE_KEY を貼り付けてください！")
        return

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return

    # ==========================================
    # ステップ1: マスタテーブル(etf)への登録
    # ==========================================
    print("\n🛠️ [Step 1/3] ETFマスタに銘柄を登録中...")
    try:
        # 銘柄が存在しないと価格を入れられないため、先に登録(upsert)
        # ※もし 'name' カラムがないDB設計の場合は、下の行を {"symbol": symbol} だけにしてください
        master_data = {"symbol": symbol, "name": etf_name}
        
        supabase.table('etf').upsert(master_data).execute()
        print(f"✅ マスタ登録完了: {symbol}")
        
    except Exception as e:
        print(f"⚠️ マスタ登録で警告 (無視して進めます): {e}")
        # 万が一 name カラムがない場合などの予備動作
        try:
            supabase.table('etf').upsert({"symbol": symbol}).execute()
        except:
            pass

    # ==========================================
    # ステップ2: Yahoo Financeからデータ取得
    # ==========================================
    print(f"\n📥 [Step 2/3] Yahoo Financeから価格データを取得中...")
    try:
        # auto_adjust=True でデータ構造をシンプルに取得
        df = yf.download(symbol, start="2024-01-01", end=datetime.now().strftime('%Y-%m-%d'), progress=False, auto_adjust=True)
        
        if df.empty:
            print("❌ データが見つかりませんでした。")
            return

        # カラム名の修正 (MultiIndex対策)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df = df.reset_index()
        print(f"✅ ダウンロード成功: {len(df)} 件")

    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        return

    # ==========================================
    # ステップ3: データベースへ保存
    # ==========================================
    print(f"\n💾 [Step 3/3] データベースへ保存中...")
    
    data_to_insert = []
    convert_error = False

    for index, row in df.iterrows():
        try:
            # 日付カラムの特定 (Date または date)
            date_val = row.get('Date') if 'Date' in row else row.get('date')
            if pd.isna(date_val): continue

            record = {
                "symbol": symbol,
                "trade_date": date_val.strftime('%Y-%m-%d'),
                "open_price": float(row['Open']),
                "high_price": float(row['High']),
                "low_price": float(row['Low']),
                "close_price": float(row['Close']),
                # auto_adjust=Trueなので Adj Close は Close と同じか存在しない
                "adjusted_close_price": float(row['Adj Close']) if 'Adj Close' in row else float(row['Close']),
                "volume": int(row['Volume'])
            }
            data_to_insert.append(record)
        except Exception as e:
            if not convert_error:
                print(f"⚠️ データ変換エラー発生: {e}")
                convert_error = True
            continue

    if not data_to_insert:
        print("❌ 保存対象のデータがありません。")
        return

    try:
        # 既存データのクリーニング
        supabase.table('market_prices').delete().eq('symbol', symbol).execute()
        
        # 分割送信 (100件ずつ)
        chunk_size = 100
        for i in range(0, len(data_to_insert), chunk_size):
            chunk = data_to_insert[i:i + chunk_size]
            supabase.table('market_prices').insert(chunk).execute()
            
        print(f"\n🎉 【完了】{symbol} の全処理が成功しました！")
        print(f"   登録件数: {len(data_to_insert)} 件")

    except Exception as e:
        print(f"❌ データベース保存エラー: {e}")

if __name__ == "__main__":
    run_silver_import()