import React from "react";
import { ShieldAlert } from "lucide-react";

export const SafetyBanner: React.FC = () => {
  return (
    <div className="bg-amber-500/10 border-b border-amber-500/30 text-amber-900 px-4 py-2 text-xs font-medium flex items-center justify-center gap-2">
      <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
      <span>
        <strong>MANDATORY CLINICAL SAFETY GATE:</strong> Non-diagnostic decision support prototype.
        All care recommendations require qualified healthcare professional review before action.
      </span>
    </div>
  );
};
