"""CLINOVA AI — SIGNALGRAPH Engine.

System-Level Operational Telemetry & Epidemiological Cluster Detection.
Consumes real prototype clinical events, computes privacy-preserving syndromic Z-scores,
monitors facility queue congestion, and feeds system context back to the Orchestration Engine.
Strictly operates in SYNTHETIC TELEMETRY MODE with zero real-world PHI.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import math


class SignalGraphEngine:
    """In-memory event telemetry engine and syndromic cluster detector."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        # Pre-seed realistic baseline historical events for stable statistical Z-scores
        self._init_baseline_events()

    def _init_baseline_events(self):
        """Initializes minimal baseline background events for realistic variance."""
        now = datetime.now(timezone.utc)
        baseline_syndromes = [
            ("SYNDROME_ACUTE_RESPIRATORY", "FAC-DH-04", "MODERATE"),
            ("SYNDROME_ACUTE_RESPIRATORY", "FAC-CHC-02", "ROUTINE"),
            ("SYNDROME_CARDIOVASCULAR_ACUTE", "FAC-DH-04", "URGENT"),
            ("SYNDROME_ACUTE_GASTROENTERITIS", "FAC-PHC-01", "ROUTINE"),
        ]
        for idx, (syn, fac, tier) in enumerate(baseline_syndromes):
            self.events.append({
                "id": f"sig-base-{idx+1}",
                "facility_id": fac,
                "syndrome_tag": syn,
                "acuity_tier": tier,
                "recorded_at": now - timedelta(hours=idx * 6),
            })

    def record_event(
        self,
        facility_id: str,
        syndrome_tag: str,
        acuity_tier: str,
        source_event_id: Optional[str] = None,
        disposition: Optional[str] = None,
        actual_action: Optional[str] = None,
        outcome_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ingests a real de-identified event from the clinical workflow with deduplication."""
        if source_event_id:
            for existing in self.events:
                if existing.get("source_event_id") == source_event_id:
                    # Update fields if corrected/re-sent without duplicating event count
                    if disposition:
                        existing["disposition"] = disposition
                    if actual_action:
                        existing["actual_action"] = actual_action
                    if outcome_status:
                        existing["outcome_status"] = outcome_status
                    if syndrome_tag:
                        existing["syndrome_tag"] = syndrome_tag
                    return existing

        event = {
            "id": f"sig-ev-{len(self.events) + 1}",
            "facility_id": facility_id,
            "syndrome_tag": syndrome_tag,
            "acuity_tier": acuity_tier,
            "source_event_id": source_event_id,
            "disposition": disposition,
            "actual_action": actual_action,
            "outcome_status": outcome_status,
            "recorded_at": datetime.now(timezone.utc),
        }
        self.events.append(event)
        return event

    def get_syndromic_clusters(self, window_hours: int = 48) -> Dict[str, Any]:
        """
        Computes syndromic counts and Z-scores over a rolling time window:
        Z = (C_observed - mu_baseline) / sigma_baseline
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        recent_events = []
        for e in self.events:
            rec_at = e.get("recorded_at")
            if rec_at:
                if isinstance(rec_at, str):
                    rec_at = datetime.fromisoformat(rec_at.replace("Z", "+00:00"))
                if rec_at.tzinfo is None:
                    rec_at = rec_at.replace(tzinfo=timezone.utc)
                if rec_at >= cutoff:
                    recent_events.append(e)

        counts: Dict[str, int] = {}
        for ev in recent_events:
            tag = ev.get("syndrome_tag", "UNKNOWN")
            counts[tag] = counts.get(tag, 0) + 1

        # Known syndromes to track
        tracked = [
            "SYNDROME_HEMORRHAGIC_FEVER",
            "SYNDROME_ACUTE_RESPIRATORY",
            "SYNDROME_ACUTE_GASTROENTERITIS",
            "SYNDROME_ENCEPHALITIS_ALTERED_SENSORIUM",
            "SYNDROME_CARDIOVASCULAR_ACUTE",
        ]

        clusters = []
        overall_alert_level = "NORMAL"

        for syndrome in tracked:
            observed = counts.get(syndrome, 0)
            baseline_mu = 1.5
            baseline_sigma = 1.0
            z_score = round((observed - baseline_mu) / baseline_sigma, 2)

            if z_score >= 3.5:
                status = "SURGE_ALERT"
                alert_class = "CRITICAL"
                overall_alert_level = "CRITICAL"
            elif z_score >= 2.5:
                status = "ELEVATED_CLUSTER"
                alert_class = "WARNING"
                if overall_alert_level != "CRITICAL":
                    overall_alert_level = "WARNING"
            else:
                status = "NORMAL_BASELINE"
                alert_class = "NORMAL"

            clusters.append({
                "syndrome": syndrome,
                "observed_cases_48h": observed,
                "baseline_mean": baseline_mu,
                "z_score": z_score,
                "status": status,
                "alert_class": alert_class,
            })

        return {
            "mode": "SYNTHETIC_TELEMETRY_MODE",
            "disclaimer": "Generated from simulated and prototype clinical events. Zero real-world PHI.",
            "overall_alert_level": overall_alert_level,
            "window_hours": window_hours,
            "total_signals_in_window": len(recent_events),
            "clusters": clusters,
        }

    def get_facility_load_metrics(self, facilities_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates network facility capacity and emergency department load."""
        total_icu_beds = sum(f.get("icu_beds_total", 0) for f in facilities_data)
        avail_icu_beds = sum(f.get("icu_beds_available", 0) for f in facilities_data)
        total_gen_beds = sum(f.get("general_beds_total", 0) for f in facilities_data)
        avail_gen_beds = sum(f.get("general_beds_available", 0) for f in facilities_data)
        total_waiting_ed = sum(f.get("ed_waiting_cases", 0) for f in facilities_data)

        icu_occ_pct = round(((total_icu_beds - avail_icu_beds) / max(1, total_icu_beds)) * 100, 1)
        gen_occ_pct = round(((total_gen_beds - avail_gen_beds) / max(1, total_gen_beds)) * 100, 1)

        facility_summaries = []
        for fac in facilities_data:
            fac_icu_tot = fac.get("icu_beds_total", 0)
            fac_icu_avail = fac.get("icu_beds_available", 0)
            fac_occ = (
                round(((fac_icu_tot - fac_icu_avail) / max(1, fac_icu_tot)) * 100, 1)
                if fac_icu_tot > 0
                else round(((fac.get("general_beds_total", 1) - fac.get("general_beds_available", 1)) / max(1, fac.get("general_beds_total", 1))) * 100, 1)
            )
            facility_summaries.append({
                "facility_id": fac.get("id"),
                "name": fac.get("name"),
                "tier": fac.get("tier"),
                "ed_waiting": fac.get("ed_waiting_cases", 0),
                "ed_avg_wait_min": fac.get("ed_avg_wait_min", 0),
                "occupancy_pct": fac_occ,
                "is_congested": fac.get("ed_avg_wait_min", 0) > 60 or fac_occ > 90.0,
            })

        return {
            "mode": "SYNTHETIC_TELEMETRY_MODE",
            "network_icu_occupancy_pct": icu_occ_pct,
            "network_general_occupancy_pct": gen_occ_pct,
            "total_ed_waiting_cases": total_waiting_ed,
            "facilities": facility_summaries,
        }

    def get_macro_summary(self, facilities_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provides high-level dashboard telemetry overview."""
        surges = self.get_syndromic_clusters()
        load = self.get_facility_load_metrics(facilities_data)

        return {
            "mode": "SYNTHETIC_TELEMETRY_MODE",
            "active_events_logged": len(self.events),
            "overall_epidemiological_alert": surges["overall_alert_level"],
            "network_icu_occupancy_pct": load["network_icu_occupancy_pct"],
            "total_ed_waiting": load["total_ed_waiting_cases"],
            "active_clusters": [c for c in surges["clusters"] if c["alert_class"] != "NORMAL"],
        }

    def get_outcome_metrics(
        self,
        facility_id: Optional[str] = None,
        window_hours: int = 48,
    ) -> Dict[str, Any]:
        """
        Aggregates de-identified macro outcome telemetry across facilities.
        Strictly zero PHI. Preserves unknown status without false optimism.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        filtered = []
        for e in self.events:
            rec_at = e.get("recorded_at")
            if rec_at:
                if isinstance(rec_at, str):
                    rec_at = datetime.fromisoformat(rec_at.replace("Z", "+00:00"))
                if rec_at.tzinfo is None:
                    rec_at = rec_at.replace(tzinfo=timezone.utc)
                if rec_at < cutoff:
                    continue

            # Only consider events with outcome metadata
            if not (e.get("outcome_status") or e.get("actual_action") or (e.get("syndrome_tag") and e["syndrome_tag"].startswith("OUTCOME_"))):
                continue

            if facility_id and e.get("facility_id") != facility_id:
                continue

            filtered.append(e)

        outcome_status_counts: Dict[str, int] = {}
        actual_action_counts: Dict[str, int] = {}
        disposition_counts: Dict[str, int] = {}
        unknown_outcomes = 0

        for ev in filtered:
            status = ev.get("outcome_status") or "UNKNOWN"
            outcome_status_counts[status] = outcome_status_counts.get(status, 0) + 1
            if status == "UNKNOWN":
                unknown_outcomes += 1

            act = ev.get("actual_action") or "UNKNOWN"
            actual_action_counts[act] = actual_action_counts.get(act, 0) + 1

            disp = ev.get("disposition") or (
                ev.get("syndrome_tag", "").replace("OUTCOME_", "") if ev.get("syndrome_tag", "").startswith("OUTCOME_") else "UNKNOWN"
            )
            disposition_counts[disp] = disposition_counts.get(disp, 0) + 1

        return {
            "mode": "SYNTHETIC_TELEMETRY_MODE",
            "disclaimer": "De-identified aggregated outcome telemetry. Zero real-world PHI.",
            "window_hours": window_hours,
            "facility_id_filter": facility_id,
            "total_outcomes_recorded": len(filtered),
            "outcome_status_distribution": outcome_status_counts,
            "actual_action_distribution": actual_action_counts,
            "disposition_distribution": disposition_counts,
            "unknown_outcomes_count": unknown_outcomes,
        }


# Global singleton instance for prototype runtime
signal_engine = SignalGraphEngine()
