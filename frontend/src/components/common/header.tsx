import React from "react";
import Image from "next/image";
import Link from "next/link";
import { Activity, ShieldCheck } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-9 h-9 relative rounded-lg overflow-hidden border border-slate-200 bg-slate-50 flex items-center justify-center">
            <Image
              src="/branding/clinova-ai-mark.png"
              alt="Clinova AI"
              width={32}
              height={32}
              className="object-contain"
            />
          </div>
          <div>
            <span className="font-bold text-slate-900 text-lg tracking-tight">CLINOVA AI</span>
            <span className="text-[10px] text-teal-700 block font-semibold -mt-1 tracking-wider uppercase">
              Continuous Care Intelligence
            </span>
          </div>
        </Link>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Human-in-the-Loop Mode</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-teal-700 bg-teal-50 border border-teal-200 px-2.5 py-1 rounded-md">
            <Activity className="w-3.5 h-3.5" />
            <span className="font-medium">v2.0 Foundation</span>
          </div>
        </div>
      </div>
    </header>
  );
};
