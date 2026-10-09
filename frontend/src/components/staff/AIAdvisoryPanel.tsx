"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  RefreshCw,
  AlertTriangle,
  FileText,
  Clock,
  HelpCircle,
  FileEdit,
  Shield,
  Layers,
  Info,
} from "lucide-react";
import { AIResultRecord, AITaskId } from "@/types";
import {
  getCaseAIResults,
  generateCaseAISummary,
  generateCaseAITimeline,
  analyzeCaseAIMissingInfo,
  draftCaseAIFollowUpQuestions,
  draftCaseAITriageNote,
} from "@/lib/api";
import { Button } from "@/components/ui/Button";

interface AIAdvisoryPanelProps {
  caseId: string;
  initialResults?: AIResultRecord[];
  onNoteDrafted?: () => void;
}

export const AIAdvisoryPanel: React.FC<AIAdvisoryPanelProps> = ({
  caseId,
  initialResults = [],
  onNoteDrafted,
}) => {
  const [results, setResults] = useState<AIResultRecord[]>(initialResults);
  const [activeTab, setActiveTab] = useState<AITaskId>("CASE_SUMMARY_V1");
  const [loadingTask, setLoadingTask] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync initial results from parent or fetch fresh
  useEffect(() => {
    if (initialResults && initialResults.length > 0) {
      setResults(initialResults);
    } else {
      let isMounted = true;
      getCaseAIResults(caseId)
        .then((res) => {
          if (isMounted && Array.isArray(res)) {
            setResults(res);
          }
        })
        .catch((err) => {
          console.warn("Unable to fetch AI results:", err);
        });
      return () => {
        isMounted = false;
      };
    }
  }, [caseId, initialResults]);

  const getResultForTask = (taskId: string): AIResultRecord | undefined => {
    return results.find((r) => r.task_id === taskId);
  };

  const handleRunTask = async (taskId: AITaskId, force: boolean = false) => {
    setLoadingTask(taskId);
    setErrorMsg(null);
    try {
      let record: AIResultRecord;
      switch (taskId) {
        case "CASE_SUMMARY_V1":
          record = await generateCaseAISummary(caseId, force);
          break;
        case "TIMELINE_SUMMARY_V1":
          record = await generateCaseAITimeline(caseId, force);
          break;
        case "MISSING_INFORMATION_V1":
          record = await analyzeCaseAIMissingInfo(caseId, force);
          break;
        case "FOLLOWUP_QUESTION_V1":
          record = await draftCaseAIFollowUpQuestions(caseId, force);
          break;
        case "TRIAGE_NOTE_DRAFT_V1":
          record = await draftCaseAITriageNote(caseId, force);
          if (onNoteDrafted) onNoteDrafted();
          break;
        default:
          throw new Error(`Unsupported task: ${taskId}`);
      }

      // Update state with new or updated record
      setResults((prev) => {
        const filtered = prev.filter((r) => r.task_id !== record.task_id);
        return [record, ...filtered];
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "AI task generation failed";
      setErrorMsg(msg);
    } finally {
      setLoadingTask(null);
    }
  };

  const activeResult = getResultForTask(activeTab);

  const taskTabs: Array<{ id: AITaskId; label: string; icon: React.ReactNode }> = [
    { id: "CASE_SUMMARY_V1", label: "Summary", icon: <FileText style={{ width: 14, height: 14 }} /> },
    { id: "TIMELINE_SUMMARY_V1", label: "Timeline", icon: <Clock style={{ width: 14, height: 14 }} /> },
    { id: "MISSING_INFORMATION_V1", label: "Gaps", icon: <AlertTriangle style={{ width: 14, height: 14 }} /> },
    { id: "FOLLOWUP_QUESTION_V1", label: "Inquiries", icon: <HelpCircle style={{ width: 14, height: 14 }} /> },
    { id: "TRIAGE_NOTE_DRAFT_V1", label: "Draft Note", icon: <FileEdit style={{ width: 14, height: 14 }} /> },
  ];

  return (
    <div
      className="clinova-card"
      style={{
        borderLeft: "4px solid #8b5cf6",
        display: "flex",
        flexDirection: "column",
        gap: 12,
        padding: 14,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Sparkles style={{ width: 16, height: 16, color: "#8b5cf6" }} aria-hidden="true" />
          <span className="clinova-label" style={{ color: "#7c3aed", fontWeight: 700 }}>
            AI ADVISORY SUPPORT (LOCAL LLM)
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            className="clinova-badge"
            style={{
              backgroundColor: "#ede9fe",
              color: "#6d28d9",
              borderColor: "#ddd6fe",
              fontSize: "0.6875rem",
              fontWeight: 700,
            }}
          >
            ADVISORY ONLY
          </span>
          <span
            className="clinova-badge"
            style={{
              backgroundColor: "var(--clinova-surface-subtle)",
              color: "var(--clinova-text-muted)",
              fontSize: "0.6875rem",
            }}
          >
            $0 Local Qwen
          </span>
        </div>
      </div>

      {/* Task Tabs */}
      <div
        style={{
          display: "flex",
          gap: 4,
          background: "var(--clinova-surface-subtle)",
          padding: 3,
          borderRadius: "var(--clinova-radius-md)",
          border: "1px solid var(--clinova-border)",
          overflowX: "auto",
        }}
      >
        {taskTabs.map((t) => {
          const isSelected = activeTab === t.id;
          const hasRecord = !!getResultForTask(t.id);
          const isStale = getResultForTask(t.id)?.is_stale;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 5,
                padding: "6px 8px",
                fontSize: "0.75rem",
                fontWeight: isSelected ? 700 : 500,
                color: isSelected ? "#6d28d9" : "var(--clinova-text-secondary)",
                backgroundColor: isSelected ? "#ffffff" : "transparent",
                border: "none",
                borderRadius: 4,
                boxShadow: isSelected ? "0 1px 2px rgba(0,0,0,0.06)" : "none",
                cursor: "pointer",
                whiteSpace: "nowrap",
                position: "relative",
              }}
            >
              {t.icon}
              <span>{t.label}</span>
              {hasRecord && (
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    backgroundColor: isStale ? "#f59e0b" : "#10b981",
                  }}
                  title={isStale ? "Result Stale (Evidence Updated)" : "Fresh Result Available"}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Error Feedback */}
      {errorMsg && (
        <div
          style={{
            padding: "8px 10px",
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 6,
            fontSize: "0.75rem",
            color: "#991b1b",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <AlertTriangle style={{ width: 14, height: 14, flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Active Task Body */}
      {activeResult ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {/* Metadata & Freshness Bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: "0.6875rem",
              color: "var(--clinova-text-muted)",
              borderBottom: "1px solid var(--clinova-border)",
              paddingBottom: 6,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              {activeResult.is_stale ? (
                <span
                  className="clinova-badge"
                  style={{ backgroundColor: "#fef3c7", color: "#b45309", borderColor: "#fde68a" }}
                >
                  STALE (EVIDENCE UPDATED)
                </span>
              ) : (
                <span
                  className="clinova-badge"
                  style={{ backgroundColor: "#ecfdf5", color: "#047857", borderColor: "#a7f3d0" }}
                >
                  FRESH
                </span>
              )}
              {activeResult.is_cached && (
                <span className="clinova-badge" style={{ backgroundColor: "#eff6ff", color: "#1d4ed8", borderColor: "#bfdbfe" }}>
                  CACHED
                </span>
              )}
              <span>Model: {activeResult.model_id}</span>
            </div>

            <Button
              size="sm"
              variant="outline"
              onClick={() => handleRunTask(activeTab, true)}
              disabled={loadingTask === activeTab}
              style={{ fontSize: "0.6875rem", padding: "2px 8px", height: 24 }}
            >
              <RefreshCw
                style={{
                  width: 11,
                  height: 11,
                  animation: loadingTask === activeTab ? "spin 1s linear infinite" : "none",
                }}
              />
              <span>Regenerate</span>
            </Button>
          </div>

          {/* Fallback / Offline Notice */}
          {activeResult.status === "FALLBACK" && (
            <div
              style={{
                padding: "8px 10px",
                backgroundColor: "#fffbeb",
                border: "1px solid #fde68a",
                borderRadius: 6,
                fontSize: "0.75rem",
                color: "#92400e",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <Info style={{ width: 14, height: 14, flexShrink: 0 }} />
              <span>
                <strong>Safe Degradation:</strong> Local AI runtime offline. Clinical review is unaffected.
              </span>
            </div>
          )}

          {/* Task-Specific Renderings */}
          {activeTab === "CASE_SUMMARY_V1" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div
                style={{
                  backgroundColor: "var(--clinova-surface-subtle)",
                  padding: 10,
                  borderRadius: 6,
                  border: "1px solid var(--clinova-border)",
                  fontSize: "0.8125rem",
                  lineHeight: 1.5,
                  color: "var(--clinova-text-primary)",
                }}
              >
                {String(activeResult.payload?.clinical_summary || "No clinical summary available.")}
              </div>

              {Array.isArray(activeResult.payload?.key_findings) && (
                <div>
                  <span className="clinova-metadata" style={{ fontWeight: 600, display: "block", marginBottom: 4 }}>
                    KEY SYNTHESIZED FINDINGS:
                  </span>
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
                    {(activeResult.payload.key_findings as string[]).map((kf, i) => (
                      <li key={i}>{kf}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {activeTab === "TIMELINE_SUMMARY_V1" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div
                style={{
                  backgroundColor: "var(--clinova-surface-subtle)",
                  padding: 10,
                  borderRadius: 6,
                  border: "1px solid var(--clinova-border)",
                  fontSize: "0.8125rem",
                  lineHeight: 1.5,
                }}
              >
                {String(activeResult.payload?.chronological_narrative || "No chronological narrative available.")}
              </div>

              {Array.isArray(activeResult.payload?.milestones) && (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <span className="clinova-metadata" style={{ fontWeight: 600 }}>CHRONOLOGICAL MILESTONES:</span>
                  {(activeResult.payload.milestones as Array<{ timestamp?: string; event: string }>).map((ms, mi) => (
                    <div
                      key={mi}
                      style={{
                        padding: "6px 8px",
                        background: "var(--clinova-surface)",
                        borderRadius: 4,
                        border: "1px solid var(--clinova-border)",
                        fontSize: "0.75rem",
                      }}
                    >
                      <strong style={{ color: "var(--clinova-text-primary)" }}>{ms.event}</strong>
                    </div>
                  ))}
                </div>
              )}

              {Boolean(activeResult.payload?.progression_assessment) && (
                <div style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)", fontStyle: "italic" }}>
                  <strong>Progression:</strong> {String(activeResult.payload.progression_assessment)}
                </div>
              )}
            </div>
          )}

          {activeTab === "MISSING_INFORMATION_V1" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {Array.isArray(activeResult.payload?.missing_parameters) && (
                (activeResult.payload.missing_parameters as Array<{
                  parameter_name: string;
                  clinical_rationale: string;
                  impact_level: string;
                  suggested_inquiry?: string;
                }>).map((gap, gi) => (
                  <div
                    key={gi}
                    style={{
                      padding: "8px 10px",
                      borderRadius: 6,
                      border: "1px solid var(--clinova-border)",
                      backgroundColor: "var(--clinova-surface-subtle)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <strong style={{ fontSize: "0.8125rem" }}>{gap.parameter_name}</strong>
                      <span
                        className="clinova-badge"
                        style={{
                          backgroundColor: gap.impact_level === "HIGH" ? "#fef2f2" : "#fef3c7",
                          color: gap.impact_level === "HIGH" ? "#991b1b" : "#92400e",
                          fontSize: "0.625rem",
                        }}
                      >
                        {gap.impact_level} IMPACT
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
                      {gap.clinical_rationale}
                    </p>
                    {gap.suggested_inquiry && (
                      <span style={{ fontSize: "0.6875rem", color: "#7c3aed", fontWeight: 600 }}>
                        Inquiry: {gap.suggested_inquiry}
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "FOLLOWUP_QUESTION_V1" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {Array.isArray(activeResult.payload?.questions) && (
                (activeResult.payload.questions as Array<{
                  question_text: string;
                  clinical_target: string;
                  priority: string;
                }>).map((q, qi) => (
                  <div
                    key={qi}
                    style={{
                      padding: "8px 10px",
                      borderRadius: 6,
                      border: "1px solid var(--clinova-border)",
                      backgroundColor: "var(--clinova-surface)",
                      fontSize: "0.75rem",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <strong style={{ color: "#7c3aed" }}>{q.question_text}</strong>
                      <span className="clinova-badge" style={{ fontSize: "0.625rem" }}>{q.priority}</span>
                    </div>
                    <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                      Target: {q.clinical_target}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "TRIAGE_NOTE_DRAFT_V1" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div
                style={{
                  backgroundColor: "var(--clinova-surface-subtle)",
                  padding: 10,
                  borderRadius: 6,
                  border: "1px solid var(--clinova-border)",
                  fontSize: "0.75rem",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                <div>
                  <strong style={{ color: "var(--clinova-text-primary)" }}>Subjective: </strong>
                  <span>{String(activeResult.payload?.subjective_summary || "")}</span>
                </div>
                <div>
                  <strong style={{ color: "var(--clinova-text-primary)" }}>Objective: </strong>
                  <span>{String(activeResult.payload?.objective_summary || "")}</span>
                </div>
                <div>
                  <strong style={{ color: "var(--clinova-text-primary)" }}>Assessment: </strong>
                  <span>{String(activeResult.payload?.assessment_synthesis || "")}</span>
                </div>
              </div>

              {Array.isArray(activeResult.payload?.suggested_next_steps) && (
                <div>
                  <span className="clinova-metadata" style={{ fontWeight: 600 }}>SUGGESTED NEXT STEPS (ADVISORY):</span>
                  <ul style={{ margin: "4px 0 0", paddingLeft: 16, fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
                    {(activeResult.payload.suggested_next_steps as string[]).map((step, si) => (
                      <li key={si}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Evidence Grounding Badges */}
          {activeResult.source_evidence_references && activeResult.source_evidence_references.length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
              <span className="clinova-metadata" style={{ fontSize: "0.6875rem" }}>
                Grounding Evidence:
              </span>
              {activeResult.source_evidence_references.map((evId, idx) => (
                <span
                  key={idx}
                  className="clinova-badge"
                  style={{
                    backgroundColor: "var(--clinova-surface-subtle)",
                    borderColor: "var(--clinova-border)",
                    fontSize: "0.625rem",
                  }}
                >
                  {evId}
                </span>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div
          style={{
            padding: "20px 14px",
            textAlign: "center",
            backgroundColor: "var(--clinova-surface-subtle)",
            borderRadius: "var(--clinova-radius-md)",
            border: "1px dashed var(--clinova-border)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
          }}
        >
          <Layers style={{ width: 24, height: 24, color: "var(--clinova-text-muted)" }} />
          <div>
            <strong style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)", display: "block" }}>
              No {taskTabs.find((t) => t.id === activeTab)?.label} Generated Yet
            </strong>
            <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
              Run local advisory inference grounded in verified case data.
            </span>
          </div>
          <Button
            size="sm"
            variant="primary"
            onClick={() => handleRunTask(activeTab)}
            disabled={loadingTask === activeTab}
            style={{ marginTop: 4, backgroundColor: "#7c3aed", borderColor: "#6d28d9" }}
          >
            <Sparkles style={{ width: 12, height: 12 }} />
            <span>{loadingTask === activeTab ? "Synthesizing..." : `Generate ${taskTabs.find((t) => t.id === activeTab)?.label}`}</span>
          </Button>
        </div>
      )}

      {/* Mandatory Regulatory / Medicolegal Notice */}
      <div
        style={{
          borderTop: "1px solid var(--clinova-border)",
          paddingTop: 8,
          display: "flex",
          alignItems: "flex-start",
          gap: 6,
          fontSize: "0.6875rem",
          color: "var(--clinova-text-muted)",
        }}
      >
        <Shield style={{ width: 12, height: 12, flexShrink: 0, marginTop: 1, color: "#8b5cf6" }} aria-hidden="true" />
        <span>
          <strong>Advisory Notice:</strong> Clinical AI advisory result. Non-diagnostic and non-binding. Qualified registered clinician holds sole authority and responsibility for all clinical decisions.
        </span>
      </div>
    </div>
  );
};
