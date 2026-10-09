"use client";

import React from "react";

export interface FilterOption {
  id: string;
  label: string;
  count?: number;
}

interface FilterBarProps {
  label?: string;
  options: FilterOption[];
  selectedId: string;
  onSelect: (id: string) => void;
  ariaLabel?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  label,
  options,
  selectedId,
  onSelect,
  ariaLabel = "Filter Options",
}) => {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        flexWrap: "wrap",
      }}
    >
      {label && (
        <span className="clinova-label" style={{ marginRight: 4 }}>
          {label}
        </span>
      )}
      {options.map((opt) => {
        const isSelected = selectedId === opt.id;
        return (
          <button
            key={opt.id}
            type="button"
            onClick={() => onSelect(opt.id)}
            aria-pressed={isSelected}
            className="clinova-btn clinova-btn-sm"
            style={{
              backgroundColor: isSelected ? "var(--clinova-accent)" : "var(--clinova-surface-subtle)",
              color: isSelected ? "#ffffff" : "var(--clinova-text-secondary)",
              border: "1px solid var(--clinova-border)",
              fontWeight: isSelected ? 700 : 500,
              gap: 4,
            }}
          >
            <span>{opt.label}</span>
            {opt.count !== undefined && (
              <span
                style={{
                  fontSize: "0.6875rem",
                  padding: "0 5px",
                  borderRadius: "var(--clinova-radius-pill)",
                  backgroundColor: isSelected ? "rgba(255, 255, 255, 0.25)" : "var(--clinova-border)",
                  color: isSelected ? "#ffffff" : "var(--clinova-text-primary)",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {opt.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
