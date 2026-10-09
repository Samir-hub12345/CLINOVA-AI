"use client";

import React, { useState } from "react";
import { Upload, FileText, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DocumentUploadProps {
  caseId: string;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ caseId }) => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const handleSimulateUpload = () => {
    setSelectedFile("sample_lab_report.pdf");
    setUploadStatus("Document staged for Phase 20 OCR processing.");
  };

  return (
    <div className="clinova-card" style={{ padding: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <span className="clinova-label">CLINICAL DOCUMENTS & OCR</span>
        <span className="clinova-badge" style={{ backgroundColor: "#f8fafc", color: "#64748b", fontSize: "0.6875rem" }}>
          Case {caseId.substring(0, 8)}...
        </span>
      </div>
      <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)", marginBottom: 8 }}>
        Attach supplementary medical records or prescriptions for OCR extraction and timeline indexing.
      </p>

      {uploadStatus ? (
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", color: "var(--clinova-success-text)" }}>
          <CheckCircle2 style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>{selectedFile}: {uploadStatus}</span>
        </div>
      ) : (
        <div style={{ display: "flex", gap: 8 }}>
          <Button variant="outline" size="sm" onClick={handleSimulateUpload}>
            <Upload style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Select Document</span>
          </Button>
          <div style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--clinova-text-muted)", fontSize: "0.75rem" }}>
            <FileText style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>PDF, JPEG, PNG (up to 10MB)</span>
          </div>
        </div>
      )}
    </div>
  );
};
