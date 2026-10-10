"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { RoleGuard } from "@/components/common/RoleGuard";
import {
  UserPlus,
  Search,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Clock,
  Activity,
  CheckCircle2,
  FileText,
  Users,
  Filter,
  Check,
} from "lucide-react";
import { submitPatientIntake, getClinicalQueue, QueueResponse } from "@/lib/api";
import { QueueItem } from "@/types";
import { DownloadReportButton } from "@/components/common/DownloadReportButton";

interface SyntheticPatientRecord {
  id: string;
  synthetic_token: string;
  name: string;
  age_bracket: string;
  sex: string;
  phone: string;
  pathway: "OPD_GENERAL" | "EMERGENCY";
  consent: boolean;
  status: "Registered" | "Triage Pending" | "In Review" | "Completed";
  registered_at: string;
  chief_complaint: string;
}

const INITIAL_RECORDS: SyntheticPatientRecord[] = [
  {
    id: "REC-PT-001",
    synthetic_token: "PT-SYN-0014",
    name: "Priya Das",
    age_bracket: "25-35 YRS",
    sex: "FEMALE",
    phone: "+91 98765 43210",
    pathway: "OPD_GENERAL",
    consent: true,
    status: "Triage Pending",
    registered_at: "Today, 08:30 AM",
    chief_complaint: "Mild persistent cough and sore throat for 3 days",
  },
  {
    id: "REC-PT-002",
    synthetic_token: "PT-SYN-0842",
    name: "Rajesh Kumar",
    age_bracket: "50-65 YRS",
    sex: "MALE",
    phone: "+91 94321 09876",
    pathway: "EMERGENCY",
    consent: true,
    status: "In Review",
    registered_at: "Today, 08:45 AM",
    chief_complaint: "Acute crushing retrosternal chest pain radiating to left arm",
  },
  {
    id: "REC-PT-003",
    synthetic_token: "PT-SYN-0319",
    name: "Sunita Rao",
    age_bracket: "35-50 YRS",
    sex: "FEMALE",
    phone: "+91 91234 56789",
    pathway: "OPD_GENERAL",
    consent: true,
    status: "Triage Pending",
    registered_at: "Today, 09:10 AM",
    chief_complaint: "High febrile illness with body chills and persistent headache",
  },
  {
    id: "REC-PT-004",
    synthetic_token: "CLN-10482",
    name: "Ada Okafor",
    age_bracket: "35-50 YRS",
    sex: "FEMALE",
    phone: "+234 803 555 0142",
    pathway: "OPD_GENERAL",
    consent: true,
    status: "Registered",
    registered_at: "Today, 09:25 AM",
    chief_complaint: "Routine chronic care review and prescription renewal",
  },
];

