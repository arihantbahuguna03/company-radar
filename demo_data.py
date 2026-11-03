"""
Company Radar — Demo Data
==========================
Synthetic Slack signals across multiple teams.
No real company names, channel IDs, or employee data.
Used when DEMO_MODE = True in config.py.
"""

from datetime import datetime, timedelta

_now = datetime.now()
_h   = lambda n: (_now - timedelta(hours=n)).isoformat()

# ── Demo teams and channels ───────────────────────────────────────────────────

DEMO_TEAMS = {
    "Engineering - Platform": {
        "channels": ["C_DEMO_PLATFORM"],
        "watch_level": "high",
    },
    "Engineering - Mobile": {
        "channels": ["C_DEMO_MOBILE"],
        "watch_level": "high",
    },
    "Analytics": {
        "channels": ["C_DEMO_ANALYTICS", "C_DEMO_DATA_ALERTS"],
        "watch_level": "medium",
    },
    "Business": {
        "channels": ["C_DEMO_BUSINESS"],
        "watch_level": "high",
    },
    "Risk & Fraud": {
        "channels": ["C_DEMO_RISK"],
        "watch_level": "high",
    },
    "Design": {
        "channels": ["C_DEMO_DESIGN"],
        "watch_level": "medium",
    },
    "Your Pod": {
        "channels": ["C_DEMO_POD_INTL", "C_DEMO_POD_CAR"],
        "watch_level": "high",
    },
}

DEMO_LEADERSHIP_CHANNELS = ["C_DEMO_ALLHANDS", "C_DEMO_LEADERSHIP"]
DEMO_COMPLIANCE_CHANNELS = ["C_DEMO_LEGAL", "C_DEMO_COMPLIANCE"]

# ── Demo role context ─────────────────────────────────────────────────────────

DEMO_ROLE = {
    "name":         "Demo PM",
    "role":         "Product Manager, International Payments",
    "pods":         ["International Payments", "CAR Flow", "UP Flow"],
    "dependencies": ["Engineering - Platform", "Engineering - Mobile", "Risk & Fraud"],
    "projects":     ["Payment Method Expansion", "Checkout Redesign", "Recurring Payments V2"],
    "metrics":      ["international success rate", "CAR activation rate", "international GMV"],
    "keywords":     ["international", "checkout", "recurring", "tokenization", "card", "payment"],
}

# ── Demo Slack messages (one per channel, covering all signal types) ───────────

