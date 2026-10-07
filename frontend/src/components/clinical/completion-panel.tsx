"use client";

import React, { useState, useEffect } from "react";
import {
  CompletionSession,
  CompletionQuestion,
  NextQuestionResponse,
} from "@/types";
import { completionApi } from "@/lib/api";

interface CompletionPanelProps {
  caseId: string;
  onCaseUpdated?: () => void;
}

export function CompletionPanel({ caseId, onCaseUpdated }: CompletionPanelProps) {
  const [session, setSession] = useState<CompletionSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<CompletionQuestion | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    loadSessionAndNextQuestion();
  }, [caseId]);

  const loadSessionAndNextQuestion = async () => {
    setLoading(true);
    setError(null);
    try {
      const sessRes = await completionApi.getSession(caseId);
      if (sessRes.data) {
        setSession(sessRes.data);
        const nextRes = await completionApi.getNextQuestion(caseId);
        if (nextRes.data) {
          setCurrentQuestion(nextRes.data.question || null);
          setIsCompleted(nextRes.data.is_complete);
        }
      }
    } catch (err: any) {
      // 404 indicates no completion session has been initiated yet for this case
      if (err.message && (err.message.includes("404") || err.message.includes("Not Found"))) {
        setSession(null);
        setCurrentQuestion(null);
      } else {
        setError(err.message || "Failed to load completion session.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await completionApi.startSession(caseId);
      if (res.data) {
        setSession(res.data);
        const nextRes = await completionApi.getNextQuestion(caseId);
        if (nextRes.data) {
          setCurrentQuestion(nextRes.data.question || null);
          setIsCompleted(nextRes.data.is_complete);
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to start intelligent completion session.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion) return;
    const finalAnswer = selectedOption || answerText.trim();
    if (!finalAnswer) {
      setError("Please select an option or enter an answer.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await completionApi.submitAnswer(caseId, currentQuestion.id, {
        raw_answer_text: finalAnswer,
        modality: selectedOption ? "patient_choice" : "patient_text",
      });

      if (res.data) {
        setSelectedOption(null);
        setAnswerText("");
        setCurrentQuestion(res.data.next_question || null);
        setIsCompleted(res.data.is_session_complete);

        // Reload session data for fresh progress
        const sessRes = await completionApi.getSession(caseId);
        if (sessRes.data) setSession(sessRes.data);

        if (onCaseUpdated) {
          onCaseUpdated();
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit answer.");
    } finally {
      setLoading(false);
    }
  };

  const handleSkipQuestion = async () => {
    if (!currentQuestion) return;
    setLoading(true);
    setError(null);
    try {
      const res = await completionApi.skipQuestion(caseId, currentQuestion.id, {
        reason: "patient_skipped",
      });

      if (res.data) {
        setSelectedOption(null);
        setAnswerText("");
        setCurrentQuestion(res.data.next_question || null);
        setIsCompleted(res.data.is_session_complete);

        const sessRes = await completionApi.getSession(caseId);
        if (sessRes.data) setSession(sessRes.data);

        if (onCaseUpdated) {
          onCaseUpdated();
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to skip question.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <span>Intelligent Completion</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-emerald-100 text-emerald-800">
              Phase 5
            </span>
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Adaptive interview to fill verified clinical information gaps before physician review.
          </p>
        </div>

        {session && (
          <div className="text-right">
            <span className="text-xs text-slate-400 block">Readiness Score</span>
            <span className="text-xl font-bold text-emerald-600">
              {Math.round(session.current_readiness_score * 100)}%
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* No Active Session State */}
      {!session && !loading && (
        <div className="text-center py-8 space-y-4">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto text-xl font-bold">
            ?
          </div>
          <p className="text-slate-600 text-sm max-w-md mx-auto">
            Begin an adaptive completion session to ask targeted follow-up questions,
            clarify ambiguities, and improve case completeness.
          </p>
          <button
            onClick={handleStartSession}
            disabled={loading}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg transition-colors shadow-sm"
          >
            Start Completion Interview
          </button>
        </div>
      )}

      {/* Active Session with Question */}
      {session && !isCompleted && currentQuestion && (
        <div className="space-y-5">
          {/* Progress Indicator */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-slate-500">
              <span>Turn {session.current_turn} of {session.max_turns}</span>
              <span>{session.remaining_gap_count} gaps remaining</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${(session.current_turn / session.max_turns) * 100}%` }}
              />
            </div>
          </div>

          {/* Question Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <h4 className="text-base font-medium text-slate-900">
                {currentQuestion.question_text}
              </h4>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-medium whitespace-nowrap">
                {currentQuestion.target_field.replace("_", " ")}
              </span>
            </div>

            {/* Clinical Rationale (Transparent, Non-Diagnostic) */}
            <p className="text-xs text-slate-500 italic">
              Clinical Rationale: {currentQuestion.clinical_rationale}
            </p>

            {/* Single Choice Options */}
            {currentQuestion.options && currentQuestion.options.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                {currentQuestion.options.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setSelectedOption(opt.value)}
                    className={`text-left px-4 py-3 rounded-lg border text-sm font-medium transition-all ${
                      selectedOption === opt.value
                        ? "bg-blue-50 border-blue-600 text-blue-900 shadow-sm"
                        : "bg-white border-slate-200 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            )}

            {/* Free Text Input */}
            {(!currentQuestion.options || currentQuestion.options.length === 0) && (
              <textarea
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder={currentQuestion.placeholder || "Enter details..."}
                rows={3}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={handleSkipQuestion}
              disabled={loading}
              className="text-sm text-slate-500 hover:text-slate-800 transition-colors"
            >
              Skip Question
            </button>

            <button
              type="button"
              onClick={handleSubmitAnswer}
              disabled={loading || (!selectedOption && !answerText.trim())}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium text-sm rounded-lg transition-colors shadow-sm"
            >
              {loading ? "Updating Case..." : "Submit & Continue"}
            </button>
          </div>
        </div>
      )}

      {/* Completed State */}
      {session && isCompleted && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6 text-center space-y-3">
          <div className="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto font-bold">
            ✓
          </div>
          <h4 className="text-base font-semibold text-emerald-900">
            Intelligent Completion Concluded
          </h4>
          <p className="text-sm text-emerald-700 max-w-md mx-auto">
            {session.stopping_reason || "All prioritized questions answered. Case is ready for clinician review."}
          </p>
          <div className="pt-2 text-xs text-emerald-800">
            Final Readiness: {Math.round(session.current_readiness_score * 100)}% ({session.questions_answered_count} questions answered)
          </div>
        </div>
      )}

      {/* Persistent Non-Diagnostic Disclaimer */}
      <div className="text-[11px] text-slate-400 text-center border-t border-slate-100 pt-3">
        Educational prototype only. Intelligent Completion asks questions to improve intake information.
        Does not diagnose disease, prescribe medication, or replace physician review.
      </div>
    </div>
  );
}
