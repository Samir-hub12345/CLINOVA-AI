import React from "react";
import { TimelineEventItem } from "@/types";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { UncertaintyIndicator } from "./UncertaintyIndicator";

interface TimelineEventProps {
  event: TimelineEventItem;
}

export const TimelineEvent: React.FC<TimelineEventProps> = ({ event }) => {
  return (
    <div className="clinova-timeline-item">
      <div
        className={`clinova-timeline-dot ${event.is_red_flag ? "clinova-timeline-dot-alert" : ""}`}
        aria-hidden="true"
      />
      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
          <span className="clinova-mono" style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)", fontWeight: 600 }}>
            {event.timestamp}
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <ProvenanceBadge provenance={event.provenance} showIcon={false} />
            <UncertaintyIndicator status={event.epistemic_status} />
          </div>
        </div>

        <h5 style={{ fontSize: "0.9375rem", color: event.is_red_flag ? "var(--clinova-danger-text)" : "var(--clinova-text-primary)" }}>
          {event.title}
        </h5>

        <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
          {event.description}
        </p>
      </div>
    </div>
  );
};

export const Timeline: React.FC<{
  events: TimelineEventItem[];
}> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div style={{ color: "var(--clinova-text-muted)", fontSize: "0.875rem", fontStyle: "italic", padding: 12 }}>
        No chronological timeline events logged.
      </div>
    );
  }

  return (
    <div className="clinova-timeline">
      {events.map((ev) => (
        <TimelineEvent key={ev.id} event={ev} />
      ))}
    </div>
  );
};
