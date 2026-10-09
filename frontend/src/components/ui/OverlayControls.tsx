"use client";

import React, { useEffect } from "react";
import { X, AlertTriangle } from "lucide-react";
import { Button } from "./Button";
import { IconButton } from "./IconButton";

export const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}> = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="clinova-modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="clinova-modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--clinova-space-4)" }}>
          <h3 id="modal-title">{title}</h3>
          <IconButton label="Close Dialog" onClick={onClose}>
            <X style={{ width: 16, height: 16 }} aria-hidden="true" />
          </IconButton>
        </div>
        {children}
      </div>
    </div>
  );
};

export const Drawer: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  width?: number;
}> = ({ isOpen, onClose, title, subtitle, children, width = 560 }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="clinova-drawer-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div
        className="clinova-drawer-panel"
        style={{ maxWidth: width }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            padding: "var(--clinova-space-5) var(--clinova-space-6)",
            borderBottom: "1px solid var(--clinova-border)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            backgroundColor: "var(--clinova-surface-subtle)",
          }}
        >
          <div>
            <h3 id="drawer-title" style={{ fontSize: "1.125rem" }}>{title}</h3>
            {subtitle && <p style={{ fontSize: "0.8125rem", marginTop: 2 }}>{subtitle}</p>}
          </div>
          <IconButton label="Close Drawer" onClick={onClose}>
            <X style={{ width: 16, height: 16 }} aria-hidden="true" />
          </IconButton>
        </div>

        <div style={{ padding: "var(--clinova-space-6)", flex: 1, overflowY: "auto" }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export const ConfirmationDialog: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  isDestructive?: boolean;
}> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirm Action",
  isDestructive = false,
}) => {
  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
          {isDestructive && (
            <AlertTriangle style={{ width: 22, height: 22, color: "var(--clinova-danger)", flexShrink: 0 }} aria-hidden="true" />
          )}
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>{message}</p>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 8 }}>
          <Button variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant={isDestructive ? "danger" : "primary"}
            size="md"
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
