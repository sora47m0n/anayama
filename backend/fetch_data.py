import yfinance as yf
import psycopg2
import sys
from datetime import datetime, date

# ---------------------------------------------------------
# 設定：Supabaseの接続文字列(URI)
# ---------------------------------------------------------
DB_URL = "postgresql://postgres.ogjpslisorqbztlzhocd:fbifaufiuaef@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

# 取得期間設定 (2024/1 ～ 2025/12)
START_DATE = "2024-01-01"

END_DATE = "2025-11-30" 

def save_etf_and_prices(symbol):
    conn = None
    try:
        print(f"\n [{symbol}] 処理開始...")
        
        # 1. yfinanceからすべての情報を取得
        ticker = yf.Ticker(symbol)
        
        # -----------------------------------------------------
        # ステップA: ETF情報の取得とマスタテーブル(etf)への登録
        # -----------------------------------------------------
        print(f"   ...基本情報を取得中")
        info = ticker.info
        
        # 必要な情報を辞書から取り出す（無い場合はデフォルト値を入れる）
        etf_name = info.get('longName') or info.get('shortName') or symbol
        # ETFの場合は 'category'、個別株の場合は 'sector' に情報が入ることが多い
        etf_sector = info.get('category') or info.get('sector') or 'Unknown'
        etf_currency = info.get('currency', 'USD')
        etf_desc = info.get('longBusinessSummary') or info.get('description') or ''

        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # 親テーブルへのUPSERT（情報があれば更新する）
        sql_etf = """
            INSERT INTO etf (symbol, name, sector, currency, description, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
            ON CONFLICT (symbol) 
            DO UPDATE SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                currency = EXCLUDED.currency,
                description = EXCLUDED.description;
        """
        cur.execute(sql_etf, (symbol, etf_name, etf_sector, etf_currency, etf_desc))
        print(f"    ETFマスタを更新しました: {etf_name}")

        # -----------------------------------------------------
        # ステップB: 株価データの取得とテーブル(market_prices)への登録
        # -----------------------------------------------------
        print(f"   ...株価データを取得中 ({START_DATE} ~ {END_DATE})")
        
        # auto_adjust=False で、調整前(Close)と調整後(Adj Close)を両方取得
        df = ticker.history(start=START_DATE, end=END_DATE, auto_adjust=False)

        if df.empty:
            print(f"   areat {symbol} の指定期間のデータがありませんでした。")
            return

        # 日付をカラムに戻す
        df = df.reset_index()

        sql_price = """
            INSERT INTO market_prices (
                symbol, trade_date, open_price, high_price, low_price, 
                close_price, adjusted_close_price, volume
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, trade_date) 
            DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                adjusted_close_price = EXCLUDED.adjusted_close_price,
                volume = EXCLUDED.volume;
        """

        # 高速化のためにバッチ処理（execute_batchを使いたいところですが、今回は分かりやすくループで）
        count = 0
        for _, row in df.iterrows():
            # Volumeが空の場合のケア
            volume = int(row['Volume']) if 'Volume' in row and row['Volume'] else 0
            
            # タイムゾーン情報がついているとエラーになることがあるので、日付のみにする
            trade_date = row['Date'].date()

            data_tuple = (
                symbol,
                trade_date,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                float(row['Adj Close']),
                volume
            )
            cur.execute(sql_price, data_tuple)
            count += 1

        conn.commit()
        print(f"   ☑ 株価データの登録完了: {count}件")

    except Exception as e:
        print(f"   × エラーが発生しました: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    # 対象の銘柄リスト
    # (SPY:S&P500, QQQ:ナスダック, VTI:全米, GLD:金, MSFT:個別株の例)
    tickers = ["SPY", "QQQ", "VTI", "GLD", "MSFT","1542.T"]
    
    for t in tickers:
        save_etf_and_prices(t)
        
    print("\n すべての処理が完了しました")