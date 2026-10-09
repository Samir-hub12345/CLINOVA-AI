"use client";

import React, { useState } from "react";
import {
  CheckCircle,
  XCircle,
  Edit3,
  HelpCircle,
  ArrowUpRight,
  Send,
  Eye,
  Check,
  Share2,
} from "lucide-react";
import { HumanDecisionAction } from "@/types";
import { Button } from "./Button";

interface HumanDecisionCardProps {
  caseId: string;
  clinicianName?: string;
  onDecision: (action: HumanDecisionAction, notes: string) => Promise<void>;
}

export const HumanDecisionCard: React.FC<HumanDecisionCardProps> = ({
  caseId,
  clinicianName = "Dr. Priya Sharma",
  onDecision,
}) => {
  const [selectedAction, setSelectedAction] = useState<HumanDecisionAction | null>(null);
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleExecute = async () => {
    if (!selectedAction) return;
    setIsSubmitting(true);
    try {
      await onDecision(selectedAction, notes);
      setSuccessMessage(`Decision [${selectedAction}] committed to case ${caseId} audit log.`);
      setSelectedAction(null);
      setNotes("");
    } catch {
      // error handled upstream
    } finally {
      setIsSubmitting(false);
    }
  };

  const actionButtons: Array<{
    action: HumanDecisionAction;
    label: string;
    variant: "primary" | "secondary" | "outline" | "danger" | "emergency";
    icon: React.ReactNode;
    desc: string;
  }> = [
    {
      action: "VERIFY",
      label: "Verify Evidence",
      variant: "primary",
      icon: <CheckCircle style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Confirm and authenticate extracted parameters and vitals.",
    },
    {
      action: "MODIFY",
      label: "Modify Parameter",
      variant: "secondary",
      icon: <Edit3 style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Override or correct inaccurate recorded values.",
    },
    {
      action: "RESOLVE_CONFLICT",
      label: "Resolve Conflict",
      variant: "secondary",
      icon: <Check style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Designate authoritative source for contradicting records.",
    },
    {
      action: "REQUEST_INFO",
      label: "Request More Info",
      variant: "outline",
      icon: <HelpCircle style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Dispatch Next-Best Information follow-up question or lab order.",
    },
    {
      action: "REJECT",
      label: "Reject Advisory",
      variant: "danger",
      icon: <XCircle style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Dismiss algorithmic suggestion with mandatory clinical rationale.",
    },
    {
      action: "CONTINUE",
      label: "Continue OPD",
      variant: "secondary",
      icon: <Eye style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Pathway A: Outpatient routine management and scheduled discharge.",
    },
    {
      action: "OBSERVE",
      label: "Observe / Revisit",
      variant: "secondary",
      icon: <Eye style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Pathway B: Serial monitoring or dedicated follow-up review.",
    },
    {
      action: "ESCALATE",
      label: "Escalate Ward / OT",
      variant: "emergency",
      icon: <ArrowUpRight style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Pathway C: Immediate inpatient bed or surgical resuscitation transfer.",
    },
    {
      action: "REFER",
      label: "Refer Facility",
      variant: "secondary",
      icon: <Share2 style={{ width: 14, height: 14 }} aria-hidden="true" />,
      desc: "Initiate inter-facility SBAR handoff to tertiary center.",
    },
  ];

  return (
    <div
      className="clinova-card"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-4)",
        backgroundColor: "#ffffff",
        border: "1px solid var(--clinova-border-strong)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <span className="clinova-label" style={{ color: "var(--clinova-text-primary)" }}>
            CLINICIAN DECISION GATE
          </span>
          <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
            Authoritative physician review by <strong>{clinicianName}</strong>
          </p>
        </div>
        <span
          className="clinova-badge"
          style={{ backgroundColor: "#f1f5f9", color: "#334155", borderColor: "#cbd5e1" }}
        >
          HUMAN-IN-THE-LOOP
        </span>
      </div>

      {successMessage && (
        <div
          role="status"
          style={{
            backgroundColor: "var(--clinova-success-bg)",
            border: "1px solid var(--clinova-success-border)",
            color: "var(--clinova-success-text)",
            padding: "8px 12px",
            borderRadius: "var(--clinova-radius-md)",
            fontSize: "0.8125rem",
          }}
        >
          {successMessage}
        </div>
      )}

      {/* Action Buttons Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
        {actionButtons.map((btn) => (
          <button
            key={btn.action}
            type="button"
            onClick={() => {
              setSelectedAction(btn.action);
              setSuccessMessage(null);
            }}
            className="clinova-btn"
            style={{
              justifyContent: "flex-start",
              fontSize: "0.8125rem",
              padding: "6px 10px",
              height: "auto",
              minHeight: 38,
              border: selectedAction === btn.action
                ? "2px solid var(--clinova-accent)"
                : "1px solid var(--clinova-border)",
              backgroundColor: selectedAction === btn.action
                ? "var(--clinova-accent-light)"
                : "var(--clinova-surface)",
              color: selectedAction === btn.action
                ? "var(--clinova-accent-text)"
                : "var(--clinova-text-primary)",
            }}
            title={btn.desc}
          >
            {btn.icon}
            <span style={{ fontWeight: 600 }}>{btn.label}</span>
          </button>
        ))}
      </div>

      {/* Decision Rationale Input & Final Commit */}
      {selectedAction && (
        <div
          style={{
            backgroundColor: "var(--clinova-surface-subtle)",
            border: "1px solid var(--clinova-border)",
            borderRadius: "var(--clinova-radius-md)",
            padding: "var(--clinova-space-3)",
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.8125rem", fontWeight: 700 }}>
              Action Selected: <span style={{ color: "var(--clinova-accent)" }}>{selectedAction}</span>
            </span>
            <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
              Mandatory Audit Log
            </span>
          </div>

          <textarea
            className="clinova-textarea"
            style={{ minHeight: 64, fontSize: "0.8125rem" }}
            placeholder={`Enter clinical rationale for [${selectedAction}] on Case ${caseId}...`}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedAction(null)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleExecute}
              loading={isSubmitting}
              disabled={isSubmitting || ((selectedAction === "REJECT" || selectedAction === "MODIFY") && !notes.trim())}
            >
              <Send style={{ width: 12, height: 12 }} aria-hidden="true" />
              <span>Commit Decision & Sign Off</span>
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
