"use client";

import React from "react";
import Link from "next/link";
import { Clock, Sparkles, UserCheck, ArrowRight } from "lucide-react";

export interface ActivityItem {
  id: string;
  actor: string;
  action: string;
  source: string;
  time: string;
  isAi: boolean;
}

export const DEFAULT_RECENT_ACTIVITY: ActivityItem[] = [
  {
    id: "act-1",
    actor: "Clinova AI",
    action: "Calculated NEWS2 score (8 - High)",
    source: "Bedside vitals acquisition • Bay 2",
    time: "10 mins ago",
    isAi: true,
  },
  {
    id: "act-2",
    actor: "Dr. Priya Sharma",
    action: "Verified ECG findings & signed admission",
    source: "Encounter ENC-5310 • Acute Coronary Bay",
    time: "24 mins ago",
    isAi: false,
  },
  {
    id: "act-3",
    actor: "Ananya Patel, RN",
    action: "Completed triage intake & shock index check",
    source: "Triage Queue • Cuttack DHH",
    time: "42 mins ago",
    isAi: false,
  },
  {
    id: "act-4",
    actor: "Clinova AI",
    action: "Prepared SBAR transfer dossier",
    source: "FacilityGraph referral to SCB Cath Lab",
    time: "1 hour ago",
    isAi: true,
  },
];

interface RecentActivityWidgetProps {
  activity?: ActivityItem[];
  compact?: boolean;
}

export const RecentActivityWidget: React.FC<RecentActivityWidgetProps> = ({
  activity = DEFAULT_RECENT_ACTIVITY,
  compact = false,
}) => {
  return (
    <div className="card" aria-labelledby="audit-heading">
      <div className="card-header">
        <div className="row gap-2">
          <Clock style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
          <h2 id="audit-heading" style={{ margin: 0, fontSize: "1.125rem", fontWeight: 700 }}>
            Recent Clinical Activity
          </h2>
        </div>
        <Link href="/system" className="small" style={{ color: "var(--teal-700)" }}>
          View Audit Ledger
        </Link>
      </div>
      <div className="card-body">
        <ol className="list-reset timeline">
          {activity.map((act) => (
            <li key={act.id} className="timeline-item">
              <span className="timeline-dot">
                {act.isAi ? (
                  <Sparkles style={{ width: 8, height: 8, color: "var(--teal-600)" }} aria-hidden="true" />
                ) : (
                  <UserCheck style={{ width: 8, height: 8, color: "var(--success)" }} aria-hidden="true" />
                )}
              </span>
              <div className="stack" style={{ gap: 2 }}>
                <div className="small">
                  <span className="medium" style={{ color: "var(--navy-900)" }}>
                    {act.actor}
                  </span>{" "}
                  <span className="subtle">{act.action}</span>
                </div>
                <div className="xs muted">
                  {act.source} • {act.time}
                </div>
              </div>
            </li>
          ))}
        </ol>
      </div>
      {!compact && (
        <div className="card-footer">
          <Link href="/system" className="btn btn-secondary btn-sm btn-block">
            <span>Inspect Cryptographic SHA-256 Ledger</span>
            <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
          </Link>
        </div>
      )}
    </div>
  );
};
