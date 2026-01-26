"use client";
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from "react";
import Header from '@/components/Header';
import PriceChart from "@/components/PriceChart";
import { fetchPredictSeries, type Row } from "@/app/lib/api";

export default function PredictHome(){
  const searchParams = useSearchParams();
  const code = searchParams.get('code'); // これで "1542.T" をとる

  // 値が変わったときにリロードしてくれる部分
  const [data, setData] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  // マウント時のみ一度だけ実行される
  useEffect(() => {
    fetchPredictSeries(code)
      .then(setData)
      .catch((e) =>{
        console.error(e);
        setData([]);
      })
      .finally(() => setLoading(false));
  }, []);
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
