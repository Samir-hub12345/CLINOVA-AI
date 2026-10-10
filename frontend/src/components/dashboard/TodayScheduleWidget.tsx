"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Calendar, ArrowRight } from "lucide-react";

export interface AppointmentItem {
  id: string;
  time: string;
  patient: string;
  patientId: string;
  type: string;
  clinician: string;
  status: "In progress" | "Completed" | "Scheduled";
  mine: boolean;
  avatar: string;
}

export const DEFAULT_APPOINTMENTS: AppointmentItem[] = [
  {
    id: "apt-1",
    time: "09:00",
    patient: "Manoj Das",
    patientId: "CASE-SYNTH-003",
    type: "Chest pain & acute triage consult",
    clinician: "Dr. Priya Sharma",
    status: "In progress",
    mine: true,
    avatar: "MD",
  },
  {
    id: "apt-2",
    time: "09:30",
    patient: "Sunita Devi",
    patientId: "CASE-SYNTH-004",
    type: "Severe headache & hypertension review",
    clinician: "Dr. Priya Sharma",
    status: "Completed",
    mine: true,
    avatar: "SD",
  },
  {
    id: "apt-3",
    time: "10:15",
    patient: "Rajesh Kumar",
    patientId: "CASE-SYNTH-005",
    type: "Respiratory distress & fever consult",
    clinician: "Dr. Amit Roy",
    status: "Scheduled",
    mine: false,
    avatar: "RK",
  },
  {
    id: "apt-4",
    time: "11:00",
    patient: "Priya Sen",
    patientId: "CASE-SYNTH-001",
    type: "Abdominal colic & vitals acquisition",
    clinician: "Dr. Priya Sharma",
    status: "Scheduled",
    mine: true,
    avatar: "PS",
  },
  {
    id: "apt-5",
    time: "11:45",
    patient: "Ananya Roy",
    patientId: "CASE-SYNTH-006",
    type: "Hypertension follow-up & medication review",
    clinician: "Dr. Amit Roy",
    status: "Scheduled",
    mine: false,
    avatar: "AR",
  },
];

interface TodayScheduleWidgetProps {
  appointments?: AppointmentItem[];
  compact?: boolean;
}

export const TodayScheduleWidget: React.FC<TodayScheduleWidgetProps> = ({
  appointments = DEFAULT_APPOINTMENTS,
  compact = false,
}) => {
  const router = useRouter();
  const [scheduleScope, setScheduleScope] = useState<"mine" | "all">("mine");

  const filteredAppointments =
    scheduleScope === "mine"
      ? appointments.filter((apt) => apt.mine)
      : appointments;

  const renderStatusBadge = (status: "In progress" | "Completed" | "Scheduled") => {
    if (status === "In progress") {
      return <span className="badge badge-teal">In progress</span>;
    }
    if (status === "Completed") {
      return <span className="badge badge-success">Completed</span>;
    }
    return <span className="badge badge-warning">Scheduled</span>;
  };

  return (
    <div className="card" aria-labelledby="sched-heading">
      <div className="card-header">
        <div className="row gap-2">
          <Calendar style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
          <h2 id="sched-heading" style={{ margin: 0, fontSize: "1.125rem", fontWeight: 700 }}>
            Today&apos;s Schedule
          </h2>
        </div>
        <div className="segmented" role="group" aria-label="Schedule scope">
          <button
            type="button"
            aria-pressed={scheduleScope === "mine"}
            onClick={() => setScheduleScope("mine")}
          >
            My patients ({appointments.filter((a) => a.mine).length})
          </button>
          <button
            type="button"
            aria-pressed={scheduleScope === "all"}
            onClick={() => setScheduleScope("all")}
          >
            Whole clinic ({appointments.length})
          </button>
        </div>
      </div>
      <div className="table-wrap">
        <table className="table responsive">
          <thead>
            <tr>
              <th>Time</th>
              <th>Patient</th>
              <th>Consultation Type</th>
              {scheduleScope === "all" && <th>Clinician</th>}
              <th>Status</th>
              <th style={{ textAlign: "right" }}>
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredAppointments.length === 0 ? (
              <tr>
                <td
                  colSpan={scheduleScope === "all" ? 6 : 5}
                  style={{
                    textAlign: "center",
                    padding: "24px 16px",
                    color: "var(--text-3)",
                  }}
                >
                  No appointments scheduled for this view.
                </td>
              </tr>
            ) : (
              filteredAppointments.map((apt) => (
                <tr
                  key={apt.id}
                  className="clickable"
                  onClick={() => {
                    router.push(`/staff/cases/${apt.patientId}`);
                  }}
                >
                  <td data-label="Time" className="tnum medium">
                    {apt.time}
                  </td>
                  <td className="primary-cell">
                    <div className="row gap-2">
                      <span className="avatar sm">{apt.avatar}</span>
                      <span className="medium" style={{ color: "var(--navy-900)" }}>
                        {apt.patient}
                      </span>
                      {apt.patientId === "CASE-SYNTH-003" && (
                        <span className="badge badge-teal">Demo</span>
                      )}
                    </div>
                  </td>
                  <td data-label="Type" className="subtle">
                    {apt.type}
                  </td>
                  {scheduleScope === "all" && (
                    <td data-label="Clinician" className="subtle">
                      {apt.clinician}
                    </td>
                  )}
                  <td data-label="Status">
                    {renderStatusBadge(apt.status)}
                  </td>
                  <td className="hide-sm" style={{ textAlign: "right" }}>
                    <Link
                      href={`/staff/cases/${apt.patientId}`}
                      className="btn btn-ghost btn-sm"
                      onClick={(e) => e.stopPropagation()}
                      aria-label={`Open record for ${apt.patient}`}
                    >
                      <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {!compact && (
        <div className="card-footer">
          <Link href="/staff/reception" className="btn btn-secondary btn-sm btn-block">
            <span>Open Reception & Intake Desk</span>
            <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
          </Link>
        </div>
      )}
    </div>
  );
};
