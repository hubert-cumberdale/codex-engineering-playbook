# Source of Truth: Detection Strategy Generator

This document defines where truth comes from and how conflicts are resolved.

---

## 1) Authoritative sources

### MITRE ATT&CK STIX (authoritative)
Authoritative for:
- detection strategy intent and scope
- analytic references and platform associations
- log source references and mutable elements
- any explicit technique/sub-technique relationships in the STIX graph

If MITRE data is absent, the system MUST say so explicitly.

---

### Company Profile + Overlays (authoritative)
Authoritative for:
- telemetry availability and organization-specific naming
- ownership, escalation, and routing
- priority policy / severity rubric
- response playbooks and operational steps
- validation procedures and BAS implementation details
- local assumptions and known false positives (explicitly labeled)

---

### Rule Providers (authoritative)
Authoritative for:
- the existence of mapped rule references
- rule reference metadata (ID/name/link/status/timestamps if provided)
- mapping provenance (dataset version/hash, provider identity)

Rule providers are NOT authoritative for:
- whether a rule is effective
- whether coverage is “complete”
- whether the organization is actually collecting required telemetry

---

## 2) Conflict resolution rules

1. If MITRE and Company disagree about “what the strategy is about”:
   - MITRE wins for intent; company context must be placed in operational sections (Priority/Response/Validation/Assumptions).

2. If MITRE says telemetry is needed but company profile says telemetry is missing:
   - Both are recorded:
     - “Required by MITRE” + “Telemetry gap in environment”.

3. If a rule provider mapping suggests coverage but company telemetry is missing:
   - The doc must not imply coverage.
   - Show rule reference and explicitly mark telemetry gap.

4. If multiple rule providers disagree:
   - Show both with provenance.
   - Do not choose a winner unless company overlay explicitly selects one.

---

## 3) Prohibited sources of “truth”
- model inference / guessing
- external blog posts or vendor marketing claims (unless linked as non-authoritative reference)
- “common knowledge” assumptions about telemetry, platforms, or tools

---

## 4) Required labeling
Every non-MITRE statement must be labeled as one of:
- Company-provided
- Rule-provider-provided
- Generator-scaffolded (placeholder)
