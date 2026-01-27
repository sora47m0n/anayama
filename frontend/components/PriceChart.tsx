"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

type Row = {
  date: string;   //日付
  actual?: number;  //実値
  pred?: number;  //予測値
}

export default function PriceChart({ data }: { data: Row[]}){
  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10}}>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="date"/>
          <YAxis domain={[22000, 27000]}/>
          <Tooltip/>
          <Legend/>

          {/*終値の実値*/}
          <Line
            type="monotone"
            dataKey="actual"
            name="終値（実値）"
            stroke="#0000ff"
            strokeWidth={4} //線の太さ
            connectNulls={false} 
            dot={true}
          />


          {/*AIの予測値*/}
          <Line
            type="monotone"
            dataKey="pred"
            name="AI予測"
            stroke="#ff0000"
            strokeWidth={4} //線の太さ
            connectNulls={false} 
            dot={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>

  );
  
}

