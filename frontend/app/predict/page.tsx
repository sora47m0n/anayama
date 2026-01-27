"use client";
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from "react";
import Header from '@/components/Header';
import PriceChart from "@/components/PriceChart";
import { fetchPredictSeries, fetchAiComment, type Row } from "@/app/lib/api";
import styles from "./page.module.css";

export default function PredictHome(){
  const searchParams = useSearchParams();
  const code = searchParams.get('code'); // これで "1542.T" をとる

  // 値が変わったときにリロードしてくれる部分
  const [data, setData] = useState<Row[]>([]);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingComment,setLoadingComment] = useState(false);

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

  const onGenerateComment = async () => {
    try {
      setLoadingComment(true);
      const res = await fetchAiComment(code);
      setComment(res.comment);
    } finally {
      setLoadingComment(false);
    }
  };

  return (
    <div >
      {/* ヘッダー*/}
        <Header/>
      {/* メイン */}
      <main >
        {/*銘柄コード確認用*/}
        {/* <div className="text-center mt-4">
            <h1 className="text-2xl font-bold">銘柄コード: {code}</h1>
        </div> */}
        {/*チャート */}
        <section >
          <PriceChart data={data}/>
        </section>

        {/*固定コメント */}
         {/* 固定コメント：画像の見た目に合わせたカード */}
        <section className={styles.card}>
          <div className={styles.headerRow}>
            <span className={styles.badge}>固定コメント</span>

            <button
              className={styles.aiButton}
              onClick={onGenerateComment}
              disabled={loadingComment || !code}
              type="button"
            >
            <span className={styles.sparkle} aria-hidden>
              ✨
            </span>
            {loadingComment ? "生成中..." : "AIでコメント生成"}
          </button>
          </div>
          

          <div className={styles.divider} />

          <textarea
            className={styles.textarea}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="固定コメントを入れてください"
            rows={4}
            readOnly
          />
        </section>
      </main>
    </div>
  );
}
