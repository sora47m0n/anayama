import Header from '@/components/Header';
import StockList from '@/components/StockList';

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/*ヘッダーを表示 */}
      <Header />

      {/* stockリストエリアを表示 */}
      <StockList />
    </main>
  );
}