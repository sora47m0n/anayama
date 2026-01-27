"use client";

import { useState } from 'react';
import Link from 'next/link';

export default function StockList() {
  const stocks = [
    { id: '1542.T', name: '純銀信託' }
  ];

  // 検索文字を管理する変数
  const [searchTerm, setSearchTerm] = useState("");

  // 検索ロジック
  const filteredStocks = stocks.filter((stock) => {
    const term = searchTerm.toLowerCase();
    return stock.id.toLowerCase().includes(term) || stock.name.includes(term);
  });

  return (
    <div className="w-fit mx-auto mt-32 px-4">
      
      {/* --- 1段目: タイトルとソート --- */}
      <div className="flex items-end gap-6 border-b border-gray-300 pb-2 mb-6">
        <h2 className="h1 text-[28px] font-bold text-black leading-none whitespace-nowrap">
          銘柄一覧
        </h2>

        <select className="wf_bt01 bg-gray-100 border-none rounded px-2 py-1 text-[14px] text-black focus:outline-none cursor-pointer">
            <option>ソート</option>
            <option>昇順</option>
            <option>降順</option>
        </select>
      </div>

      {/* --- 2段目: 検索バー --- */}
      <div className="mb-6">
          <input 
              type="text" 
              placeholder="検索 🔍" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="wf_tx01 bg-gray-100 border-none rounded px-4 py-2 text-[16px] text-black placeholder-[#cccccc] w-64 focus:outline-none focus:ring-1 focus:ring-[#6633cc]"
          />
      </div>

      {/* --- 3段目: 銘柄リスト --- */}
      <div className="">
        {filteredStocks.map((stock) => (
            <Link 
              key={stock.id}
              href={`/predict?code=${stock.id}`} 
              className="wf_lnc01 text-[#6633cc] text-[20px] hover:underline hover:opacity-80 block"
            >
              {stock.id} : {stock.name}
            </Link>
        ))}
      </div>

    </div>
  );
}