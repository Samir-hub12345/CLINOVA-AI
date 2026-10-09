"use client";

import React from "react";
import { AlertOctagon, Zap } from "lucide-react";
import { RedFlagAlert } from "@/types";

interface RedFlagBannerProps {
  flags: RedFlagAlert[];
  onInitiateResuscitation?: () => void;
}

export const RedFlagBanner: React.FC<RedFlagBannerProps> = ({
  flags,
  onInitiateResuscitation,
}) => {
  if (!flags || flags.length === 0) return null;

  return (
    <div className="clinova-banner-emergency" role="alert" aria-live="assertive">
      <AlertOctagon style={{ width: 22, height: 22, color: "var(--clinova-emergency)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
          <div>
            <strong style={{ fontSize: "0.9375rem", textTransform: "uppercase", letterSpacing: "0.02em" }}>
              CRITICAL EMERGENCY RED FLAG DETECTED ({flags.length})
            </strong>
            <p style={{ color: "var(--clinova-emergency-text)", fontSize: "0.8125rem", marginTop: 2 }}>
              Clinical Resuscitation BEFORE Administrative Completion. Divert to Resuscitation Bay immediately.
            </p>
          </div>
          {onInitiateResuscitation && (
            <button
              onClick={onInitiateResuscitation}
              className="clinova-btn clinova-btn-emergency"
              style={{ fontSize: "0.8125rem", height: 36 }}
            >
              <Zap style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>ACTIVATE RESUSCITATION BAY</span>
            </button>
          )}
        </div>

        <ul style={{ marginTop: 8, paddingLeft: 18, fontSize: "0.8125rem", display: "flex", flexDirection: "column", gap: 4 }}>
          {flags.map((flag) => (
            <li key={flag.id}>
              <strong>{flag.flag_name}</strong> — detected at {flag.detected_at} ({flag.source_evidence})
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
