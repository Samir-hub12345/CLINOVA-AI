"""Care Orchestration Domain Package.

Responsible for:
- Connecting patient clinical state (CareGraph), evidence uncertainty,
  facility capability/capacity (FacilityGraph), and system context (SignalGraph).
- Recommending the safest achievable next care action.
- Enforcing mandatory human-in-the-loop review before any action execution.
- Guaranteeing strictly advisory, non-diagnostic operation.
"""
