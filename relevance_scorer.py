"""
Company Radar — Relevance Scorer
==================================
Scores each signal 0–100 against the PM's role context.
Claude already flags is_relevant in signal_extractor.py, but
this scorer adds a numeric score + label for ranking and filtering.

Score breakdown (weights from config.py RELEVANCE_WEIGHTS):
  direct_dependency  35  — signal is from/about a team you depend on
  your_metric        25  — a metric you own is mentioned
  your_project       20  — your current project area is mentioned
  adjacent_team      12  — signal from a team that works near yours
  company_wide        8  — leadership / all-hands signal
"""

from config import RELEVANCE_WEIGHTS


def _keyword_hit(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def score_signal(msg: dict, role_context: dict) -> dict:
    """
    Compute relevance score for one message.
    Adds score, score_label, and score_reasons to the message dict.
    Returns the enriched dict.
    """
    text        = (msg.get("text", "") + " " + msg.get("signal_summary", "")).lower()
    team        = msg.get("team", "")
    signal_type = msg.get("signal_type", "general_update")
    entities    = [e.lower() for e in msg.get("entities", [])]

    score   = 0
    reasons = []

    # 1. Direct dependency check
    deps = [d.lower() for d in role_context.get("dependencies", [])]
    if team.lower() in deps or any(d in text for d in deps):
        score += RELEVANCE_WEIGHTS["direct_dependency"]
        reasons.append("from a direct dependency team")

    # 2. Your metric mentioned
    metrics = [m.lower() for m in role_context.get("metrics", [])]
    if _keyword_hit(text, metrics) or any(m in entities for m in metrics):
        score += RELEVANCE_WEIGHTS["your_metric"]
        reasons.append("mentions a metric you own")

    # 3. Your project area mentioned
    projects = [p.lower() for p in role_context.get("projects", [])]
    keywords = [k.lower() for k in role_context.get("keywords", [])]
    if _keyword_hit(text, projects + keywords):
        score += RELEVANCE_WEIGHTS["your_project"]
        reasons.append("touches your project area")

    # 4. Adjacent team (same broad area, not a direct dep)
    pods = [p.lower() for p in role_context.get("pods", [])]
    if _keyword_hit(text, pods):
        score += RELEVANCE_WEIGHTS["adjacent_team"]
        reasons.append("mentions your pod area")

    # 5. Company-wide signal (leadership / all-hands)
    company_wide_types = {"goal_update", "compliance_regulatory"}
    if signal_type in company_wide_types:
        score += RELEVANCE_WEIGHTS["company_wide"]
        reasons.append("company-wide signal")

    # Compliance and incidents always get a floor score
    if signal_type in {"compliance_regulatory", "incident_outage"}:
        score = max(score, 60)
        if "compliance/incident floor" not in reasons:
            reasons.append("compliance or incident — minimum threshold applied")

    # Claude already determined is_relevant — boost if it agrees
    if msg.get("is_relevant"):
        score = min(100, score + 10)

    # Label
    if score >= 70:
        label = "HIGH"
    elif score >= 40:
        label = "MEDIUM"
    elif score >= 15:
        label = "LOW"
    else:
        label = "NOISE"

    msg["relevance_score"]  = score
    msg["relevance_label"]  = label
    msg["relevance_reason"] = (
        msg.get("relevance_reason") or
        ("; ".join(reasons) if reasons else "no direct match to your context")
    )
    return msg


def score_all(messages: list[dict], role_context: dict) -> list[dict]:
    """Score and rank all messages. Returns sorted by relevance descending."""
    scored = [score_signal(m, role_context) for m in messages]
    return sorted(scored, key=lambda m: m.get("relevance_score", 0), reverse=True)
