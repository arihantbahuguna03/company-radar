"""
Company Radar — Main Entry Point
==================================
Runs the full pipeline:
  1. Fetch messages from all configured team channels
  2. Extract typed signals (Claude)
  3. Score relevance against your role context
  4. Track new tools built at the company
  5. Map business metric signals to product implications
  6. Detect channel activity anomalies
  7. Extract company goals and map to your projects
  8. Write morning brief or weekly advisory

Run modes:
  python main.py              — morning brief (demo mode)
  python main.py --weekly     — weekly strategic advisor
  python main.py --tools      — show tools database
  python main.py --live       — use live Slack API

Author: demo-owner@demo.com
"""

import argparse
from datetime import datetime

import pytz

from brief_writer import run_brief
from business_pulse import extract_metric_signals, map_implications
from config import DEMO_MODE, SLACK_WEEKLY_LOOKBACK_HOURS
from goal_alignment import extract_goals, map_goals_to_projects
from relevance_scorer import score_all
from rhythm_tracker import detect_anomalies, record_activity
from signal_extractor import extract_signals
from slack_reader import fetch_messages
from tools_tracker import get_relevant_tools, record_all_tools
from weekly_advisor import run_weekly

IST = pytz.timezone("Asia/Kolkata")


def load_role_context() -> dict:
    """Load PM role context — from role_config.py if it exists, else demo context."""
    try:
        import role_config
        return {
            "name":         role_config.YOUR_NAME,
            "role":         role_config.YOUR_ROLE,
            "pods":         role_config.YOUR_PODS,
            "dependencies": role_config.YOUR_DEPENDENCIES,
            "projects":     role_config.YOUR_CURRENT_PROJECTS,
            "metrics":      role_config.YOUR_METRICS,
            "keywords":     role_config.YOUR_KEYWORDS,
        }
    except ImportError:
        from demo_data import DEMO_ROLE
        return DEMO_ROLE


def run_morning_pipeline() -> None:
    role = load_role_context()

    print(f"\n{'='*65}")
    print(f"  COMPANY RADAR — Pipeline starting | {datetime.now(IST).strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode: {'DEMO' if DEMO_MODE else 'LIVE'}")
    print(f"{'='*65}\n")

    # 1. Fetch
    print("📡 Fetching messages from team channels…")
    messages = fetch_messages()
    print(f"   {len(messages)} messages fetched from {len({m['team'] for m in messages})} teams\n")

    # 2. Extract signals (Claude)
    print("🧠 Extracting signals…")
    messages = extract_signals(messages, role)
    by_type  = {}
    for m in messages:
        by_type.setdefault(m.get("signal_type", "unknown"), 0)
        by_type[m.get("signal_type", "unknown")] += 1
    for stype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"   {count}x {stype}")
    print()

    # 3. Score relevance
    print("🎯 Scoring relevance…")
    messages = score_all(messages, role)
    high   = len([m for m in messages if m.get("relevance_label") == "HIGH"])
    medium = len([m for m in messages if m.get("relevance_label") == "MEDIUM"])
    noise  = len([m for m in messages if m.get("relevance_label") == "NOISE"])
    print(f"   {high} HIGH | {medium} MEDIUM | {noise} NOISE\n")

    # 4. Track tools
    print("🔧 Tracking new tools…")
    saved = record_all_tools(messages)
    print(f"   {saved} new tool(s) logged to database\n")

    # 5. Business pulse
    print("📊 Analysing business signals…")
    metric_sigs = extract_metric_signals(messages)
    metric_sigs = map_implications(metric_sigs, role)
    print(f"   {len(metric_sigs)} business signal(s) with implications mapped\n")

    # Merge implications back into messages
    impl_map = {m["msg_id"]: m.get("business_implication") for m in metric_sigs if m.get("business_implication")}
    for m in messages:
        if m["msg_id"] in impl_map:
            m["business_implication"] = impl_map[m["msg_id"]]

    # 6. Rhythm anomalies
    print("📈 Checking channel rhythm…")
    record_activity(messages)
    anomalies = detect_anomalies(messages)
    print(f"   {len(anomalies)} anomaly(ies) detected\n")

    # 7. Goal alignment
    print("🎖️  Checking goal alignment…")
    goal_messages = extract_goals(messages)
    alignment     = map_goals_to_projects(goal_messages, role)
    print(f"   {len(alignment.get('goals', []))} company goal(s) extracted")
    print(f"   {len(alignment.get('alignment', []))} project alignment(s) found\n")

    # 8. Morning brief
    run_brief(messages, anomalies, role, period="morning")

    # Show relevant tools if any new ones
    relevant_tools = get_relevant_tools(limit=3)
    if relevant_tools:
        print("🔵 TOOLS RELEVANT TO YOU:")
        for t in relevant_tools:
            print(f"  • [{t['team']}] {t['name'][:80]}")
        print()


def run_weekly_pipeline() -> None:
    role = load_role_context()

    print(f"\n{'='*65}")
    print(f"  COMPANY RADAR — Weekly pipeline | {datetime.now(IST).strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*65}\n")

    print("📡 Fetching last 7 days of messages…")
    messages = fetch_messages(lookback_hours=SLACK_WEEKLY_LOOKBACK_HOURS)
    print(f"   {len(messages)} messages\n")

    print("🧠 Extracting signals…")
    messages = extract_signals(messages, role)

    print("🎯 Scoring relevance…")
    messages = score_all(messages, role)

    print("📊 Analysing business signals…")
    metric_sigs = extract_metric_signals(messages)
    metric_sigs = map_implications(metric_sigs, role)
    impl_map = {m["msg_id"]: m.get("business_implication") for m in metric_sigs if m.get("business_implication")}
    for m in messages:
        if m["msg_id"] in impl_map:
            m["business_implication"] = impl_map[m["msg_id"]]

    record_activity(messages)
    anomalies = detect_anomalies(messages)

    print("🎖️  Extracting company goals…")
    goal_messages = extract_goals(messages)
    alignment     = map_goals_to_projects(goal_messages, role)

    run_weekly(messages, alignment, anomalies, role)


def show_tools() -> None:
    from tools_tracker import get_all_tools
    tools = get_all_tools(limit=20)
    if not tools:
        print("\nNo tools tracked yet. Run the morning pipeline first.")
        return
    print(f"\n{'='*65}")
    print(f"  COMPANY RADAR — Tools Database ({len(tools)} entries)")
    print(f"{'='*65}\n")
    for t in tools:
        rel = " ★ RELEVANT" if t["is_relevant"] else ""
        print(f"[{t['team']}]{rel}")
        print(f"  {t['name'][:100]}")
        print(f"  #{t['channel_name']} | {t['mentioned_at'][:10]}")
        print()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Company Radar — your personal company intelligence tool")
    parser.add_argument("--weekly", action="store_true", help="Run weekly strategic advisor")
    parser.add_argument("--tools",  action="store_true", help="Show tools database")
    parser.add_argument("--live",   action="store_true", help="Use live Slack API")
    args = parser.parse_args()

    if args.live:
        import config
        config.DEMO_MODE = False

    if args.tools:
        show_tools()
    elif args.weekly:
        run_weekly_pipeline()
    else:
        run_morning_pipeline()
