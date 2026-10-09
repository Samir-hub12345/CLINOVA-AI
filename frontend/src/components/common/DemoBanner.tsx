import React from "react";
import { ShieldAlert, Database } from "lucide-react";

export const DemoBanner: React.FC = () => {
  return (
    <div
      role="alert"
      aria-live="polite"
      className="clinova-banner-demo"
      id="clinova-synthetic-demo-banner"
    >
      <ShieldAlert style={{ width: 14, height: 14, flexShrink: 0 }} aria-hidden="true" />
      <span>
        <strong>DEMO / SYNTHETIC DATA MODE:</strong> Non-diagnostic prototype running strictly on synthetic cases (e.g. <code>CASE-SYNTH-*</code>). Zero real patient data or PII.
      </span>
      <Database style={{ width: 13, height: 13, flexShrink: 0, opacity: 0.75 }} aria-hidden="true" />
    </div>
  );
};