DEMO_MESSAGES = [

    # Engineering - Platform: dependency change (high urgency)
    {
        "msg_id":       "DEMO_MSG_001",
        "channel_id":   "C_DEMO_PLATFORM",
        "channel_name": "eng-platform",
        "team":         "Engineering - Platform",
        "sender":       "Demo Engineer 1",
        "ts":           _h(6),
        "text": (
            "Heads up: shipping payment gateway abstraction layer v2 next Tuesday. "
            "Breaking change — any service calling /charge/v1 directly needs to migrate "
            "to /charge/v2 before Tuesday 10am. Reach out if you have questions."
        ),
    },

    # Engineering - Mobile: dependency change affecting checkout
    {
        "msg_id":       "DEMO_MSG_002",
        "channel_id":   "C_DEMO_MOBILE",
        "channel_name": "eng-mobile",
        "team":         "Engineering - Mobile",
        "sender":       "Demo Engineer 2",
        "ts":           _h(10),
        "text": (
            "Android SDK v4.2 ships Friday. Breaking change in deep-link handling — "
            "the checkout intent URI format has changed. Any team that uses "
            "deep-links into checkout needs to update their URI scheme. "
            "Changelog in the usual doc."
        ),
    },

    # Analytics: new tool built (high value for PM)
    {
        "msg_id":       "DEMO_MSG_003",
        "channel_id":   "C_DEMO_ANALYTICS",
        "channel_name": "data-analytics",
        "team":         "Analytics",
        "sender":       "Demo Analyst 1",
        "ts":           _h(18),
        "text": (
            "Published the international payments funnel dashboard — covers "
            "activation cohort, step-by-step drop-off, and weekly SR trends "
            "broken down by card type and geography. Link in the thread. "
            "Happy to add more filters if teams need them."
        ),
    },

    # Analytics: metric alert
    {
        "msg_id":       "DEMO_MSG_004",
        "channel_id":   "C_DEMO_DATA_ALERTS",
        "channel_name": "data-alerts",
        "team":         "Analytics",
        "sender":       "Demo Analyst 2",
        "ts":           _h(4),
        "text": (
            "ALERT: International GMV down 14% WoW as of yesterday. "
            "CAR activation rate also down ~8%. Both started dropping "
            "around Tuesday. Flagging for the relevant PMs."
        ),
    },

    # Business: strategic signal
    {
        "msg_id":       "DEMO_MSG_005",
        "channel_id":   "C_DEMO_BUSINESS",
        "channel_name": "business-weekly",
        "team":         "Business",
        "sender":       "Demo Business Lead",
        "ts":           _h(22),
        "text": (
            "Weekly business update: international revenue missed target by 11%. "
            "Enterprise pipeline is healthy but several deals are blocked on "
            "international payment method availability. This is now a Q2 blocker "
            "for enterprise acquisition. Escalating to leadership."
        ),
    },

    # Risk & Fraud: incident (immediate urgency)
    {
        "msg_id":       "DEMO_MSG_006",
        "channel_id":   "C_DEMO_RISK",
        "channel_name": "risk-ops",
        "team":         "Risk & Fraud",
        "sender":       "Demo Risk Lead",
        "ts":           _h(3),
        "text": (
            "Seeing a fraud spike in international card transactions over last 6 hours. "
            "Potential 3DS bypass vector — investigating. Temporarily increasing "
            "friction on international card auth while we root cause. "
            "Will update in 2 hours."
        ),
    },

    # Design: new component with breaking changes
    {
        "msg_id":       "DEMO_MSG_007",
        "channel_id":   "C_DEMO_DESIGN",
        "channel_name": "design-system",
        "team":         "Design",
        "sender":       "Demo Designer 1",
        "ts":           _h(30),
        "text": (
            "Design system v3 is live. Breaking changes to form input components — "
            "the checkout form uses the old pattern. Tagging PM team: please "
            "coordinate with your eng to update before the next checkout release "
            "or the UI will regress."
        ),
    },

    # Leadership: goal alignment signal
    {
        "msg_id":       "DEMO_MSG_008",
        "channel_id":   "C_DEMO_ALLHANDS",
        "channel_name": "all-hands-updates",
        "team":         "Leadership",
        "sender":       "Demo CEO",
        "ts":           _h(48),
        "text": (
            "Q2 priorities confirmed: (1) International expansion — target 25% of GMV "
            "from international by end of Q2. (2) Enterprise acquisition — close 10 "
            "enterprise deals. (3) Platform reliability — 99.9% uptime. "
            "International payments is our #1 growth lever this quarter."
        ),
    },

    # Leadership: decision without PM in the room
    {
        "msg_id":       "DEMO_MSG_009",
        "channel_id":   "C_DEMO_LEADERSHIP",
        "channel_name": "leadership-decisions",
        "team":         "Leadership",
        "sender":       "Demo VP Product",
        "ts":           _h(14),
        "text": (
            "Decided in today's leadership sync: we're pausing new international "
            "payment method launches until the fraud spike is resolved. "
            "Existing flows continue. New market expansions on hold. "
            "Affected PMs — please reprioritize accordingly."
        ),
    },

    # Compliance: regulatory signal (immediate)
    {
        "msg_id":       "DEMO_MSG_010",
        "channel_id":   "C_DEMO_COMPLIANCE",
        "channel_name": "compliance-updates",
        "team":         "Compliance",
        "sender":       "Demo Legal Lead",
        "ts":           _h(36),
        "text": (
            "New regulatory circular published: all recurring international card "
            "transactions above a certain threshold require additional authentication "
            "from Dec 1. 90-day compliance window. Products using recurring "
            "international flows need to assess impact and plan updates. "
            "Reach out if you need a legal review session."
        ),
    },

    # Pod channel: user research finding
    {
        "msg_id":       "DEMO_MSG_011",
        "channel_id":   "C_DEMO_POD_INTL",
        "channel_name": "pod-international",
        "team":         "Your Pod",
        "sender":       "Demo UX Researcher",
        "ts":           _h(20),
        "text": (
            "Sharing findings from last week's international user research (12 sessions). "
            "Top finding: 60% of users abandon at the card details step — "
            "primary reason is unfamiliar authentication UX (3DS popup). "
            "Secondary: currency confusion when price displayed in USD not local currency. "
            "Full report in Notion."
        ),
    },

    # Pod channel: cross-team ask
    {
        "msg_id":       "DEMO_MSG_012",
        "channel_id":   "C_DEMO_POD_CAR",
        "channel_name": "pod-car",
        "team":         "Your Pod",
        "sender":       "Demo PM 2",
        "ts":           _h(8),
        "text": (
            "CAR team is running an experiment on the activation flow next week. "
            "Want to make sure it doesn't conflict with the checkout redesign "
            "the international PM team has in progress. Can we sync? "
            "Potentially the same step in the funnel."
        ),
    },
]
