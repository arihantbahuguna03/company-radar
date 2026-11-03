"""
Company Radar — Tools & Knowledge Tracker
==========================================
Maintains a persistent SQLite database of every tool, dashboard,
script, or automation anyone in the company mentions building.

Classic PM problem: you've been manually pulling a report for 3 months,
and it turns out the data team built that dashboard in January. Nobody told you.

This module solves it permanently. After a few weeks of use, you have
a searchable map of everything that exists internally.

Schema
------
  tools (id, name, description, team, channel, mentioned_at, is_relevant, relevance_reason)
"""

import sqlite3
import uuid
from datetime import datetime

from config import TOOLS_DB_PATH, TOOL_SIGNAL_KEYWORDS


def _conn():
    c = sqlite3.connect(TOOLS_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id              TEXT PRIMARY KEY,
                name            TEXT,
                description     TEXT,
                team            TEXT,
                channel_name    TEXT,
                mentioned_at    TEXT,
                msg_id          TEXT,
                is_relevant     INTEGER DEFAULT 0,
                relevance_reason TEXT
            )
        """)


def _is_tool_signal(msg: dict) -> bool:
    """Return True if this message looks like someone announcing a new tool."""
    if msg.get("signal_type") == "tool_built":
        return True
    text = msg.get("text", "").lower()
    return any(kw in text for kw in TOOL_SIGNAL_KEYWORDS)


def _extract_tool_name(text: str, signal_summary: str) -> str:
    """Best-effort extraction of the tool/dashboard name from the message."""
    # Use signal_summary as the name source — it's already Claude-summarised
    return signal_summary[:120] if signal_summary else text[:80]


def record_tool(msg: dict) -> str | None:
    """
    If this message describes a new tool, persist it to the database.
    Returns the tool id if saved, None if not a tool signal.
    """
    if not _is_tool_signal(msg):
        return None

    tool_id   = str(uuid.uuid4())
    name      = _extract_tool_name(msg.get("text", ""), msg.get("signal_summary", ""))
    init_db()

    with _conn() as c:
        c.execute(
            """INSERT OR IGNORE INTO tools
               (id, name, description, team, channel_name, mentioned_at, msg_id,
                is_relevant, relevance_reason)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                tool_id,
                name,
                msg.get("text", "")[:500],
                msg.get("team", "Unknown"),
                msg.get("channel_name", ""),
                msg.get("ts", datetime.now().isoformat()),
                msg.get("msg_id", ""),
                1 if msg.get("is_relevant") else 0,
                msg.get("relevance_reason", ""),
            ),
        )
    return tool_id


def get_relevant_tools(limit: int = 10) -> list[dict]:
    """Return tools flagged as relevant to the PM, most recent first."""
    init_db()
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM tools WHERE is_relevant = 1 ORDER BY mentioned_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_tools(limit: int = 50) -> list[dict]:
    """Return all tracked tools, most recent first."""
    init_db()
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM tools ORDER BY mentioned_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def search_tools(query: str) -> list[dict]:
    """Full-text search across tool name and description."""
    init_db()
    q = f"%{query.lower()}%"
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM tools WHERE lower(name) LIKE ? OR lower(description) LIKE ? ORDER BY mentioned_at DESC",
            (q, q),
        ).fetchall()
    return [dict(r) for r in rows]


def record_all_tools(messages: list[dict]) -> int:
    """Run record_tool over a batch. Returns count of new tools saved."""
    init_db()
    saved = sum(1 for m in messages if record_tool(m) is not None)
    return saved
