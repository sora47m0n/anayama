"use client";
import { useSearchParams } from 'next/navigation';
import Header from '@/components/Header';
import PriceChart from "@/components/PriceChart";

const data = [
  { date: "12/1", actual: 900, pred: 880 },
  { date: "12/2", actual: 820, pred: 840 },
  { date: "12/3", actual: 950, pred: 910 },
  { date: "12/4", actual: 1000, pred: 930 },
  { date: "12/5", pred: 930 },
]

export default function PredictHome(){
  const searchParams = useSearchParams();
  const code = searchParams.get('code'); // これで "1542.T" をとる
  return (
    <div >
      {/* ヘッダー*/}
        <Header/>
      {/* メイン */}
      <main >
        {/*銘柄コード確認用*/}
        <div className="text-center mt-4">
            <h1 className="text-2xl font-bold">銘柄コード: {code}</h1>
        </div>
        {/*チャート */}
        <section >
          <PriceChart data={data}/>
        </section>

        {/*固定コメント */}
        <section >
          <label>固定コメント</label>
          <input type="textbox" placeholder="固定コメントを入れてください"></input>
        </section>
      </main>
    </div>
  );
}
