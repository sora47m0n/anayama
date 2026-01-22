from supabase import create_client, Client

# --- 設定値 ---
SUPABASE_URL = "https://zwnqbpunabqgnhkiutbj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3bnFicHVuYWJxZ25oa2l1dGJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgzNTQ0NjMsImV4cCI6MjA4MzkzMDQ2M30.c1YKLmb6mRvhENUsgcydInSgizcpMZfiypjQJu-5ocI"

def check_supabase_connection():
    print("🔄 Supabaseへ接続を試行中...")
    
    try:
        # クライアントの作成
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # テスト: market_pricesテーブルからデータを1件だけ取得してみる
        response = supabase.table('market_prices').select("*").limit(1).execute()
        
        # --- 結果の判定 ---
        if response.data:
            print("✅ 【成功】接続に成功し、データが取得できました。")
            print("--- 取得データサンプル ---")
            print(response.data)
            return True
        elif response.data == []:
            print("jg 【確認】接続は成功しましたが、テーブルが空（データなし）です。")
            return True
        else:
            print("❌ 【失敗】データが取得できませんでした（予期しないレスポンス）。")
            return False

    except Exception as e:
        print("❌ 【エラー】接続に失敗しました。")
        print(f"詳細: {e}")
        return False

if __name__ == "__main__":
    check_supabase_connection()