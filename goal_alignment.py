"""
Company Radar — Goal Alignment
================================
Extracts company goals from leadership/all-hands channels and maps them
to the PM's current projects.

Why this matters: PMs often know the company's goals abstractly ("Q2 is
international growth") but don't track how directly their current projects
map to them. This module makes that connection explicit every week.

Two outputs:
  1. Extracted goals — parsed from goal_update signals in leadership channels
  2. Alignment map — how each of the PM's projects connects to a company goal
"""

import anthropic


def extract_goals(messages: list[dict]) -> list[dict]:
    """
    Filter for goal_update signals from leadership/all-hands channels.
    Returns messages that likely contain company goal statements.
    """
    goal_keywords = [
        "goal", "priority", "focus", "target", "objective", "okr",
        "q1", "q2", "q3", "q4", "quarter", "north star", "strategy",
        "all-hands", "all hands",
    ]
    goals = []
    for msg in messages:
        if msg.get("signal_type") == "goal_update":
            goals.append(msg)
            continue
        text = msg.get("text", "").lower()
        ch   = msg.get("channel_name", "").lower()
        if ("all-hands" in ch or "leadership" in ch or "strategy" in ch):
            if any(kw in text for kw in goal_keywords):
                goals.append(msg)
    return goals


def map_goals_to_projects(goal_messages: list[dict], role_context: dict) -> dict:
    """
    Use Claude to map extracted company goals to the PM's current projects.
    Returns:
      {
        "goals": [...extracted goal statements...],
        "alignment": [...{project, goal, alignment_strength, note}...]
      }
    """
    if not goal_messages:
        return {"goals": [], "alignment": []}

    client = anthropic.Anthropic()

    goals_text = "\n\n".join(
        f"[{m.get('channel_name', '?')}] {m.get('text', '')[:400]}"
        for m in goal_messages
    )

    projects = role_context.get("projects", [])
    metrics  = role_context.get("metrics", [])

    prompt = f"""You are a PM advisor. Extract company goals from these messages and map them
to the PM's current projects.

PM's current projects: {', '.join(projects)}
PM's metrics: {', '.join(metrics)}

Leadership/all-hands messages:
{goals_text}

Return JSON:
{{
  "goals": ["<extracted goal 1>", "<extracted goal 2>", ...],
  "alignment": [
    {{
      "project": "<project name>",
      "goal": "<related company goal>",
      "alignment_strength": "direct" | "adjacent" | "none",
      "note": "<one sentence on why>"
    }}
  ]
}}

Only include projects where alignment_strength is "direct" or "adjacent".
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
        return json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        return {"goals": [], "alignment": []}
