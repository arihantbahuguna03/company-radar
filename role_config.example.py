"""
role_config.example.py
=======================
Copy → role_config.py and fill in real values.
role_config.py is gitignored — your real role context is not
included in this demo repo.

This is what tells Company Radar what YOU care about.
The same Slack signal is more or less relevant depending on this config.
"""

YOUR_NAME = "Your Name"
YOUR_ROLE = "Product Manager, [Your Pod / Domain]"

# Pods / sub-products you own or closely work with
YOUR_PODS = [
    "Pod Name 1",
    "Pod Name 2",
    # e.g. "International Payments", "CAR Flow", "Domestic Cards"
]

# Teams you directly depend on (high relevance — their signals matter most)
YOUR_DEPENDENCIES = [
    "Engineering - Platform",
    "Engineering - Mobile",
    # add teams whose changes affect your work
]

# Your current active projects (used to detect relevance + goal alignment)
YOUR_CURRENT_PROJECTS = [
    "Project Alpha",   # replace with your real project names
    "Project Beta",
]

# Metrics you own or closely track
YOUR_METRICS = [
    "metric_1",   # e.g. "international success rate", "CAR activation rate"
    "metric_2",
]

# Keywords that flag a signal as relevant to you (beyond team matching)
YOUR_KEYWORDS = [
    "keyword_1",
    "keyword_2",
    # e.g. "international", "tokenization", "checkout", "recurring"
]
