"use client";

import React from "react";
import Link from "next/link";
import {
  FileCheck2,
  FileText,
  AlertTriangle,
  Activity,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";

export interface TaskQueueItem {
  id: string;
  title: string;
  who: string;
  to: string;
  badge: string;
  icon: React.ComponentType<{ style?: React.CSSProperties; "aria-hidden"?: boolean | "true" | "false" }>;
}

export const DEFAULT_TASK_QUEUE_ITEMS: TaskQueueItem[] = [
  {
    id: "task-1",
    title: "Consultation note awaiting review",
    who: "Dr. Priya Sharma • Patient Manoj Das (Chest Pain)",
    to: "/staff/review",
    badge: "tile-navy",
    icon: FileText,
  },
  {
    id: "task-2",
    title: "Missing information in patient record",
    who: "Epistemic Check • Conflicting lisinopril dosage",
    to: "/staff/cases/CASE-SYNTH-003",
    badge: "tile-warning",
    icon: AlertTriangle,
  },
  {
    id: "task-3",
    title: "Laboratory result awaiting clinician review",
    who: "Biochemistry • Cardiac Troponin-I: 0.12 ng/mL (High)",
    to: "/staff/cases/CASE-SYNTH-003",
    badge: "tile-info",
    icon: Activity,
  },
  {
    id: "task-4",
    title: "Follow-up instructions awaiting approval",
    who: "Odia/Hindi Vernacular • BP monitoring schedule",
    to: "/patient/case/CASE-SYNTH-003",
    badge: "tile-teal",
    icon: CheckCircle2,
  },
];

interface ClinicalReviewQueueWidgetProps {
  tasks?: TaskQueueItem[];
  badgeText?: string;
  showFooter?: boolean;
}

export const ClinicalReviewQueueWidget: React.FC<ClinicalReviewQueueWidgetProps> = ({
  tasks = DEFAULT_TASK_QUEUE_ITEMS,
  badgeText = "4 Need Attention",
  showFooter = true,
}) => {
  return (
    <div className="card" aria-labelledby="tasks-heading">
      <div className="card-header">
        <div className="row gap-2">
          <FileCheck2 style={{ width: 18, height: 18, color: "var(--warning)" }} aria-hidden="true" />
          <h2 id="tasks-heading" style={{ margin: 0, fontSize: "1.125rem", fontWeight: 700 }}>
            Clinical Review Queue
          </h2>
        </div>
        <span className="badge badge-warning">{badgeText}</span>
      </div>
      <div className="card-body" style={{ padding: 0 }}>
        <ul className="list-reset">
          {tasks.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.id} style={{ borderBottom: "1px solid var(--border)" }}>
                <Link
                  href={item.to}
                  className="row between gap-3 interactive"
                  style={{
                    padding: "12px 18px",
                    color: "inherit",
                    textDecoration: "none",
                    display: "flex",
                  }}
                >
                  <div className="row gap-3">
                    <span className={`icon-tile ${item.badge}`} style={{ width: 32, height: 32 }}>
                      <Icon style={{ width: 16, height: 16 }} aria-hidden="true" />
                    </span>
                    <div className="stack gap-1">
                      <span className="small medium" style={{ color: "var(--navy-900)" }}>
                        {item.title}
                      </span>
                      <span className="xs muted">{item.who}</span>
                    </div>
                  </div>
                  <ArrowRight style={{ width: 15, height: 15, color: "var(--text-4)" }} aria-hidden="true" />
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
      {showFooter && (
        <div className="card-footer">
          <Link href="/staff/review" className="btn btn-secondary btn-sm btn-block">
            <span>View Full Attending Review Worklist</span>
            <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
          </Link>
        </div>
      )}
    </div>
  );
};
