"""
Company Radar — Global Settings
================================
Tune thresholds and schedules here. No sensitive data in this file.
Team names, channel IDs, and role context live in company_config.py
and role_config.py (both gitignored — see *.example.py for structure).
"""

# ── Demo mode ─────────────────────────────────────────────────────────────────
DEMO_MODE = True   # False = live Slack API

# ── Brief schedule ────────────────────────────────────────────────────────────
MORNING_BRIEF_HOUR = 8    # 8am daily
WEEKLY_ADVISOR_DAY = "Monday"

# ── Relevance scoring weights (must sum to 100) ───────────────────────────────
RELEVANCE_WEIGHTS = {
    "direct_dependency": 35,   # signal mentions a team you depend on
    "your_metric":       25,   # signal mentions a metric you own
    "your_project":      20,   # signal mentions your current project area
    "adjacent_team":     12,   # signal from a team that works near yours
    "company_wide":       8,   # company-level signal (all-hands, leadership)
}

# ── Signal type priorities ────────────────────────────────────────────────────
# Routing table: which signal types demand immediate attention vs. weekly digest
SIGNAL_URGENCY = {
    "compliance_regulatory": "immediate",
    "incident_outage":       "immediate",
    "decision_without_me":   "immediate",
    "tool_built":            "daily_brief",
    "business_metric":       "daily_brief",
    "user_research":         "daily_brief",
    "dependency_change":     "daily_brief",
    "goal_update":           "weekly",
    "general_update":        "weekly",
}

# ── Rhythm tracker ────────────────────────────────────────────────────────────
# A channel is "anomalously active" if its message count exceeds its 4-week
# rolling average by this multiplier.
RHYTHM_ANOMALY_MULTIPLIER = 2.5

# A channel is "anomalously quiet" if its count drops below this fraction.
RHYTHM_QUIET_FRACTION = 0.3

# ── Tools tracker ─────────────────────────────────────────────────────────────
TOOLS_DB_PATH = "/tmp/company_radar_tools.db"

# Keywords that suggest someone built something worth tracking
TOOL_SIGNAL_KEYWORDS = [
    "dashboard", "script", "tool", "automation", "pipeline",
    "report", "query", "model", "analysis", "framework",
    "built", "shipped", "launched", "released", "deployed",
    "published", "created", "set up",
]

# ── Knowledge gap ─────────────────────────────────────────────────────────────
# A topic is a "knowledge gap" if it appears this many times across channels
# without you engaging with it.
KNOWLEDGE_GAP_MIN_MENTIONS = 4

# ── Slack API ─────────────────────────────────────────────────────────────────
SLACK_LOOKBACK_HOURS = 24   # morning brief: last 24h
SLACK_WEEKLY_LOOKBACK_HOURS = 168  # weekly advisor: last 7 days
