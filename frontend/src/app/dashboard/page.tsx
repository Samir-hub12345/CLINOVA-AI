"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export default function DashboardGatewayPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.replace(dashboardPath(user.role));
      } else {
        router.replace("/login?redirect=/dashboard");
      }
    }
  }, [user, loading, router]);

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 items-center justify-center p-6">
      <div className="flex flex-col items-center gap-4 text-slate-800 font-semibold text-sm bg-white px-8 py-6 rounded-3xl border border-slate-200 shadow-sm text-center">
        <div className="h-12 w-12 rounded-2xl bg-teal-50 border border-teal-100 flex items-center justify-center p-2">
          <ClinovaLogo variant="mark" size="sm" className="animate-pulse" />
        </div>
        <span>Directing to your authorized Clinova AI workspace...</span>
      </div>
    </div>
  );
}
