"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Globe,
  Languages,
  CheckCircle2,
  AlertTriangle,
  Edit3,
  ShieldAlert,
  Save,
  X,
} from "lucide-react";
import { TranslationRecordItem } from "@/types";
import {
  getCaseTranslations,
  requestCaseTranslation,
  verifyCaseTranslation,
  correctCaseTranslation,
} from "@/lib/api";
import { Button } from "@/components/ui/Button";

interface MultilingualTranslationPanelProps {
  caseId: string;
  sourceComplaint?: string;
  sourceLanguage?: string;
}

export const MultilingualTranslationPanel: React.FC<MultilingualTranslationPanelProps> = ({
  caseId,
  sourceComplaint = "",
  sourceLanguage = "en",
}) => {
  const [translations, setTranslations] = useState<TranslationRecordItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"SIDE_BY_SIDE" | "ORIGINAL" | "TRANSLATION">("SIDE_BY_SIDE");
  
  // Correction state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState<string>("");
  const [isSavingCorrection, setIsSavingCorrection] = useState(false);

  // New translation state
  const [newText, setNewText] = useState(sourceComplaint);
  const [sourceLang, setSourceLang] = useState(sourceLanguage || "hi");
  const [targetLang, setTargetLang] = useState("en");
  const [isTranslating, setIsTranslating] = useState(false);

  const fetchTranslations = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getCaseTranslations(caseId);
      if (Array.isArray(data)) {
        setTranslations(data as unknown as TranslationRecordItem[]);
      }
    } catch (err: unknown) {
      console.warn("Could not fetch case translations:", err);
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchTranslations();
  }, [fetchTranslations]);

  const handleRequestTranslation = async () => {
    if (!newText.trim()) return;
    setIsTranslating(true);
    setErrorMsg(null);
    try {
      await requestCaseTranslation(caseId, {
        text: newText,
        source_lang: sourceLang,
        target_lang: targetLang,
        entity_type: "Case",
        entity_id: caseId,
      });
      await fetchTranslations();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Translation request failed.";
      setErrorMsg(msg);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleVerify = async (transId: string) => {
    try {
      await verifyCaseTranslation(caseId, transId, true);
      await fetchTranslations();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to verify translation.";
      setErrorMsg(msg);
    }
  };

  const handleStartEdit = (item: TranslationRecordItem) => {
    setEditingId(item.id);
    setEditText(item.translated_text);
  };

  const handleSaveCorrection = async (transId: string) => {
    if (!editText.trim()) return;
    setIsSavingCorrection(true);
    try {
      await correctCaseTranslation(caseId, transId, editText);
      setEditingId(null);
      await fetchTranslations();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save corrected translation.";
      setErrorMsg(msg);
    } finally {
      setIsSavingCorrection(false);
    }
  };

  const languageLabels: Record<string, string> = {
    en: "English",
    hi: "Hindi (हिन्दी)",
    or: "Odia (ଓଡ଼ିଆ)",
  };

  return (
    <div
      className="clinova-card"
      style={{
        border: "1px solid var(--clinova-border)",
        borderRadius: "var(--clinova-radius-lg)",
        padding: "var(--clinova-space-4)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-3)",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Languages style={{ width: 18, height: 18, color: "var(--clinova-accent)" }} aria-hidden="true" />
          <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, margin: 0 }}>
            Multilingual Translation & Source Provenance
          </h3>
          {isLoading && (
            <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
              Loading...
            </span>
          )}
        </div>

        {/* View Mode Controls */}
        <div style={{ display: "flex", gap: 4, backgroundColor: "var(--clinova-surface-subtle)", padding: 2, borderRadius: 6 }}>
          {(["SIDE_BY_SIDE", "ORIGINAL", "TRANSLATION"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              style={{
                border: "none",
                background: viewMode === mode ? "var(--clinova-surface)" : "transparent",
                color: viewMode === mode ? "var(--clinova-text-primary)" : "var(--clinova-text-muted)",
                fontSize: "0.75rem",
                fontWeight: 500,
                padding: "3px 8px",
                borderRadius: 4,
                cursor: "pointer",
                boxShadow: viewMode === mode ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
              }}
            >
              {mode === "SIDE_BY_SIDE" ? "Side-by-Side" : mode === "ORIGINAL" ? "Original" : "Translation"}
            </button>
          ))}
        </div>
      </div>

      {/* Safety Notice */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          backgroundColor: "var(--clinova-surface-subtle)",
          padding: "6px 10px",
          borderRadius: 6,
          fontSize: "0.75rem",
          color: "var(--clinova-text-secondary)",
        }}
      >
        <ShieldAlert style={{ width: 14, height: 14, color: "var(--clinova-warning-text)" }} aria-hidden="true" />
        <span>
          <strong>Safety Rule:</strong> Original text is the authoritative source. Translation is a derived representation and never substitutes for clinician examination.
        </span>
      </div>

      {errorMsg && (
        <div
          style={{
            backgroundColor: "var(--clinova-danger-light)",
            color: "var(--clinova-danger-text)",
            padding: "8px 12px",
            borderRadius: 6,
            fontSize: "0.8125rem",
          }}
        >
          {errorMsg}
        </div>
      )}

      {/* Translations List */}
      {translations.length === 0 ? (
        <div
          style={{
            padding: 16,
            textAlign: "center",
            backgroundColor: "var(--clinova-surface-subtle)",
            borderRadius: 6,
            fontSize: "0.8125rem",
            color: "var(--clinova-text-muted)",
          }}
        >
          No translations recorded for this case yet. Request translation below.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {translations.map((item) => (
            <div
              key={item.id}
              style={{
                border: "1px solid var(--clinova-border)",
                borderRadius: 8,
                padding: 12,
                backgroundColor: item.review_status === "VERIFIED" ? "var(--clinova-surface)" : "var(--clinova-surface-subtle)",
              }}
            >
              {/* Badges row */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                  <span
                    style={{
                      fontSize: "0.6875rem",
                      fontWeight: 600,
                      padding: "2px 6px",
                      borderRadius: 4,
                      backgroundColor: "var(--clinova-accent-light)",
                      color: "var(--clinova-accent)",
                    }}
                  >
                    {languageLabels[item.source_language] || item.source_language} → {languageLabels[item.target_language] || item.target_language}
                  </span>

                  {item.translation_status === "REQUIRES_REVIEW" && (
                    <span
                      style={{
                        fontSize: "0.6875rem",
                        fontWeight: 600,
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: "var(--clinova-danger-light)",
                        color: "var(--clinova-danger-text)",
                        display: "flex",
                        alignItems: "center",
                        gap: 3,
                      }}
                    >
                      <AlertTriangle style={{ width: 10, height: 10 }} />
                      TRANSLATION REQUIRES REVIEW
                    </span>
                  )}

                  {item.translation_status === "LOW_CONFIDENCE" && (
                    <span
                      style={{
                        fontSize: "0.6875rem",
                        fontWeight: 600,
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: "var(--clinova-warning-light)",
                        color: "var(--clinova-warning-text)",
                      }}
                    >
                      LOW CONFIDENCE
                    </span>
                  )}

                  <span
                    style={{
                      fontSize: "0.6875rem",
                      fontWeight: 600,
                      padding: "2px 6px",
                      borderRadius: 4,
                      backgroundColor:
                        item.review_status === "VERIFIED"
                          ? "var(--clinova-success-light)"
                          : item.review_status === "CORRECTED"
                          ? "var(--clinova-accent-light)"
                          : "var(--clinova-surface)",
                      color:
                        item.review_status === "VERIFIED"
                          ? "var(--clinova-success-text)"
                          : item.review_status === "CORRECTED"
                          ? "var(--clinova-accent)"
                          : "var(--clinova-text-muted)",
                    }}
                  >
                    {item.review_status}
                  </span>
                </div>

                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                  {item.provider} ({item.model_version})
                </span>
              </div>

              {/* Content Comparison Grid */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: viewMode === "SIDE_BY_SIDE" ? "1fr 1fr" : "1fr",
                  gap: 12,
                }}
              >
                {/* Original Source */}
                {(viewMode === "SIDE_BY_SIDE" || viewMode === "ORIGINAL") && (
                  <div
                    style={{
                      backgroundColor: "var(--clinova-surface)",
                      border: "1px solid var(--clinova-border)",
                      borderRadius: 6,
                      padding: 10,
                    }}
                  >
                    <div style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--clinova-text-muted)", marginBottom: 4 }}>
                      AUTHORITATIVE ORIGINAL SOURCE ({languageLabels[item.source_language] || item.source_language})
                    </div>
                    <div style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)", whiteSpace: "pre-wrap" }}>
                      {item.source_text}
                    </div>
                  </div>
                )}

                {/* Translated Representation */}
                {(viewMode === "SIDE_BY_SIDE" || viewMode === "TRANSLATION") && (
                  <div
                    style={{
                      backgroundColor: "var(--clinova-surface)",
                      border: "1px solid var(--clinova-border)",
                      borderRadius: 6,
                      padding: 10,
                    }}
                  >
                    <div style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--clinova-text-muted)", marginBottom: 4 }}>
                      DERIVED TRANSLATION ({languageLabels[item.target_language] || item.target_language})
                    </div>
                    {editingId === item.id ? (
                      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                        <textarea
                          className="clinova-input"
                          rows={3}
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          style={{ width: "100%", fontSize: "0.875rem" }}
                        />
                        <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                          <Button variant="secondary" size="sm" onClick={() => setEditingId(null)}>
                            <X style={{ width: 12, height: 12 }} />
                            <span>Cancel</span>
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={isSavingCorrection}
                            onClick={() => handleSaveCorrection(item.id)}
                          >
                            <Save style={{ width: 12, height: 12 }} />
                            <span>Save Correction</span>
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)", whiteSpace: "pre-wrap" }}>
                        {item.translated_text}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Clinician Review Actions */}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 8 }}>
                {item.review_status !== "VERIFIED" && editingId !== item.id && (
                  <>
                    <Button variant="outline" size="sm" onClick={() => handleVerify(item.id)}>
                      <CheckCircle2 style={{ width: 12, height: 12 }} />
                      <span>Verify Accuracy</span>
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleStartEdit(item)}>
                      <Edit3 style={{ width: 12, height: 12 }} />
                      <span>Correct Translation</span>
                    </Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Request New Translation Bar */}
      <div
        style={{
          marginTop: 8,
          borderTop: "1px solid var(--clinova-border)",
          paddingTop: 12,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        <div style={{ fontSize: "0.8125rem", fontWeight: 600 }}>Request New Text Translation</div>
        <textarea
          className="clinova-input"
          rows={2}
          placeholder="Enter text to translate..."
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          style={{ width: "100%", fontSize: "0.8125rem" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <select
              className="clinova-select"
              style={{ fontSize: "0.75rem", padding: "4px 8px" }}
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
            >
              <option value="hi">Source: Hindi (हिन्दी)</option>
              <option value="or">Source: Odia (ଓଡ଼ିଆ)</option>
              <option value="en">Source: English</option>
            </select>
            <select
              className="clinova-select"
              style={{ fontSize: "0.75rem", padding: "4px 8px" }}
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
            >
              <option value="en">Target: English</option>
              <option value="hi">Target: Hindi (हिन्दी)</option>
              <option value="or">Target: Odia (ଓଡ଼ିଆ)</option>
            </select>
          </div>

          <Button
            variant="primary"
            size="sm"
            disabled={isTranslating || !newText.trim()}
            onClick={handleRequestTranslation}
          >
            <Globe style={{ width: 12, height: 12 }} />
            <span>{isTranslating ? "Translating..." : "Translate Text"}</span>
          </Button>
        </div>
      </div>
    </div>
  );
};
