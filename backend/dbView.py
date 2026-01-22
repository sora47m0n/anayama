from supabase import create_client, Client

# --- 設定 ---
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 


def check_database():
    print("🔍 データベースの中身を診断します...\n")

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 1. ETFマスタの確認
        print("--- [1. ETFマスタテーブル (etf)] ---")
        response_etf = supabase.table('etf').select("*").execute()
        etfs = response_etf.data
        if not etfs:
            print("❌ ETFマスタが空です！ 'SLV' が登録されていません。")
        else:
            for item in etfs:
                print(f"✅ 登録済み: {item.get('symbol')} - {item.get('name')}")

        print("\n")

        # 2. 価格データの確認
        print("--- [2. 価格データテーブル (market_prices)] ---")
        
        # SLVのデータ件数をカウント
        response_slv = supabase.table('market_prices').select("symbol", count="exact").eq('symbol', 'SLV').execute()
        count = response_slv.count
        
        if count == 0:
            print("❌ 'SLV' の価格データが 0件 です。")
            print("   (可能性: 保存処理の途中でエラーになり、削除だけされて保存されなかった)")
        else:
            print(f"✅ 'SLV' のデータが {count} 件 見つかりました！")
            
            # 最新の日付を確認
            latest = supabase.table('market_prices').select("trade_date").eq('symbol', 'SLV').order('trade_date', desc=True).limit(1).execute()
            if latest.data:
                print(f"   📅 最新データ日付: {latest.data[0]['trade_date']}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    check_database()