"use client";

import React from "react";

export interface ColumnDef<T> {
  header: string;
  accessor?: (row: T) => React.ReactNode;
  field?: keyof T;
  align?: "left" | "center" | "right";
  width?: string | number;
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  keyExtractor: (row: T, index: number) => string;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  ariaLabel?: string;
  rowHighlight?: (row: T) => boolean;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  emptyMessage = "No clinical records found.",
  ariaLabel = "Clinical Data Table",
  rowHighlight,
}: DataTableProps<T>): React.ReactElement {
  return (
    <div className="clinova-table-wrapper" role="region" aria-label={ariaLabel} tabIndex={0}>
      <table className="clinova-table">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={idx}
                style={{
                  textAlign: col.align || "left",
                  width: col.width,
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: "center", padding: 24, fontStyle: "italic", color: "var(--clinova-text-muted)" }}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIdx) => {
              const isHighlighted = rowHighlight ? rowHighlight(row) : false;
              return (
                <tr
                  key={keyExtractor(row, rowIdx)}
                  onClick={() => onRowClick && onRowClick(row)}
                  style={{
                    cursor: onRowClick ? "pointer" : undefined,
                    backgroundColor: isHighlighted ? "rgba(254, 242, 242, 0.45)" : undefined,
                  }}
                >
                  {columns.map((col, colIdx) => {
                    const content = col.accessor
                      ? col.accessor(row)
                      : col.field
                      ? String(row[col.field] ?? "")
                      : null;
                    return (
                      <td
                        key={colIdx}
                        style={{
                          textAlign: col.align || "left",
                        }}
                      >
                        {content}
                      </td>
                    );
                  })}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
