"use client";

import React, { useState } from "react";
import { Download, FileText, CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { downloadCaseReportPdf, getCaseReportPdfUrl } from "@/lib/api";

interface DownloadReportButtonProps {
  caseId: string;
  variant?: "primary" | "secondary" | "outline";
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const DownloadReportButton: React.FC<DownloadReportButtonProps> = ({
  caseId,
  variant = "primary",
  label = "Download Care Summary (PDF)",
  size = "md",
  className = "",
}) => {
  const [loading, setLoading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    setDownloadSuccess(false);

    try {
      const blob = await downloadCaseReportPdf(caseId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `clinova_report_${caseId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status;
      if (status === 401) {
        setError("Session expired. Please sign in again.");
      } else if (status === 403) {
        setError("Access denied: You are not authorized to download this report.");
      } else if (status === 404) {
        setError("Report not found for this case.");
      } else {
        try {
          const directUrl = getCaseReportPdfUrl(caseId);
          window.open(directUrl, "_blank");
        } catch {
          setError("Report download unavailable. Please try again.");
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const getBtnClass = () => {
    if (className) return className;
    if (variant === "primary") return `btn btn-primary ${size === "sm" ? "btn-sm" : size === "lg" ? "btn-lg" : ""}`;
    if (variant === "secondary") return `btn btn-secondary ${size === "sm" ? "btn-sm" : size === "lg" ? "btn-lg" : ""}`;
    return `btn btn-outline ${size === "sm" ? "btn-sm" : size === "lg" ? "btn-lg" : ""}`;
  };

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: 4 }}>
      <button
        type="button"
        onClick={handleDownload}
        disabled={loading}
        className={getBtnClass()}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          cursor: loading ? "wait" : "pointer",
        }}
        title={`Download official tamper-evident PDF report for Case ${caseId}`}
      >
        {loading ? (
          <Loader2 style={{ width: 15, height: 15, animation: "spin 1s linear infinite" }} aria-hidden="true" />
        ) : downloadSuccess ? (
          <CheckCircle style={{ width: 15, height: 15, color: "var(--success)" }} aria-hidden="true" />
        ) : (
          <Download style={{ width: 15, height: 15 }} aria-hidden="true" />
        )}
        <span>{loading ? "Generating PDF..." : downloadSuccess ? "Report Downloaded!" : label}</span>
      </button>

      {error && (
        <span className="xs text-danger" style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <AlertTriangle style={{ width: 12, height: 12 }} aria-hidden="true" />
          <span>{error}</span>
        </span>
      )}
    </div>
  );
};
