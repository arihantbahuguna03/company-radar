"""
Company Radar — Slack Reader
=============================
Fetches messages from configured team channels.
Demo mode: returns synthetic signals from demo_data.py.
Live mode: uses Slack Web API with a bot token.

Scopes required (Slack app):
  channels:history  — read public channel messages
  groups:history    — read private channel messages (if needed)
  users:read        — resolve user display names

Note: Company Radar NEVER reads DMs. Only public/private channels
that have been explicitly configured in company_config.py.
"""

import os
from datetime import datetime, timedelta

from config import DEMO_MODE, SLACK_LOOKBACK_HOURS


def _load_company_config():
    try:
        from company_config import TEAMS, LEADERSHIP_CHANNELS, COMPLIANCE_CHANNELS, ALL_CHANNELS
        return TEAMS, LEADERSHIP_CHANNELS, COMPLIANCE_CHANNELS, ALL_CHANNELS
    except ImportError:
        from demo_data import DEMO_TEAMS, DEMO_LEADERSHIP_CHANNELS, DEMO_COMPLIANCE_CHANNELS
        all_ch = (
            [c for t in DEMO_TEAMS.values() for c in t["channels"]]
            + DEMO_LEADERSHIP_CHANNELS
            + DEMO_COMPLIANCE_CHANNELS
        )
        return DEMO_TEAMS, DEMO_LEADERSHIP_CHANNELS, DEMO_COMPLIANCE_CHANNELS, all_ch


# ── Normalise ─────────────────────────────────────────────────────────────────

def normalise_message(raw: dict) -> dict:
    return {
        "msg_id":       raw.get("msg_id", raw.get("ts", "")),
        "channel_id":   raw.get("channel_id", ""),
        "channel_name": raw.get("channel_name", ""),
        "team":         raw.get("team", "Unknown"),
        "sender":       raw.get("sender", raw.get("user", "Unknown")),
        "ts":           raw.get("ts", datetime.now().isoformat()),
        "text":         raw.get("text", ""),
        # Filled by signal_extractor.py
        "signal_type":     None,
        "signal_summary":  None,
        "urgency":         None,
        "relevance_score": None,
        "relevance_reason": None,
        "entities":        [],
    }


# ── Demo reader ───────────────────────────────────────────────────────────────

def fetch_demo_messages() -> list[dict]:
    from demo_data import DEMO_MESSAGES
    return [normalise_message(m) for m in DEMO_MESSAGES]


# ── Live reader ───────────────────────────────────────────────────────────────

def fetch_live_messages(lookback_hours: int = SLACK_LOOKBACK_HOURS) -> list[dict]:
    """
    Fetch messages from all configured channels via Slack API.
    Requires SLACK_BOT_TOKEN env var.
    """
    try:
        from slack_sdk import WebClient
    except ImportError:
        raise RuntimeError("slack_sdk not installed. Run: pip install slack-sdk")

    teams, _, _, all_channels = _load_company_config()

    token  = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=token)
    oldest = str((datetime.now() - timedelta(hours=lookback_hours)).timestamp())

    # Build channel → team mapping for normalisation
    ch_to_team = {}
    for team_name, team_data in teams.items():
        for ch in team_data["channels"]:
            ch_to_team[ch] = team_name

    messages = []
    for channel_id in all_channels:
        try:
            history = client.conversations_history(channel=channel_id, oldest=oldest)
            for msg in history.get("messages", []):
                if msg.get("subtype"):
                    continue  # skip system messages
                messages.append(normalise_message({
                    **msg,
                    "channel_id":   channel_id,
                    "channel_name": channel_id,
                    "team":         ch_to_team.get(channel_id, "Unknown"),
                    "sender":       msg.get("user", "Unknown"),
                }))
        except Exception as e:
            print(f"  Warning: could not read channel {channel_id}: {e}")
            continue

    return messages


# ── Public interface ──────────────────────────────────────────────────────────

def fetch_messages(lookback_hours: int = SLACK_LOOKBACK_HOURS) -> list[dict]:
    if DEMO_MODE:
        return fetch_demo_messages()
    return fetch_live_messages(lookback_hours)
