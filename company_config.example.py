"""
company_config.example.py
==========================
Copy → company_config.py and fill in real values.
company_config.py is gitignored — real team names and channel IDs
are not included in this demo repo.

Structure
---------
TEAMS maps a logical team name to:
  - channels: list of Slack channel IDs to monitor for that team
  - watch_level: "high" (direct dependency), "medium" (adjacent), "low" (FYI)

LEADERSHIP_CHANNELS: channels where strategy/goals are discussed.
COMPLIANCE_CHANNELS: channels for legal, regulatory, policy updates.
"""

TEAMS = {
    "Engineering - Platform": {
        "channels": ["C_YOUR_CHANNEL_ID"],
        "watch_level": "high",   # you depend on platform APIs
    },
    "Engineering - Mobile": {
        "channels": ["C_YOUR_CHANNEL_ID"],
        "watch_level": "high",
    },
    "Analytics": {
        "channels": ["C_YOUR_CHANNEL_ID", "C_YOUR_CHANNEL_ID_2"],
        "watch_level": "medium",
    },
    "Business": {
        "channels": ["C_YOUR_CHANNEL_ID"],
        "watch_level": "high",   # business metrics drive your priorities
    },
    "Risk & Fraud": {
        "channels": ["C_YOUR_CHANNEL_ID"],
        "watch_level": "high",
    },
    "Design": {
        "channels": ["C_YOUR_CHANNEL_ID"],
        "watch_level": "medium",
    },
    "Your Pod": {
        "channels": ["C_YOUR_CHANNEL_ID", "C_YOUR_CHANNEL_ID_2"],
        "watch_level": "high",
    },
    # Add more teams as needed
}

LEADERSHIP_CHANNELS = ["C_ALL_HANDS_CHANNEL", "C_LEADERSHIP_CHANNEL"]
COMPLIANCE_CHANNELS = ["C_LEGAL_CHANNEL", "C_COMPLIANCE_CHANNEL"]

# All channels to scan (auto-built from TEAMS + above)
ALL_CHANNELS = (
    [c for t in TEAMS.values() for c in t["channels"]]
    + LEADERSHIP_CHANNELS
    + COMPLIANCE_CHANNELS
)
