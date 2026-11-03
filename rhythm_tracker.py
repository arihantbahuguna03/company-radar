"""
Company Radar — Rhythm Tracker
================================
Learns the company's operating cadence and detects anomalies.

Two things it does:
  1. Anomaly detection — flags channels that are unusually active or
     unusually quiet compared to their rolling average
  2. Cadence context — adds interpretive context to the morning brief
     ("end of quarter" / "post-launch week" / "incident response mode")

State is stored in SQLite so anomaly detection improves over time.

Schema
------
  channel_activity (channel_id, week_start, message_count)
"""

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

from config import RHYTHM_ANOMALY_MULTIPLIER, RHYTHM_QUIET_FRACTION, TOOLS_DB_PATH

_RHYTHM_DB = TOOLS_DB_PATH.replace("tools", "rhythm")


def _conn():
    c = sqlite3.connect(_RHYTHM_DB)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS channel_activity (
                channel_id   TEXT,
                week_start   TEXT,
                message_count INTEGER,
                PRIMARY KEY (channel_id, week_start)
            )
        """)


def record_activity(messages: list[dict]) -> None:
    """Record this batch's message counts per channel for the current week."""
    init_db()
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    counts: dict[str, int] = defaultdict(int)
    for msg in messages:
        counts[msg.get("channel_id", "unknown")] += 1

    with _conn() as c:
        for ch_id, count in counts.items():
            c.execute(
                """INSERT INTO channel_activity (channel_id, week_start, message_count)
                   VALUES (?, ?, ?)
                   ON CONFLICT(channel_id, week_start)
                   DO UPDATE SET message_count = message_count + excluded.message_count""",
                (ch_id, week_start, count),
            )


def detect_anomalies(messages: list[dict]) -> list[dict]:
    """
    Compare current message counts per channel against 4-week rolling average.
    Returns a list of anomaly dicts: {channel, type, current, average, ratio, note}
    """
    init_db()
    current_counts: dict[str, int] = defaultdict(int)
    channel_names: dict[str, str]  = {}

    for msg in messages:
        ch_id = msg.get("channel_id", "unknown")
        current_counts[ch_id] += 1
        channel_names[ch_id]   = msg.get("channel_name", ch_id)

    # 4-week rolling average (exclude current week)
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    with _conn() as c:
        rows = c.execute(
            "SELECT channel_id, AVG(message_count) as avg_count "
            "FROM channel_activity "
            "WHERE week_start < ? "
            "GROUP BY channel_id",
            (week_start,),
        ).fetchall()

    averages = {r["channel_id"]: r["avg_count"] for r in rows}
    anomalies = []

    for ch_id, current in current_counts.items():
        avg = averages.get(ch_id)
        if avg is None or avg < 3:
            continue  # not enough history

        ratio = current / avg
        ch_name = channel_names.get(ch_id, ch_id)

        if ratio >= RHYTHM_ANOMALY_MULTIPLIER:
            anomalies.append({
                "channel":  ch_name,
                "type":     "unusually_active",
                "current":  current,
                "average":  round(avg, 1),
                "ratio":    round(ratio, 1),
                "note": (
                    f"#{ch_name} is {round(ratio, 1)}x its usual activity "
                    f"({current} messages vs avg {round(avg, 1)}). "
                    "Something significant may be happening there."
                ),
            })
        elif ratio <= RHYTHM_QUIET_FRACTION and current < 3:
            anomalies.append({
                "channel":  ch_name,
                "type":     "unusually_quiet",
                "current":  current,
                "average":  round(avg, 1),
                "ratio":    round(ratio, 1),
                "note": (
                    f"#{ch_name} is unusually quiet "
                    f"({current} messages vs avg {round(avg, 1)}). "
                    "Team may be in deep work, incident response, or offline."
                ),
            })

    return anomalies
