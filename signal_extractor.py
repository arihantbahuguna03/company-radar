"""
Company Radar — Signal Extractor
==================================
Uses Claude to extract typed signals from each Slack message.
A "signal" is not a summary — it is a classified, actionable piece
of information with a type, urgency, and list of entities mentioned.

Signal types
------------
  tool_built           — someone built/shipped a tool, dashboard, script
  decision_without_me  — a decision was made that may affect your work
  business_metric      — a metric was mentioned (positive or negative)
  compliance_regulatory — legal, regulatory, policy update
  incident_outage      — system failure or active incident
  dependency_change    — a team you depend on is making a breaking change
  user_research        — user interview or research finding shared
  goal_update          — company or team goal announced or changed
  cross_team_ask       — someone is asking for coordination across teams
  general_update       — informational, no action needed
"""

import anthropic

from config import SIGNAL_URGENCY


def _build_extraction_prompt(messages: list[dict], role_context: dict) -> str:
    role_summary = (
        f"Role: {role_context.get('role', 'PM')}\n"
        f"Projects: {', '.join(role_context.get('projects', []))}\n"
        f"Metrics I own: {', '.join(role_context.get('metrics', []))}\n"
        f"Keywords relevant to me: {', '.join(role_context.get('keywords', []))}"
    )

    messages_text = "\n\n".join(
        f"[{m['team']} / #{m['channel_name']}] {m['sender']}:\n{m['text']}"
        for m in messages
    )

    return f"""You are a signal extractor for a PM's company intelligence tool.

This PM's context:
{role_summary}

For each Slack message below, extract a structured signal. Return a JSON array — one object per message — with these fields:
  msg_id: (copy from input)
  signal_type: one of [tool_built, decision_without_me, business_metric, compliance_regulatory, incident_outage, dependency_change, user_research, goal_update, cross_team_ask, general_update]
  signal_summary: one sentence — what happened, plain English, no jargon
  urgency: "immediate" | "daily" | "weekly" | "skip"
  entities: list of things mentioned (team names, project names, metric names, tool names)
  is_relevant_to_pm: true/false — does this affect the PM's work, projects, or metrics?
  relevance_reason: one sentence explaining why it is or isn't relevant (only when is_relevant_to_pm is true)

Rules:
- Be precise with signal_type — don't use general_update if a more specific type fits
- urgency "immediate" = needs action today; "daily" = morning brief; "weekly" = weekly digest; "skip" = pure noise
- For compliance_regulatory and incident_outage, always use urgency "immediate"
- is_relevant_to_pm should be true if the message mentions the PM's projects, metrics, keywords, or direct dependencies

Messages:
{messages_text}

Return only valid JSON — a JSON array, no prose before or after."""


def extract_signals(messages: list[dict], role_context: dict) -> list[dict]:
    """
    Run Claude over a batch of messages and extract typed signals.
    Attaches signal fields back onto each message dict in-place.
    Returns the enriched messages list.
    """
    if not messages:
        return messages

    client = anthropic.Anthropic()

    prompt = _build_extraction_prompt(messages, role_context)

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        signals = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        print("  Warning: could not parse signal extraction response")
        return messages

    # Index by msg_id for O(1) merge
    signal_map = {s["msg_id"]: s for s in signals if "msg_id" in s}

    for msg in messages:
        sig = signal_map.get(msg["msg_id"])
        if not sig:
            continue
        msg["signal_type"]      = sig.get("signal_type", "general_update")
        msg["signal_summary"]   = sig.get("signal_summary", "")
        msg["urgency"]          = sig.get("urgency", "weekly")
        msg["entities"]         = sig.get("entities", [])
        msg["is_relevant"]      = sig.get("is_relevant_to_pm", False)
        msg["relevance_reason"] = sig.get("relevance_reason", "")

    return messages
