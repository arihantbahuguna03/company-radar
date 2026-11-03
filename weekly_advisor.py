"""
Company Radar — Weekly Advisor
================================
Every Monday morning, synthesises the week's signals into a strategic brief:
  - What the company's biggest signal is
  - How it connects to the PM's work
  - A recommended priority order for the week
  - Goal alignment update (how your projects map to company goals)
  - Knowledge gaps detected this week

This is the output that makes Company Radar a PM tool, not just a monitor.
"""

from datetime import datetime

import anthropic
import pytz

IST = pytz.timezone("Asia/Kolkata")


def generate_weekly_brief(
    messages:       list[dict],
    goal_alignment: dict,
    anomalies:      list[dict],
    role_context:   dict,
) -> str:
    client = anthropic.Anthropic()

    # Collect high-relevance signals from the week
    top_signals = [
        m for m in messages
        if m.get("relevance_score", 0) >= 30
    ]
    top_signals.sort(key=lambda m: m.get("relevance_score", 0), reverse=True)

    signals_text = "\n".join(
        f"- [{m.get('signal_type','?')} | {m.get('team','?')}] "
        f"{m.get('signal_summary') or m.get('text','')[:120]}"
        + (f"\n  Implication: {m['business_implication']}" if m.get("business_implication") else "")
        for m in top_signals[:12]
    ) or "  (no high-relevance signals this week)"

    goals_text = "\n".join(
        f"- {a['project']}: {a['note']} (alignment: {a['alignment_strength']})"
        for a in goal_alignment.get("alignment", [])
    ) or "  (no goal alignment data)"

    company_goals = "; ".join(goal_alignment.get("goals", [])) or "not extracted this week"

    anomaly_text = "\n".join(f"- {a['note']}" for a in anomalies) or "  (none)"

    prompt = f"""You are {role_context.get('name', 'the PM')}'s Company Radar — weekly strategic advisor.
Write a Monday morning priority brief. Role: {role_context.get('role', 'PM')}.
Current projects: {', '.join(role_context.get('projects', []))}.

Company goals extracted this week: {company_goals}

High-relevance signals from the week:
{signals_text}

Project goal alignment:
{goals_text}

Channel anomalies:
{anomaly_text}

Write the weekly brief in this format:
1. Company pulse this week (2 sentences — what was the dominant signal?)
2. How it affects YOUR work (1–2 sentences)
3. Recommended priority order for this week (numbered, 3–4 items max, each with a "why" in 10 words)
4. Goal alignment snapshot — which of your projects maps to the company's stated goals
5. One knowledge gap worth closing this week (a topic the company discussed that you haven't engaged with)

Keep under 350 words. Be a trusted advisor, not a report generator.
Speak directly — "your tokenization project" not "the PM's tokenization project"."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def run_weekly(
    messages:       list[dict],
    goal_alignment: dict,
    anomalies:      list[dict],
    role_context:   dict,
) -> str:
    now = datetime.now(IST).strftime("%b %d, %Y")
    print(f"\n{'='*65}")
    print(f"  COMPANY RADAR — WEEKLY ADVISOR | Week of {now}")
    print(f"{'='*65}\n")

    brief = generate_weekly_brief(messages, goal_alignment, anomalies, role_context)
    print(brief)
    print()
    return brief