export default function ReceptionWorkstationPage() {
  const [records, setRecords] = useState<SyntheticPatientRecord[]>(INITIAL_RECORDS);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [activeTab, setActiveTab] = useState<"directory" | "register">("directory");

  // Registration Form State
  const [fullName, setFullName] = useState("");
  const [ageBracket, setAgeBracket] = useState("25-35 YRS");
  const [biologicalSex, setBiologicalSex] = useState<"FEMALE" | "MALE" | "OTHER">("FEMALE");
  const [phone, setPhone] = useState("");
  const [emergencyContact, setEmergencyContact] = useState("");
  const [assignedPathway, setAssignedPathway] = useState<"OPD_GENERAL" | "EMERGENCY">("OPD_GENERAL");
  const [consentGranted, setConsentGranted] = useState(true);
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [language, setLanguage] = useState<"en" | "hi" | "or">("en");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registeredSuccess, setRegisteredSuccess] = useState<{
    token: string;
    name: string;
    pathway: string;
    caseId?: string;
  } | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Sync real queue if available
  useEffect(() => {
    let mounted = true;
    async function loadQueue() {
      try {
        const queueRes: QueueResponse = await getClinicalQueue();
        const queue: QueueItem[] = queueRes?.queue || [];
        if (mounted && queue && queue.length > 0) {
          // Merge real cases into record directory
          const mapped: SyntheticPatientRecord[] = queue.map((qc, idx) => ({
            id: `QUEUE-${qc.case_id || idx}`,
            synthetic_token: qc.patient_synthetic_id || `PT-SYN-${1000 + idx}`,
            name: qc.patient_synthetic_id ? `Patient (${qc.patient_synthetic_id})` : "Walk-in Patient",
            age_bracket: qc.age_bracket || "Adult",
            sex: (qc.biological_sex as "FEMALE" | "MALE") || "FEMALE",
            phone: "+91 •••• •••••",
            pathway: qc.emergency_active ? "EMERGENCY" : "OPD_GENERAL",
            consent: true,
            status: qc.status === "NEW" ? "Registered" : qc.status === "CLINICIAN_REVIEW_REQUIRED" ? "In Review" : "Triage Pending",
            registered_at: qc.created_at ? new Date(qc.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Today",
            chief_complaint: qc.presenting_complaint || "Clinical intake registered",
          }));
          setRecords((prev) => {
            const existingTokens = new Set(prev.map((r) => r.synthetic_token));
            const newOnes = mapped.filter((m) => !existingTokens.has(m.synthetic_token));
            return [...prev, ...newOnes];
          });
        }
      } catch {
        // Fall back gracefully to synthetic demo records
      }
    }
    loadQueue();
    return () => {
      mounted = false;
    };
  }, []);

  const handleRegisterPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!consentGranted) {
      setErrorMessage("Patient informed consent must be recorded before registering clinical intake.");
      return;
    }
    if (!chiefComplaint.trim()) {
      setErrorMessage("Please enter the presenting chief complaint.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const generatedToken = `PT-SYN-${Math.floor(1000 + Math.random() * 9000)}`;

    try {
      const res = await submitPatientIntake({
        facility_id: "FAC-DH-04",
        pathway: assignedPathway,
        reported_age_bracket: ageBracket,
        biological_sex: biologicalSex,
        preferred_language: language,
        chief_complaint: chiefComplaint,
        symptom_duration: "Current presentation",
        narrative_notes: `Reception Registration: ${fullName || "Anonymous"}. Emergency Contact: ${emergencyContact || "None on file"}. Registered at reception desk.`,
        voice_transcript: "",
        document_uploaded: false,
        document_type: "",
        consent_confirmed: consentGranted,
      });

      const newRecord: SyntheticPatientRecord = {
        id: `REC-${Date.now()}`,
        synthetic_token: res.synthetic_reference || generatedToken,
        name: fullName || "Anonymous Patient",
        age_bracket: ageBracket,
        sex: biologicalSex,
        phone: phone || "Not provided",
        pathway: assignedPathway,
        consent: consentGranted,
        status: assignedPathway === "EMERGENCY" ? "Triage Pending" : "Registered",
        registered_at: "Just now",
        chief_complaint: chiefComplaint,
      };

      setRecords((prev) => [newRecord, ...prev]);
      setRegisteredSuccess({
        token: res.synthetic_reference || generatedToken,
        name: fullName || "Patient",
        pathway: assignedPathway === "EMERGENCY" ? "Emergency Fast-Track" : "Regular Outpatient (OPD)",
        caseId: res.case_id,
      });

      // Reset form
      setFullName("");
      setPhone("");
      setEmergencyContact("");
      setChiefComplaint("");
      setActiveTab("directory");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed";
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredRecords = records.filter((r) => {
    const matchesSearch =
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.synthetic_token.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.chief_complaint.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" ||
      (statusFilter === "EMERGENCY" && r.pathway === "EMERGENCY") ||
      (statusFilter === "REGULAR" && r.pathway === "OPD_GENERAL") ||
      r.status.toUpperCase() === statusFilter.toUpperCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <RoleGuard
      allowedRoles={["RECEPTIONIST", "NURSE", "CLINICIAN", "DOCTOR", "FACILITY_ADMIN", "SYSTEM_ADMIN"]}
      title="Medical Reception Workstation Restricted"
      message="This interface is designated for hospital receptionists and authorized intake staff to register patients, record consent, and assign initial care pathways."
    >
      <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
        <PageHeader
          title="Medical Reception & Intake Desk"
          subtitle="Patient registration, digital consent recording, and staff-directed clinical pathway assignment"
          breadcrumbs={[{ label: "Home", href: "/" }, { label: "Staff", href: "/staff" }, { label: "Reception" }]}
        />

        {/* Governance & Role Boundary Alert */}
        <div
          className="alert alert-info"
          style={{ display: "flex", alignItems: "flex-start", gap: 12 }}
        >
          <ShieldCheck style={{ width: 18, height: 18, color: "var(--info)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
          <div style={{ fontSize: "0.8125rem", lineHeight: 1.5 }}>
            <strong>Staff-Led Reception Authority Model:</strong> Reception staff verify patient demographics, record DPDP Act 2023 consent, and assign the intake pathway.
            Receptionists <em>never</em> formulate medical diagnoses or override clinical evaluations. Emergency presentations must be flagged immediately for triage bay diversion.
          </div>
        </div>

        {/* Success Banner */}
        {registeredSuccess && (
          <div
            className="alert alert-success"
            style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <CheckCircle2 style={{ width: 20, height: 20, color: "var(--success)" }} aria-hidden="true" />
              <div>
                <strong style={{ fontSize: "0.875rem" }}>
                  Patient Registered Successfully: {registeredSuccess.name}
                </strong>
                <span style={{ fontSize: "0.8125rem", display: "block" }}>
                  Token ID: <code>{registeredSuccess.token}</code> • Pathway: {registeredSuccess.pathway} • Dispatched to Triage Queue
                </span>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {registeredSuccess.caseId && (
                <DownloadReportButton caseId={registeredSuccess.caseId} label="Download Intake PDF" size="sm" variant="secondary" />
              )}
              <Link href="/staff/triage" className="btn btn-primary btn-sm">
                <span>View in Triage Queue</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
              <button
                type="button"
                onClick={() => setRegisteredSuccess(null)}
                className="btn btn-ghost btn-sm"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Operational Statistics */}
        <div className="grid grid-4 gap-3">
          <div className="metric-card">
            <span className="section-title">Today's Registrations</span>
            <div className="stat-value">{records.length}</div>
            <span className="xs muted">Total recorded walk-ins & transfers</span>
          </div>

          <div className="metric-card">
            <span className="section-title">Emergency Fast-Tracks</span>
            <div className="stat-value" style={{ color: "var(--error)" }}>
              {records.filter((r) => r.pathway === "EMERGENCY").length}
            </div>
            <span className="xs muted">Immediate resuscitation diversion</span>
          </div>

          <div className="metric-card">
            <span className="section-title">Routine OPD Queue</span>
            <div className="stat-value" style={{ color: "var(--teal-700)" }}>
              {records.filter((r) => r.pathway === "OPD_GENERAL").length}
            </div>
            <span className="xs muted">Ambulatory clinic consultations</span>
          </div>

          <div className="metric-card">
            <span className="section-title">Consent Compliance</span>
            <div className="stat-value" style={{ color: "var(--success)" }}>100%</div>
            <span className="xs muted">DPDP Act 2023 certified records</span>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="tabs">
          <button
            type="button"
            className={`tab ${activeTab === "directory" ? "active" : ""}`}
            onClick={() => setActiveTab("directory")}
          >
            <Users style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Patient Registry & Queue</span>
            <span className="count">{filteredRecords.length}</span>
          </button>
          <button
            type="button"
            className={`tab ${activeTab === "register" ? "active" : ""}`}
            onClick={() => setActiveTab("register")}
          >
            <UserPlus style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Register New Patient</span>
          </button>
        </div>

        {/* TAB 1: PATIENT REGISTRY & DIRECTORY */}
        {activeTab === "directory" && (
          <div className="card">
            {/* Filter Bar */}
            <div className="card-header" style={{ flexWrap: "wrap", gap: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1, minWidth: 260 }}>
                <div style={{ position: "relative", width: "100%", maxWidth: 360 }}>
                  <Search
                    style={{
                      position: "absolute",
                      left: 10,
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: 15,
                      height: 15,
                      color: "var(--text-4)",
                    }}
                    aria-hidden="true"
                  />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search patient, token (PT-SYN-*), complaint..."
                    style={{
                      width: "100%",
                      padding: "6px 12px 6px 32px",
                      borderRadius: "var(--r-md)",
                      border: "1px solid var(--border-strong)",
                      fontSize: "var(--fs-sm)",
                      backgroundColor: "var(--surface)",
                      color: "var(--text)",
                    }}
                  />
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Filter style={{ width: 14, height: 14, color: "var(--text-3)" }} aria-hidden="true" />
                <span className="xs muted">Filter:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{
                    padding: "4px 8px",
                    borderRadius: "var(--r-md)",
                    border: "1px solid var(--border-strong)",
                    fontSize: "var(--fs-xs)",
                    backgroundColor: "var(--surface)",
                    color: "var(--text)",
                  }}
                >
                  <option value="ALL">All Pathways & Statuses</option>
                  <option value="EMERGENCY">Emergency Fast-Track Only</option>
                  <option value="REGULAR">Routine OPD Only</option>
                  <option value="Registered">Status: Registered</option>
                  <option value="Triage Pending">Status: Triage Pending</option>
                  <option value="In Review">Status: In Review</option>
                </select>

                <button
                  type="button"
                  onClick={() => setActiveTab("register")}
                  className="btn btn-accent btn-sm"
                >
                  <UserPlus style={{ width: 14, height: 14 }} aria-hidden="true" />
                  <span>Register Patient</span>
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Token / Patient</th>
                    <th>Demographics</th>
                    <th>Assigned Pathway</th>
                    <th>Presenting Complaint</th>
                    <th>Consent</th>
                    <th>Status</th>
                    <th style={{ textAlign: "right" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: "center", padding: "32px 16px", color: "var(--text-3)" }}>
                        No patient records found matching your filter criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredRecords.map((r) => (
                      <tr key={r.id}>
                        <td>
                          <div style={{ display: "flex", flexDirection: "column" }}>
                            <strong style={{ fontSize: "var(--fs-sm)" }}>{r.name}</strong>
                            <code className="mono xs muted">{r.synthetic_token}</code>
                          </div>
                        </td>
                        <td>
                          <span className="xs muted">
                            {r.age_bracket} • {r.sex}
                          </span>
                        </td>
                        <td>
                          {r.pathway === "EMERGENCY" ? (
                            <span className="badge badge-error">
                              <AlertTriangle style={{ width: 11, height: 11 }} aria-hidden="true" />
                              <span>Emergency Fast-Track</span>
                            </span>
                          ) : (
                            <span className="badge badge-teal">
                              <Activity style={{ width: 11, height: 11 }} aria-hidden="true" />
                              <span>Regular Outpatient</span>
                            </span>
                          )}
                        </td>
                        <td style={{ maxWidth: 280 }}>
                          <span
                            className="small subtle"
                            style={{
                              display: "-webkit-box",
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                            }}
                          >
                            {r.chief_complaint}
                          </span>
                        </td>
                        <td>
                          {r.consent ? (
                            <span className="badge badge-success" title="Informed digital consent recorded">
                              <Check style={{ width: 11, height: 11 }} aria-hidden="true" />
                              <span>Recorded</span>
                            </span>
                          ) : (
                            <span className="badge badge-warning">Pending</span>
                          )}
                        </td>
                        <td>
                          <span
                            className={`badge ${
                              r.status === "In Review"
                                ? "badge-navy"
                                : r.status === "Triage Pending"
                                ? "badge-warning"
                                : "badge-outline"
                            }`}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td style={{ textAlign: "right" }}>
                          <div style={{ display: "inline-flex", gap: 6 }}>
                            <Link
                              href={`/patient/case/${r.synthetic_token}`}
                              className="btn btn-secondary btn-sm"
                              title="View patient case token status"
                            >
                              <span>Track Status</span>
                            </Link>
                            <Link
                              href="/staff/triage"
                              className="btn btn-ghost btn-sm"
                              title="Open in Nurse Triage Queue"
                            >
                              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="card-footer">
              <span className="xs muted">
                Showing {filteredRecords.length} of {records.length} patient encounters at Cuttack DHH.
              </span>
              <span className="xs muted">
                Reception Authority: Read / Register / Pathway Assignment
              </span>
            </div>
          </div>
        )}

        {/* TAB 2: REGISTER NEW PATIENT */}
        {activeTab === "register" && (
          <div className="card" style={{ maxWidth: 840, margin: "0 auto", width: "100%" }}>
            <div className="card-header">
              <div>
                <h3 style={{ fontSize: "var(--fs-lg)" }}>Patient Intake Registration</h3>
                <p className="xs muted" style={{ marginTop: 2 }}>
                  Record demographics, informed consent, and assign the clinical intake pathway.
                </p>
              </div>
              <span className="badge badge-teal">Staff-Led Intake</span>
            </div>

            <form onSubmit={handleRegisterPatient}>
              <div className="card-body stack gap-4">
                {errorMessage && (
                  <div className="alert alert-error">
                    <AlertTriangle style={{ width: 16, height: 16 }} aria-hidden="true" />
                    <span>{errorMessage}</span>
                  </div>
                )}

                {/* Patient Demographics */}
                <div>
                  <h4 className="section-title" style={{ marginBottom: 12 }}>
                    1. Patient Identity & Demographics
                  </h4>
                  <div className="grid grid-2 gap-3">
                    <div className="field">
                      <label className="label">
                        Patient Full Name <span className="req">*</span>
                      </label>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="e.g. Ramesh Chandra Das"
                        required
                        className="input"
                      />
                    </div>

                    <div className="field">
                      <label className="label">
                        Phone Number <span className="opt">(Optional for SMS follow-ups)</span>
                      </label>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+91 98765 43210"
                        className="input"
                      />
                    </div>

                    <div className="field">
                      <label className="label">
                        Age Bracket <span className="req">*</span>
                      </label>
                      <select
                        value={ageBracket}
                        onChange={(e) => setAgeBracket(e.target.value)}
                        className="select"
                      >
                        <option value="0-5 YRS">Pediatric (0–5 Yrs)</option>
                        <option value="6-17 YRS">Adolescent (6–17 Yrs)</option>
                        <option value="18-25 YRS">Young Adult (18–25 Yrs)</option>
                        <option value="25-35 YRS">Adult (25–35 Yrs)</option>
                        <option value="35-50 YRS">Adult (35–50 Yrs)</option>
                        <option value="50-65 YRS">Older Adult (50–65 Yrs)</option>
                        <option value="65+ YRS">Geriatric (65+ Yrs)</option>
                      </select>
                    </div>

                    <div className="field">
                      <label className="label">
                        Biological Sex <span className="req">*</span>
                      </label>
                      <select
                        value={biologicalSex}
                        onChange={(e) => setBiologicalSex(e.target.value as "FEMALE" | "MALE" | "OTHER")}
                        className="select"
                      >
                        <option value="FEMALE">Female</option>
                        <option value="MALE">Male</option>
                        <option value="OTHER">Other / Undisclosed</option>
                      </select>
                    </div>

                    <div className="field" style={{ gridColumn: "1 / -1" }}>
                      <label className="label">Emergency Contact Name & Phone</label>
                      <input
                        type="text"
                        value={emergencyContact}
                        onChange={(e) => setEmergencyContact(e.target.value)}
                        placeholder="e.g. Manas Das (Brother) — +91 94321 88888"
                        className="input"
                      />
                    </div>
                  </div>
                </div>

                <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "4px 0" }} />

                {/* Staff-Led Pathway Assignment */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
                    <h4 className="section-title">2. Staff-Assigned Clinical Intake Pathway</h4>
                    <span className="xs subtle" style={{ fontStyle: "italic" }}>
                      Mandatory staff determination (not patient chosen)
                    </span>
                  </div>

                  <div className="grid grid-2 gap-3">
                    <label
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 12,
                        padding: 14,
                        borderRadius: "var(--r-md)",
                        border: assignedPathway === "OPD_GENERAL" ? "2px solid var(--teal-600)" : "1px solid var(--border-strong)",
                        backgroundColor: assignedPathway === "OPD_GENERAL" ? "var(--teal-50)" : "var(--surface)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="radio"
                        name="pathway"
                        value="OPD_GENERAL"
                        checked={assignedPathway === "OPD_GENERAL"}
                        onChange={() => setAssignedPathway("OPD_GENERAL")}
                        style={{ marginTop: 2 }}
                      />
                      <div>
                        <strong style={{ fontSize: "var(--fs-sm)", display: "block", color: "var(--text)" }}>
                          Regular Outpatient Pathway (OPD)
                        </strong>
                        <p className="xs muted" style={{ marginTop: 4 }}>
                          Standard ambulatory queue for non-acute symptoms, general consultations, follow-ups, and chronic condition reviews.
                        </p>
                      </div>
                    </label>

                    <label
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 12,
                        padding: 14,
                        borderRadius: "var(--r-md)",
                        border: assignedPathway === "EMERGENCY" ? "2px solid var(--error)" : "1px solid var(--border-strong)",
                        backgroundColor: assignedPathway === "EMERGENCY" ? "var(--error-bg)" : "var(--surface)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="radio"
                        name="pathway"
                        value="EMERGENCY"
                        checked={assignedPathway === "EMERGENCY"}
                        onChange={() => setAssignedPathway("EMERGENCY")}
                        style={{ marginTop: 2 }}
                      />
                      <div>
                        <strong style={{ fontSize: "var(--fs-sm)", display: "block", color: "var(--error)" }}>
                          Emergency Fast-Track Diversion
                        </strong>
                        <p className="xs muted" style={{ marginTop: 4 }}>
                          Paschim Banga Doctrine fast-track. Crushing chest pain, severe dyspnea, shock, altered consciousness, acute trauma.
                        </p>
                      </div>
                    </label>
                  </div>
                </div>

                <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "4px 0" }} />

                {/* Presenting Chief Complaint */}
                <div>
                  <h4 className="section-title" style={{ marginBottom: 10 }}>
                    3. Presenting Chief Complaint
                  </h4>
                  <div className="field">
                    <label className="label">
                      What is the patient experiencing today? <span className="req">*</span>
                    </label>
                    <textarea
                      value={chiefComplaint}
                      onChange={(e) => setChiefComplaint(e.target.value)}
                      placeholder="e.g. Severe episodic headache for 2 days with light sensitivity and vomiting..."
                      rows={3}
                      required
                      className="textarea"
                    />
                  </div>

                  <div style={{ display: "flex", gap: 12, marginTop: 8, alignItems: "center" }}>
                    <span className="xs muted">Preferred Language for Consultation:</span>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value as "en" | "hi" | "or")}
                      style={{
                        padding: "3px 8px",
                        fontSize: "var(--fs-xs)",
                        borderRadius: "var(--r-sm)",
                        border: "1px solid var(--border)",
                      }}
                    >
                      <option value="en">English</option>
                      <option value="or">Odia (ଓଡ଼ିଆ)</option>
                      <option value="hi">Hindi (हिन्दी)</option>
                    </select>
                  </div>
                </div>

                <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "4px 0" }} />

                {/* DPDP Act 2023 Consent Recording */}
                <div
                  style={{
                    backgroundColor: "var(--surface-sunken)",
                    borderRadius: "var(--r-md)",
                    padding: 12,
                    border: "1px solid var(--border)",
                  }}
                >
                  <label style={{ display: "flex", alignItems: "flex-start", gap: 10, cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={consentGranted}
                      onChange={(e) => setConsentGranted(e.target.checked)}
                      style={{ marginTop: 3 }}
                    />
                    <div style={{ fontSize: "var(--fs-xs)", lineHeight: 1.5 }}>
                      <strong style={{ display: "block", color: "var(--text)" }}>
                        Mandatory Digital Consent Recorded (DPDP Act 2023 & NMC RMP Regulations 2023)
                      </strong>
                      <span className="muted">
                        Patient (or legal guardian) has consented to clinical data collection for triage, physician review, and emergency hospital care. Zero third-party commercial marketing.
                      </span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="card-footer">
                <button
                  type="button"
                  onClick={() => setActiveTab("directory")}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !consentGranted}
                  className="btn btn-primary"
                  style={{ minWidth: 160 }}
                >
                  {isSubmitting ? "Registering..." : "Complete Registration"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </RoleGuard>
  );
}
