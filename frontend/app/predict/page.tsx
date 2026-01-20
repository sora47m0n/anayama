"use client";

import PriceChart from "../components/PriceChart";

const data = [
  { date: "12/1", actual: 900, pred: 880 },
  { date: "12/2", actual: 820, pred: 840 },
  { date: "12/3", actual: 950, pred: 910 },
  { date: "12/4", actual: 1000, pred: 930 },
  { date: "12/5", pred: 930 },
]

export default function PredictHome(){
  return (
    <div >
      {/* ヘッダー*/}
      <header>
        <h1 >株価予測</h1>
        <button>ログアウト</button>
      </header>

      {/* メイン */}
      <main >
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
