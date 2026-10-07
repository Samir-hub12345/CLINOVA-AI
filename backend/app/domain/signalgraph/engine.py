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

    def record_event(self, facility_id: str, syndrome_tag: str, acuity_tier: str) -> Dict[str, Any]:
        """Ingests a real de-identified event from the clinical workflow."""
        event = {
            "id": f"sig-ev-{len(self.events) + 1}",
            "facility_id": facility_id,
            "syndrome_tag": syndrome_tag,
            "acuity_tier": acuity_tier,
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


# Global singleton instance for prototype runtime
signal_engine = SignalGraphEngine()
