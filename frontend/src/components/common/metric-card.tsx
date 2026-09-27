"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export type MetricColor = "teal" | "blue" | "emerald" | "amber" | "rose" | "purple" | "slate";

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ComponentType<{ className?: string }>;
  trend?: {
    direction?: "up" | "down" | "neutral";
    value?: string;
    label?: string;
  };
  statusColor?: MetricColor;
  badge?: string;
  onClick?: () => void;
  className?: string;
}

const colorStyles: Record<
  MetricColor,
  {
    bgIcon: string;
    textIcon: string;
    border: string;
    badgeBg: string;
    badgeText: string;
  }
> = {
  teal: {
    bgIcon: "bg-teal-50",
    textIcon: "text-teal-600",
    border: "border-teal-100",
    badgeBg: "bg-teal-50",
    badgeText: "text-teal-700",
  },
  blue: {
    bgIcon: "bg-sky-50",
    textIcon: "text-sky-600",
    border: "border-sky-100",
    badgeBg: "bg-sky-50",
    badgeText: "text-sky-700",
  },
  emerald: {
    bgIcon: "bg-emerald-50",
    textIcon: "text-emerald-600",
    border: "border-emerald-100",
    badgeBg: "bg-emerald-50",
    badgeText: "text-emerald-700",
  },
  amber: {
    bgIcon: "bg-amber-50",
    textIcon: "text-amber-600",
    border: "border-amber-100",
    badgeBg: "bg-amber-50",
    badgeText: "text-amber-700",
  },
  rose: {
    bgIcon: "bg-rose-50",
    textIcon: "text-rose-600",
    border: "border-rose-100",
    badgeBg: "bg-rose-50",
    badgeText: "text-rose-700",
  },
  purple: {
    bgIcon: "bg-purple-50",
    textIcon: "text-purple-600",
    border: "border-purple-100",
    badgeBg: "bg-purple-50",
    badgeText: "text-purple-700",
  },
  slate: {
    bgIcon: "bg-slate-100",
    textIcon: "text-slate-600",
    border: "border-slate-200",
    badgeBg: "bg-slate-100",
    badgeText: "text-slate-700",
  },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  statusColor = "teal",
  badge,
  onClick,
  className = "",
}) => {
  const styles = colorStyles[statusColor] || colorStyles.teal;

  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      className={`group relative overflow-hidden rounded-2xl bg-white p-5 md:p-6 border border-slate-200/90 shadow-sm transition-all duration-200 hover:shadow-md ${
        onClick ? "cursor-pointer hover:border-slate-300" : ""
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <div className="flex items-baseline gap-2 pt-1">
            <span className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">
              {value}
            </span>
            {badge && (
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles.badgeBg} ${styles.badgeText} border ${styles.border}`}
              >
                {badge}
              </span>
            )}
          </div>
        </div>

        {Icon && (
          <div
            className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${styles.bgIcon} ${styles.textIcon} border ${styles.border} shadow-xs transition-transform group-hover:scale-105`}
          >
            <Icon className="h-6 w-6" />
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-4 flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
          {trend && (
            <span
              className={`inline-flex items-center gap-1 font-semibold ${
                trend.direction === "up"
                  ? "text-emerald-700"
                  : trend.direction === "down"
                  ? "text-rose-700"
                  : "text-slate-600"
              }`}
            >
              {trend.direction === "up" && <TrendingUp className="h-3.5 w-3.5" />}
              {trend.direction === "down" && <TrendingDown className="h-3.5 w-3.5" />}
              {trend.direction === "neutral" && <Minus className="h-3.5 w-3.5" />}
              {trend.value}
            </span>
          )}
          {trend?.label && <span className="text-slate-500">{trend.label}</span>}
          {!trend && subtitle && <span className="text-slate-500">{subtitle}</span>}
        </div>
      )}
    </div>
  );
};
