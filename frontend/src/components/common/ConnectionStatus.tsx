import React, { useEffect, useState } from "react";
import { Wifi, WifiOff, RefreshCw, AlertTriangle, CheckCircle2 } from "lucide-react";
import { ConnectionState } from "@/types";
import { getPendingCount } from "@/lib/offlineQueue";
import { triggerOfflineReconciliation } from "@/lib/api";

interface ConnectionStatusProps {
  status?: ConnectionState;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status = "ONLINE",
}) => {
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  useEffect(() => {
    const updateCount = () => {
      setPendingCount(getPendingCount());
    };

    updateCount();

    const handleQueueUpdate = () => {
      updateCount();
    };

    const handleOnline = async () => {
      updateCount();
      if (getPendingCount() > 0) {
        setIsSyncing(true);
        try {
          await triggerOfflineReconciliation();
        } finally {
          setIsSyncing(false);
          updateCount();
        }
      }
    };

    window.addEventListener("clinova:sync_queue_updated", handleQueueUpdate);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", updateCount);

    return () => {
      window.removeEventListener("clinova:sync_queue_updated", handleQueueUpdate);
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", updateCount);
    };
  }, []);

  const configs: Record<
    ConnectionState,
    { label: string; bg: string; color: string; border: string; icon: React.ReactNode }
  > = {
    ONLINE: {
      label: "ONLINE",
      bg: "#f0fdf4",
      color: "#15803d",
      border: "#bbf7d0",
      icon: <Wifi style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    OFFLINE: {
      label: "LOCAL / OFFLINE",
      bg: "#f8fafc",
      color: "#475569",
      border: "#cbd5e1",
      icon: <WifiOff style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    SYNCING: {
      label: "SYNCING",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#bae6fd",
      icon: <RefreshCw style={{ width: 12, height: 12, animation: "spin 2s linear infinite" }} aria-hidden="true" />,
    },
    SYNCED: {
      label: "SYNCED",
      bg: "#f0fdf4",
      color: "#15803d",
      border: "#bbf7d0",
      icon: <CheckCircle2 style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    SYNC_ERROR: {
      label: "SYNC ERROR",
      bg: "#fef2f2",
      color: "#b91c1c",
      border: "#fecaca",
      icon: <AlertTriangle style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    STALE_DATA: {
      label: "STALE TELEMETRY",
      bg: "#fffbeb",
      color: "#b45309",
      border: "#fde68a",
      icon: <AlertTriangle style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
  };

  const effectiveStatus = isSyncing ? "SYNCING" : status;
  const current = configs[effectiveStatus] || configs.ONLINE;

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: current.bg,
        color: current.color,
        borderColor: current.border,
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
      }}
      title={`System Connectivity: ${current.label}${pendingCount > 0 ? ` (${pendingCount} queued for sync)` : ""}`}
      role="status"
    >
      {current.icon}
      <span>{current.label}</span>
      {pendingCount > 0 && (
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            background: "#e2e8f0",
            color: "#334155",
            borderRadius: 8,
            padding: "1px 5px",
          }}
        >
          {pendingCount}
        </span>
      )}
    </span>
  );
};
