"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  FileText,
  Upload,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Download,
  ExternalLink,
  Trash2,
  RefreshCw,
  Clock,
  Layers,
  FileCheck,
  AlertTriangle,
  Plus,
  X,
  FileCode,
  HardDrive,
} from "lucide-react";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { documentsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { MedicalDocument, DocumentArtifact } from "@/types";

const DOC_TYPES = [
  { value: "discharge_summary", label: "Discharge Summary" },
  { value: "clinical_note", label: "Clinical Note" },
  { value: "lab_report", label: "Lab Report" },
  { value: "radiology_image", label: "Radiology Image" },
  { value: "prescription", label: "Prescription" },
  { value: "referral_letter", label: "Referral Letter" },
  { value: "consent_form", label: "Consent Form" },
];

export default function DocumentsPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<MedicalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>("");
  const [includeArchived, setIncludeArchived] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [amendModalOpen, setAmendModalOpen] = useState(false);
  const [artifactsModalOpen, setArtifactsModalOpen] = useState(false);
  const [activeDoc, setActiveDoc] = useState<MedicalDocument | null>(null);
  const [activeArtifacts, setActiveArtifacts] = useState<DocumentArtifact[]>([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Upload Form State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDocType, setUploadDocType] = useState("discharge_summary");
  const [uploadPatientId, setUploadPatientId] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const amendFileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await documentsApi.listDocuments({
        document_type: selectedType || undefined,
        include_archived: includeArchived,
      });
      if (res.data) {
        const docs = Array.isArray(res.data) ? res.data : ((res.data as any)?.items || []);
        setDocuments(docs);
      }
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [selectedType, includeArchived]);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) {
      setStatusMessage({ type: "error", text: "Please select a file to upload." });
      return;
    }

    setActionLoading(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("document_type", uploadDocType);
    if (uploadPatientId.trim()) {
      formData.append("patient_id", uploadPatientId.trim());
    }

    try {
      const res = await documentsApi.uploadDocument(formData);
      if (res.error) {
        setStatusMessage({ type: "error", text: res.error });
      } else {
        setStatusMessage({
          type: "success",
          text: `Document '${res.data?.filename}' uploaded successfully (Scan: ${res.data?.scan_status}).`,
        });
        setUploadModalOpen(false);
        setUploadFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        fetchDocuments();
      }
    } catch (err: any) {
      setStatusMessage({ type: "error", text: err.message || "Upload failed." });
    } finally {
      setActionLoading(false);
    }
  };

  const handleAmendSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeDoc || !uploadFile) return;

    setActionLoading(true);
    setStatusMessage(null);

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await documentsApi.amendDocument(activeDoc.id, formData);
      if (res.error) {
        setStatusMessage({ type: "error", text: res.error });
      } else {
        setStatusMessage({
          type: "success",
          text: `Document amended to v${res.data?.version} successfully.`,
        });
        setAmendModalOpen(false);
        setUploadFile(null);
        fetchDocuments();
      }
    } catch (err: any) {
      setStatusMessage({ type: "error", text: err.message || "Amendment failed." });
    } finally {
      setActionLoading(false);
    }
  };

  const handlePresignedAccess = async (doc: MedicalDocument) => {
    try {
      const res = await documentsApi.getPresignedUrl(doc.id, 15);
      if (res.data?.access_url) {
        const fullUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${res.data.access_url}`;
        window.open(fullUrl, "_blank");
      } else if (res.error) {
        setStatusMessage({ type: "error", text: res.error });
      }
    } catch (err: any) {
      setStatusMessage({ type: "error", text: "Failed to generate presigned URL." });
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to archive / soft-delete this medical document?")) return;

    try {
      const res = await documentsApi.deleteDocument(docId);
      if (res.error) {
        setStatusMessage({ type: "error", text: res.error });
      } else {
        setStatusMessage({ type: "success", text: "Document marked as archived." });
        fetchDocuments();
      }
    } catch (err: any) {
      setStatusMessage({ type: "error", text: "Failed to delete document." });
    }
  };

  const handleViewArtifacts = async (doc: MedicalDocument) => {
    setActiveDoc(doc);
    setArtifactsModalOpen(true);
    try {
      const res = await documentsApi.listArtifacts(doc.id);
      if (res.data) {
        setActiveArtifacts(res.data);
      }
    } catch (err) {
      console.error("Failed to load artifacts", err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getScanBadge = (scanStatus: string) => {
    switch (scanStatus?.toLowerCase()) {
      case "clean":
        return (
          <Badge className="bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" /> Clean
          </Badge>
        );
      case "quarantined":
      case "infected":
        return (
          <Badge className="bg-rose-500/10 text-rose-600 border border-rose-500/20 flex items-center gap-1">
            <ShieldAlert className="w-3 h-3" /> Quarantined
          </Badge>
        );
      default:
        return (
          <Badge className="bg-amber-500/10 text-amber-600 border border-amber-500/20 flex items-center gap-1">
            <Clock className="w-3 h-3" /> Pending Scan
          </Badge>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Heading & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">Medical Documents & Object Storage</h1>
              <Badge variant="outline" className="text-xs bg-cyan-50 border-cyan-300 text-cyan-800">
                Phase 3 Active
              </Badge>
            </div>
            <p className="text-sm text-slate-500 mt-1">
              Zero raw binary DB storage. Secure magic-byte validated & malware-scanned clinical repository.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDocuments}
              className="flex items-center gap-2"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button
              onClick={() => setUploadModalOpen(true)}
              className="bg-cyan-600 hover:bg-cyan-700 text-white flex items-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Upload Document
            </Button>
          </div>
        </div>

        {/* Status Alert */}
        {statusMessage && (
          <div
            className={`p-4 rounded-lg mb-6 text-sm flex items-center justify-between ${
              statusMessage.type === "success"
                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                : "bg-rose-50 text-rose-800 border border-rose-200"
            }`}
          >
            <span>{statusMessage.text}</span>
            <button
              onClick={() => setStatusMessage(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Security / Architecture Banner */}
        <div className="mb-6 rounded-xl border border-slate-200 bg-gradient-to-r from-cyan-900 to-slate-900 text-white shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-md bg-cyan-500/20 text-cyan-300">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Pre-Upload Magic Bytes</h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Strict byte signature inspection detects disguised EXEs, ELFs, and scripts.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-md bg-emerald-500/20 text-emerald-300">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Anti-Malware & Quarantine</h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Threats are isolated into an unmapped quarantine directory with 403 blocks.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-md bg-indigo-500/20 text-indigo-300">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Storage Abstraction</h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Tenant-isolated keys with local disk and private S3 compatibility.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-md bg-amber-500/20 text-amber-300">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">HMAC Presigned URLs</h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Time-limited signed tokens provide direct, authorized clinical access.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-xs font-medium text-slate-500">Document Type:</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="text-sm border border-slate-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Types</option>
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>

            <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={includeArchived}
                onChange={(e) => setIncludeArchived(e.target.checked)}
                className="rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
              />
              Show Archived Records
            </label>
          </div>

          <div className="text-xs text-slate-500">
            Total records: <span className="font-semibold text-slate-800">{documents.length}</span>
          </div>
        </div>

        {/* Documents Table */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          {loading ? (
            <div className="p-12 text-center text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-600" />
              Loading clinical documents...
            </div>
          ) : documents.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              <FileText className="w-10 h-10 mx-auto mb-3 text-slate-300" />
              <p className="font-medium text-slate-600">No documents found</p>
              <p className="text-xs mt-1 text-slate-400">Upload medical records to begin clinical storage.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <th className="py-3 px-4">Document / File</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Version</th>
                    <th className="py-3 px-4">Security Scan</th>
                    <th className="py-3 px-4">Size / Hash</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Uploaded</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {documents.map((doc) => (
                    <tr
                      key={doc.id}
                      className={`hover:bg-slate-50/75 transition-colors ${
                        doc.status === "archived" ? "opacity-60 bg-slate-50" : ""
                      }`}
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="p-2 rounded bg-cyan-50 text-cyan-700">
                            <FileText className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="font-medium text-slate-900">{doc.filename}</div>
                            <div className="text-xs text-slate-400">{doc.mime_type}</div>
                          </div>
                        </div>
                      </td>

                      <td className="py-3 px-4">
                        <Badge variant="outline" className="capitalize text-xs font-normal">
                          {doc.document_type.replace(/_/g, " ")}
                        </Badge>
                      </td>

                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">
                          v{doc.version}
                        </span>
                        {!doc.is_current_version && (
                          <span className="text-[10px] text-amber-600 block">superseded</span>
                        )}
                      </td>

                      <td className="py-3 px-4">{getScanBadge(doc.scan_status)}</td>

                      <td className="py-3 px-4">
                        <div className="text-xs text-slate-700 font-mono">
                          {formatFileSize(doc.file_size_bytes)}
                        </div>
                        <div
                          className="text-[11px] font-mono text-slate-400 truncate max-w-[120px]"
                          title={doc.checksum_sha256}
                        >
                          {doc.checksum_sha256?.substring(0, 10)}...
                        </div>
                      </td>

                      <td className="py-3 px-4">
                        <Badge
                          className={`capitalize text-xs ${
                            doc.status === "stored"
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : doc.status === "quarantined"
                              ? "bg-rose-50 text-rose-700 border-rose-200"
                              : "bg-slate-100 text-slate-600"
                          }`}
                        >
                          {doc.status}
                        </Badge>
                      </td>

                      <td className="py-3 px-4 text-xs text-slate-500 whitespace-nowrap">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>

                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          {doc.scan_status !== "quarantined" && doc.status !== "archived" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handlePresignedAccess(doc)}
                                className="h-8 px-2 text-cyan-600 hover:text-cyan-700 hover:bg-cyan-50"
                                title="Open Presigned Access"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </Button>

                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setActiveDoc(doc);
                                  setAmendModalOpen(true);
                                }}
                                className="h-8 px-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                                title="Amend (Upload New Version)"
                              >
                                <Layers className="w-3.5 h-3.5" />
                              </Button>
                            </>
                          )}

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewArtifacts(doc)}
                            className="h-8 px-2 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                            title="Derived Artifacts"
                          >
                            <FileCode className="w-3.5 h-3.5" />
                          </Button>

                          {doc.status !== "archived" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(doc.id)}
                              className="h-8 px-2 text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                              title="Archive / Soft Delete"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Upload className="w-5 h-5 text-cyan-600" />
                Upload Clinical Document
              </h3>
              <button
                onClick={() => setUploadModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Document Type
                </label>
                <select
                  value={uploadDocType}
                  onChange={(e) => setUploadDocType(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-cyan-500"
                >
                  {DOC_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Patient ID (Optional)
                </label>
                <input
                  type="text"
                  placeholder="UUID or leave empty for unassigned"
                  value={uploadPatientId}
                  onChange={(e) => setUploadPatientId(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Medical File (PDF, JPEG, PNG, TIFF, DICOM)
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  File signatures are inspected via magic bytes. Disguised executables (.exe, .sh) are rejected.
                </p>
              </div>

              <div className="bg-cyan-50 p-3 rounded-lg border border-cyan-100 flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 text-cyan-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-cyan-900 leading-relaxed">
                  Files are streamed directly to tenant-isolated storage paths. SHA-256 integrity checksums and real-time antivirus scans are computed automatically.
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setUploadModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={actionLoading || !uploadFile}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white flex items-center gap-2"
                >
                  {actionLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  Upload Securely
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Amend / New Version Modal */}
      {amendModalOpen && activeDoc && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-600" />
                Amend Medical Document (v{activeDoc.version} → v{activeDoc.version + 1})
              </h3>
              <button
                onClick={() => setAmendModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500 mb-4">
              Amending creates a new immutable version while preserving the historical audit trail of prior versions.
            </p>

            <form onSubmit={handleAmendSubmit} className="space-y-4">
              <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1">
                <div><strong>Current Document:</strong> {activeDoc.filename}</div>
                <div><strong>Document ID:</strong> {activeDoc.id}</div>
                <div><strong>Type:</strong> {activeDoc.document_type}</div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Amended Replacement File
                </label>
                <input
                  type="file"
                  ref={amendFileInputRef}
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setAmendModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={actionLoading || !uploadFile}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-2"
                >
                  {actionLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4" />}
                  Save Amendment
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Derived Artifacts Modal */}
      {artifactsModalOpen && activeDoc && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 border border-slate-200 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <FileCode className="w-5 h-5 text-indigo-600" />
                  Derived Artifacts
                </h3>
                <p className="text-xs text-slate-500">{activeDoc.filename} (ID: {activeDoc.id})</p>
              </div>
              <button
                onClick={() => setArtifactsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4">
              {activeArtifacts.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-xs">
                  No derived OCR or analytical artifacts attached to this document yet.
                </div>
              ) : (
                activeArtifacts.map((art) => (
                  <div key={art.id} className="border border-slate-200 rounded-lg p-3 bg-slate-50 text-xs">
                    <div className="flex items-center justify-between font-semibold text-slate-800 mb-1">
                      <span>{art.filename}</span>
                      <Badge variant="outline" className="text-[10px] uppercase">
                        {art.artifact_type}
                      </Badge>
                    </div>
                    <div className="text-slate-500 text-[11px] mb-2">
                      MIME: {art.mime_type} | Size: {formatFileSize(art.file_size_bytes)}
                    </div>
                    {art.content_text && (
                      <pre className="p-2.5 bg-white rounded border border-slate-200 text-slate-800 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap max-h-40">
                        {art.content_text}
                      </pre>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setArtifactsModalOpen(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}
