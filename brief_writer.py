"""
Company Radar — Morning Brief Writer
======================================
Uses Claude to write a sharp, actionable morning brief from the day's signals.

Output structure:
  🔴 Act on this now    (immediate urgency, high relevance)
  🟡 Good to know      (daily urgency, medium/high relevance)
  🔵 Tools & knowledge (new tools built that you can use)
  ⚪ Noise filtered    (count of low-relevance signals skipped)
  📊 Business pulse    (metric movements + implications)
  ⚠️  Anomalies        (channels behaving unusually)
"""

from datetime import datetime

import anthropic
import pytz

IST = pytz.timezone("Asia/Kolkata")


def _format_signals_for_prompt(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        lines.append(
            f"[{m.get('relevance_label','?')} | {m.get('signal_type','?')} | "
            f"{m.get('team','?')}] {m.get('signal_summary') or m.get('text','')[:120]}"
        )
        if m.get("relevance_reason"):
            lines.append(f"  → Relevant because: {m['relevance_reason']}")
        if m.get("business_implication"):
            lines.append(f"  → Implication: {m['business_implication']}")
    return "\n".join(lines)


def generate_brief(
    messages:     list[dict],
    anomalies:    list[dict],
    role_context: dict,
    period:       str = "morning",
) -> str:
    """
    Write the morning brief. Claude synthesises all signals into one
    actionable brief — not a bullet dump, a real brief.
    """
    client = anthropic.Anthropic()
    now    = datetime.now(IST).strftime("%b %d, %Y %H:%M")

    immediate = [m for m in messages if m.get("urgency") == "immediate" and m.get("relevance_score", 0) >= 30]
    daily     = [m for m in messages if m.get("urgency") == "daily"     and m.get("relevance_score", 0) >= 30]
    tools     = [m for m in messages if m.get("signal_type") == "tool_built"]
    noise_ct  = len([m for m in messages if m.get("relevance_score", 0) < 15])

    immediate_text = _format_signals_for_prompt(immediate) or "  (none)"
    daily_text     = _format_signals_for_prompt(daily)     or "  (none)"
    tools_text     = _format_signals_for_prompt(tools)     or "  (none)"
    anomaly_text   = "\n".join(a["note"] for a in anomalies) or "  (none)"

    prompt = f"""You are {role_context.get('name', 'the PM')}'s Company Radar — a personal company intelligence tool.
Write a sharp {period} brief. Role: {role_context.get('role', 'PM')}.

Format:
1. One-line situation summary (e.g. "2 items need action today, 1 is a compliance deadline")
2. 🔴 ACT ON THIS — immediate signals, what to do
3. 🟡 GOOD TO KNOW — daily signals, no action required
4. 🔵 NEW TOOLS — things built that you can use
5. 📊 BUSINESS PULSE — metric movements + their implication for your work
6. ⚠️  ANOMALIES — {len(anomalies)} channel(s) behaving unusually

Signals that need action today:
{immediate_text}

Good to know:
{daily_text}

New tools/dashboards built:
{tools_text}

Channel anomalies:
{anomaly_text}

Rules:
- Be direct. No padding. Write as if briefing a busy PM who has 60 seconds.
- For each ACT ON THIS item: name the signal, the team it came from, and the one action to take.
- For tools: name what it does and why it's relevant.
- Keep under 300 words.
- Noise filtered: {noise_ct} low-relevance signals skipped."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def run_brief(
    messages:     list[dict],
    anomalies:    list[dict],
    role_context: dict,
    period:       str = "morning",
) -> str:
    now = datetime.now(IST).strftime("%b %d, %Y %H:%M")
    print(f"\n{'='*65}")
    print(f"  COMPANY RADAR — {period.upper()} BRIEF | {now}")
    print(f"{'='*65}\n")

    brief = generate_brief(messages, anomalies, role_context, period)
    print(brief)
    print()
    return brief
