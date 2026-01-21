export default function Header() {
  return (
    <header className="flex justify-between items-center px-10 py-4 border-b border-gray-200">
      
      {/* K1: 株価予測 (48px = text-[48px]) */}
      <h1 className="text-[48px] font-bold text-black tracking-tight">
        株価予測
      </h1>

      {/* wf_bt02: ログアウト (背景#6633cc, 文字20px) */}
      <button className="bg-[#6633cc] text-white text-[20px] px-6 py-2 rounded hover:opacity-90 transition">
        ログアウト
      </button>
      
    </header>
  );
}