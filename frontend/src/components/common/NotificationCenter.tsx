"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Bell,
  CheckCheck,
  AlertTriangle,
  Stethoscope,
  FileScan,
  Share2,
  CheckCircle2,
  X,
  ArrowRight,
  Filter,
} from "lucide-react";

export interface ClinicalNotification {
  id: string;
  category: "CRITICAL" | "REVIEW" | "LAB_OCR" | "TRANSFER" | "SYSTEM";
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  targetHref: string;
  caseId?: string;
  patientToken?: string;
}

const DEFAULT_NOTIFICATIONS: ClinicalNotification[] = [
  {
    id: "notif-001",
    category: "CRITICAL",
    title: "Critical Red Flag: Decompensated Shock",
    message: "Patient PT-SYN-0842 Shock Index > 1.0 (HR 114, BP 88/54). Immediate resuscitation review required.",
    timestamp: "4m ago",
    isRead: false,
    targetHref: "/staff/cases/CASE-SYNTH-003",
    caseId: "CASE-SYNTH-003",
    patientToken: "PT-SYN-0842",
  },
  {
    id: "notif-002",
    category: "REVIEW",
    title: "Attending Review Sign-Off Pending",
    message: "Dr. Priya Sharma: 2 cases in Cuttack DHH OPD queue awaiting authoritative decision sign-off.",
    timestamp: "18m ago",
    isRead: false,
    targetHref: "/staff/review",
  },
  {
    id: "notif-003",
    category: "LAB_OCR",
    title: "Lab Report OCR Ingestion Complete",
    message: "High-confidence extraction: Trop-I 1.45 ng/mL verified against Cuttack DHH reference ranges.",
    timestamp: "32m ago",
    isRead: false,
    targetHref: "/staff/cases/CASE-SYNTH-003",
    caseId: "CASE-SYNTH-003",
  },
  {
    id: "notif-004",
    category: "TRANSFER",
    title: "SBAR Transfer Packet Dispatched",
    message: "Inter-facility transfer to SCB Medical College Cath Lab accepted. Ambulance en route.",
    timestamp: "1h ago",
    isRead: true,
    targetHref: "/referrals",
  },
  {
    id: "notif-005",
    category: "SYSTEM",
    title: "Audit Ledger Checkpoint Verified",
    message: "Cryptographic hash chain validated with zero PII leaks across 18 active patient records.",
    timestamp: "2h ago",
    isRead: true,
    targetHref: "/system",
  },
];

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"ALL" | "CRITICAL" | "REVIEW" | "LAB_OCR" | "TRANSFER">("ALL");
  const [notifications, setNotifications] = useState<ClinicalNotification[]>(DEFAULT_NOTIFICATIONS);
  const popoverRef = useRef<HTMLDivElement>(null);

  // Load persisted read states
  useEffect(() => {
    try {
      const stored = localStorage.getItem("clinova_notifications_state");
      if (stored) {
        const readIds = new Set(JSON.parse(stored));
        setNotifications((prev) =>
          prev.map((n) => ({
            ...n,
            isRead: readIds.has(n.id) ? true : n.isRead,
          }))
        );
      }
    } catch {
      // Fallback
    }
  }, []);

  // Sync read states to localStorage
  const saveReadState = (updatedList: ClinicalNotification[]) => {
    try {
      const readIds = updatedList.filter((n) => n.isRead).map((n) => n.id);
      localStorage.setItem("clinova_notifications_state", JSON.stringify(readIds));
    } catch {
      // Ignore storage errors
    }
  };

  // Close when clicking outside
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleOutsideClick);
    }
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [isOpen]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAllAsRead = () => {
    const updated = notifications.map((n) => ({ ...n, isRead: true }));
    setNotifications(updated);
    saveReadState(updated);
  };

  const toggleRead = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = notifications.map((n) =>
      n.id === id ? { ...n, isRead: !n.isRead } : n
    );
    setNotifications(updated);
    saveReadState(updated);
  };

  const filtered = notifications.filter((n) => {
    if (activeTab === "ALL") return true;
    return n.category === activeTab;
  });

  const getCategoryBadge = (category: ClinicalNotification["category"]) => {
    switch (category) {
      case "CRITICAL":
        return <span className="badge badge-emergency">Critical Alert</span>;
      case "REVIEW":
        return <span className="badge badge-warning">Physician Review</span>;
      case "LAB_OCR":
        return <span className="badge badge-purple">Lab & OCR</span>;
      case "TRANSFER":
        return <span className="badge badge-teal">Transfer & SBAR</span>;
      default:
        return <span className="badge badge-navy">System</span>;
    }
  };

  const getCategoryIcon = (category: ClinicalNotification["category"]) => {
    switch (category) {
      case "CRITICAL":
        return <AlertTriangle style={{ width: 14, height: 14, color: "var(--clinova-emergency)" }} aria-hidden="true" />;
      case "REVIEW":
        return <Stethoscope style={{ width: 14, height: 14, color: "var(--warning)" }} aria-hidden="true" />;
      case "LAB_OCR":
        return <FileScan style={{ width: 14, height: 14, color: "var(--purple-600, #7c3aed)" }} aria-hidden="true" />;
      case "TRANSFER":
        return <Share2 style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />;
      default:
        return <CheckCircle2 style={{ width: 14, height: 14, color: "var(--text-2)" }} aria-hidden="true" />;
    }
  };

  return (
    <div style={{ position: "relative" }} ref={popoverRef}>
      {/* Trigger Bell Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="clinova-icon-btn"
        aria-label={`Clinical notifications (${unreadCount} unread)`}
        title="Open Clinical Notifications & Alerts"
        style={{ position: "relative" }}
      >
        <Bell style={{ width: 16, height: 16 }} aria-hidden="true" />
        {unreadCount > 0 && (
          <span
            style={{
              position: "absolute",
              top: 2,
              right: 2,
              backgroundColor: "var(--clinova-emergency)",
              color: "#fff",
              fontSize: "0.625rem",
              fontWeight: 800,
              width: 15,
              height: 15,
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              lineHeight: 1,
              border: "1.5px solid var(--clinova-surface)",
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {/* Floating Notification Popover Dropdown */}
      {isOpen && (
        <div
          role="region"
          aria-label="Clinical Notifications Panel"
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            width: 380,
            maxWidth: "90vw",
            backgroundColor: "var(--clinova-surface)",
            borderRadius: "var(--clinova-radius-lg, 10px)",
            border: "1px solid var(--clinova-border)",
            boxShadow: "0 12px 30px -4px rgba(0, 0, 0, 0.18), 0 4px 12px -2px rgba(0, 0, 0, 0.08)",
            zIndex: 100,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            animation: "fadeIn 0.15s ease",
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "12px 16px",
              borderBottom: "1px solid var(--clinova-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              backgroundColor: "var(--clinova-surface-subtle)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Bell style={{ width: 15, height: 15, color: "var(--clinova-accent)" }} aria-hidden="true" />
              <strong style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)" }}>
                Notifications & Alerts
              </strong>
              {unreadCount > 0 && (
                <span className="badge badge-emergency" style={{ fontSize: "0.625rem", padding: "1px 6px" }}>
                  {unreadCount} new
                </span>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={markAllAsRead}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: "0.6875rem", padding: "2px 6px", height: "auto" }}
                  title="Mark all notifications as read"
                >
                  <CheckCheck style={{ width: 12, height: 12 }} aria-hidden="true" />
                  <span>Mark all read</span>
                </button>
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="clinova-icon-btn"
                style={{ width: 24, height: 24 }}
                aria-label="Close notifications"
              >
                <X style={{ width: 14, height: 14 }} aria-hidden="true" />
              </button>
            </div>
          </div>

          {/* Category Filter Tabs */}
          <div
            style={{
              display: "flex",
              borderBottom: "1px solid var(--clinova-border)",
              padding: "4px 8px",
              gap: 4,
              backgroundColor: "var(--clinova-surface)",
              overflowX: "auto",
            }}
          >
            {[
              { id: "ALL", label: "All" },
              { id: "CRITICAL", label: "Critical" },
              { id: "REVIEW", label: "Reviews" },
              { id: "LAB_OCR", label: "Labs" },
              { id: "TRANSFER", label: "Transfers" },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                style={{
                  fontSize: "0.6875rem",
                  fontWeight: activeTab === tab.id ? 700 : 500,
                  padding: "4px 8px",
                  borderRadius: "var(--clinova-radius-sm)",
                  border: "none",
                  backgroundColor: activeTab === tab.id ? "var(--clinova-accent-light)" : "transparent",
                  color: activeTab === tab.id ? "var(--clinova-accent-text)" : "var(--clinova-text-secondary)",
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Notifications Scroll List */}
          <div style={{ maxHeight: 340, overflowY: "auto", padding: "4px 0" }}>
            {filtered.length === 0 ? (
              <div style={{ padding: "32px 16px", textAlign: "center", color: "var(--clinova-text-muted)" }}>
                <p style={{ fontSize: "0.8125rem", margin: 0 }}>No alerts in this category</p>
              </div>
            ) : (
              filtered.map((item) => (
                <div
                  key={item.id}
                  style={{
                    padding: "10px 14px",
                    borderBottom: "1px solid var(--clinova-border-subtle, #f1f5f9)",
                    backgroundColor: item.isRead ? "transparent" : "var(--clinova-accent-subtle, #f0fdfa)",
                    display: "flex",
                    gap: 10,
                    alignItems: "flex-start",
                    transition: "background 0.15s ease",
                  }}
                >
                  {/* Category icon */}
                  <div style={{ marginTop: 2, flexShrink: 0 }}>
                    {getCategoryIcon(item.category)}
                  </div>

                  {/* Text details */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 6, marginBottom: 2 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        {!item.isRead && (
                          <span
                            style={{
                              width: 6,
                              height: 6,
                              borderRadius: "50%",
                              backgroundColor: "var(--clinova-accent, #0d9488)",
                              display: "inline-block",
                            }}
                          />
                        )}
                        {getCategoryBadge(item.category)}
                      </div>
                      <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                        {item.timestamp}
                      </span>
                    </div>

                    <strong
                      style={{
                        fontSize: "0.8125rem",
                        color: "var(--clinova-text-primary)",
                        display: "block",
                        marginBottom: 2,
                      }}
                    >
                      {item.title}
                    </strong>

                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--clinova-text-secondary)",
                        margin: 0,
                        lineHeight: 1.4,
                      }}
                    >
                      {item.message}
                    </p>

                    {/* Action link & Mark Read toggle */}
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 6 }}>
                      <Link
                        href={item.targetHref}
                        onClick={() => {
                          setIsOpen(false);
                          const updated = notifications.map((n) =>
                            n.id === item.id ? { ...n, isRead: true } : n
                          );
                          setNotifications(updated);
                          saveReadState(updated);
                        }}
                        style={{
                          fontSize: "0.6875rem",
                          fontWeight: 600,
                          color: "var(--clinova-accent, #0d9488)",
                          textDecoration: "none",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                        }}
                      >
                        <span>Open Task</span>
                        <ArrowRight style={{ width: 11, height: 11 }} aria-hidden="true" />
                      </Link>

                      <button
                        type="button"
                        onClick={(e) => toggleRead(item.id, e)}
                        style={{
                          fontSize: "0.6875rem",
                          color: "var(--clinova-text-muted)",
                          border: "none",
                          background: "none",
                          cursor: "pointer",
                          padding: "2px 4px",
                        }}
                      >
                        {item.isRead ? "Mark unread" : "Mark read"}
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div
            style={{
              padding: "8px 14px",
              borderTop: "1px solid var(--clinova-border)",
              backgroundColor: "var(--clinova-surface-subtle)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
              Real-time clinical telemetry
            </span>
            <Link
              href="/staff/review"
              onClick={() => setIsOpen(false)}
              style={{
                fontSize: "0.6875rem",
                color: "var(--clinova-accent)",
                fontWeight: 600,
                textDecoration: "none",
              }}
            >
              View All Queue Items
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
