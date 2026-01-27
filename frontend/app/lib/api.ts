export const API_BASE = 
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Row = {
    date: string,
    actual: number | null;
    pred: number | null;
};

export async function fetchAiComment(code: string): Promise<{comment: string}>{
    const res = await fetch(
        `${API_BASE}/api/comment?symbol=${code}`,
        { cache: "no-cache"}
    );

    if (!res.ok) throw new Error(`API error: ${res.status}`);

    return res.json(); 
}

// promiseを入れるとすぐに返すのではなく通信終了後にかえす
export async function fetchPredictSeries(code:String): Promise<Row[]> {
    const res = await fetch(
        `${API_BASE}/api/predict-series?symbol=${code}`,
        { cache: "no-store"}
    );

    if (!res.ok){
        //コメントのやつはエラーログをブラウザに出す
        // const body = await res.text().catch(() => "");
        // throw new Error(`API error: ${res.status} ${res.statusText} - ${body}`);
        throw new Error(`API error: ${res.status}`);
    } 

    return res.json();
}
