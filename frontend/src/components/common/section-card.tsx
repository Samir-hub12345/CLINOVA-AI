"use client";

import React from "react";

export interface SectionCardProps {
  title: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  bodyClassName?: string;
}

export const SectionCard: React.FC<SectionCardProps> = ({
  title,
  description,
  icon: Icon,
  action,
  children,
  className = "",
  bodyClassName = "p-5 md:p-6",
}) => {
  return (
    <div
      className={`overflow-hidden rounded-2xl bg-white border border-slate-200/90 shadow-sm ${className}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/50 px-5 py-4 md:px-6">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50 text-teal-700 border border-teal-100">
              <Icon className="h-4 w-4" />
            </div>
          )}
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">{title}</h2>
            {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
          </div>
        </div>
        {action && <div className="flex items-center gap-2">{action}</div>}
      </div>
      <div className={bodyClassName}>{children}</div>
    </div>
  );
};
