"""
Company Radar — Business Pulse
================================
Extracts business metric signals and maps them to product implications.

This is the module that separates "company monitor" from "PM intelligence tool."
It doesn't just report that a metric dropped — it asks: given what the PM is
currently working on, what does this movement mean for their priorities?

Two layers:
  1. Metric extraction — pull any metric mention from a message (direction, magnitude)
  2. Implication mapping — Claude reasons about what this means for the PM's work
"""

import anthropic

from config import SIGNAL_URGENCY


def extract_metric_signals(messages: list[dict]) -> list[dict]:
    """
    Filter messages that contain business metric mentions.
    Returns messages where signal_type == 'business_metric' or
    the text contains metric-like language.
    """
    metric_keywords = [
        "down", "up", "dropped", "increased", "decreased", "growth",
        "decline", "spike", "miss", "beat", "target", "gmv", "revenue",
        "activation", "retention", "churn", "conversion", "%", "percent",
        "week over week", "wow", "mom", "month over month", "quarter",
    ]
    signals = []
    for msg in messages:
        if msg.get("signal_type") == "business_metric":
            signals.append(msg)
            continue
        text = msg.get("text", "").lower()
        if sum(1 for kw in metric_keywords if kw in text) >= 2:
            signals.append(msg)
    return signals


def map_implications(metric_signals: list[dict], role_context: dict) -> list[dict]:
    """
    For each relevant business metric signal, use Claude to reason about
    what this movement means for the PM's current projects and priorities.

    Returns only signals where relevance_score >= 30 (non-noise).
    Adds 'business_implication' field to each.
    """
    relevant = [m for m in metric_signals if m.get("relevance_score", 0) >= 30]
    if not relevant:
        return []

    client = anthropic.Anthropic()

    role_summary = (
        f"Role: {role_context.get('role', 'PM')}\n"
        f"Current projects: {', '.join(role_context.get('projects', []))}\n"
        f"Metrics I own: {', '.join(role_context.get('metrics', []))}\n"
        f"My pods: {', '.join(role_context.get('pods', []))}"
    )

    signals_text = "\n\n".join(
        f"Signal {i+1} [{m.get('team', '?')}]: {m.get('text', '')[:300]}"
        for i, m in enumerate(relevant)
    )

    prompt = f"""You are a PM advisor. Given these business signals and this PM's context,
write a one-sentence product implication for each signal — what does this movement
mean for the PM's priorities or current work?

PM Context:
{role_summary}

Signals:
{signals_text}

Return a JSON array with one object per signal, in the same order:
  [{{"implication": "..."}}]

Be specific. If a metric drop overlaps with a recent launch, name the overlap.
If a metric movement affects a specific project, name it.
If there's no direct implication, say "No direct impact on current projects."
Return only valid JSON."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        implications = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        return relevant

    for i, sig in enumerate(relevant):
        if i < len(implications):
            sig["business_implication"] = implications[i].get("implication", "")

    return relevant
