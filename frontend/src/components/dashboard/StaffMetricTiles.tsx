"use client";

import React from "react";
import Link from "next/link";
import { Users, Stethoscope, FileCheck2, Share2 } from "lucide-react";

export interface MetricTileItem {
  label: string;
  value: string;
  note: string;
  icon: React.ComponentType<{ style?: React.CSSProperties; "aria-hidden"?: boolean | "true" | "false" }>;
  tile: string;
  to: string;
}

export const DEFAULT_METRIC_TILES: MetricTileItem[] = [
  {
    label: "Patients Scheduled Today",
    value: "24",
    note: "18 seen & evaluated so far",
    icon: Users,
    tile: "tile-navy",
    to: "/staff/triage",
  },
  {
    label: "Consultations in Progress",
    value: "6",
    note: "Across 4 active clinical bays",
    icon: Stethoscope,
    tile: "tile-info",
    to: "/staff/reception",
  },
  {
    label: "Notes Awaiting Clinician Review",
    value: "4",
    note: "Physician sign-off & human gate",
    icon: FileCheck2,
    tile: "tile-warning",
    to: "/staff/review",
  },
  {
    label: "SBAR Transfers & Follow-Ups",
    value: "8",
    note: "Regional telemetry active",
    icon: Share2,
    tile: "tile-teal",
    to: "/referrals",
  },
];

interface StaffMetricTilesProps {
  tiles?: MetricTileItem[];
}

export const StaffMetricTiles: React.FC<StaffMetricTilesProps> = ({
  tiles = DEFAULT_METRIC_TILES,
}) => {
  return (
    <div className="grid grid-4 gap-4">
      {tiles.map((tile) => {
        const Icon = tile.icon;
        return (
          <Link
            key={tile.label}
            href={tile.to}
            className="card interactive metric-card"
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div className="row between">
              <span className="small subtle medium">{tile.label}</span>
              <span className={`icon-tile ${tile.tile}`}>
                <Icon aria-hidden="true" />
              </span>
            </div>
            <div className="stat-value" style={{ color: "var(--navy-900)" }}>
              {tile.value}
            </div>
            <div className="xs muted">{tile.note}</div>
          </Link>
        );
      })}
    </div>
  );
};
