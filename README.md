# Company Radar

> Personal company intelligence tool for product managers — reads the pulse of every team so you don't miss what matters.

Built Aug 2024–Aug 2025 using Claude 3.5 Sonnet API directly — before MCP and modern agentic tooling existed in production-ready form.

---

## The Problem

A PM at a fast-growing startup is simultaneously the person most responsible for connecting dots across the company *and* the person least likely to be in every channel where those dots are dropped.

In a single day:
- Engineering quietly ships a breaking API change that affects your feature
- Analytics posts a funnel metric that just tanked
- Leadership drops a decision in a channel you don't monitor
- Compliance drops a regulatory deadline that touches your roadmap
- A cross-functional team builds a dashboard you've been planning to build yourself

By the time you hear about any of it — if you hear about it — you're reacting, not leading.

**Company Radar** solves this by reading every team's Slack channels every morning and synthesising a single, relevance-ranked brief that tells you exactly what you need to know.

---

## What It Does

### Signal Extraction
Reads messages from configured team channels (Engineering, Analytics, Business, Risk, Design, Leadership, Product pods) and uses Claude to classify each message into one of nine typed signals:

| Signal type | What it catches |
|---|---|
| `tool_built` | New dashboards, scripts, automations |
| `decision_without_me` | Leadership or cross-team decisions that affect your work |
| `business_metric` | GMV, conversion, activation, revenue movements |
| `compliance_regulatory` | Regulatory deadlines, policy changes |
| `incident_outage` | System incidents, fraud spikes, P0s |
| `dependency_change` | API breaking changes, platform migrations |
| `user_research` | New user findings from UX, research, sales |
| `goal_update` | Company/team goal changes or new OKRs |
| `cross_team_ask` | Coordination requests from other teams |

### Relevance Scoring
Every signal is scored 0–100 against your role context (your current projects, metrics you own, teams you depend on). Signals are labelled **HIGH / MEDIUM / LOW / NOISE**. Compliance and incident signals get a relevance floor of 60 — you always hear about these.

Scoring weights (configurable):

| Dimension | Default weight |
|---|---|
| Direct dependency | 35 |
| Your metric | 25 |
| Your project | 20 |
| Adjacent team | 12 |
| Company-wide | 8 |

### Morning Brief
Claude synthesises the day's signals into one brief (under 300 words):
- 🔴 **Act on this** — immediate signals that need a response today
- 🟡 **Good to know** — daily signals, awareness only
- 🔵 **New tools** — things built across the company you can use
- 📊 **Business pulse** — metric movements + one-sentence product implication
- ⚠️  **Anomalies** — channels that went unusually quiet or unusually loud

### Weekly Strategic Advisor
Every Monday, a deeper brief:
- Company pulse (dominant theme of the week)
- How it affects your work
- Recommended priority order for the week (with "why" for each)
- Goal alignment snapshot (which of your projects maps to stated company goals)
- One knowledge gap worth closing

### Tools Database
Tracks every tool, dashboard, or script built across the company in a local SQLite database. Over time, surfaces relevant tooling you can reuse or coordinate around instead of duplicating work.

### Rhythm Anomaly Detection
Maintains a rolling 4-week baseline of channel activity per time-of-day. Flags channels that are 2.5x more active (something unusual is happening) or 70% quieter than usual (team may be in incident mode or offline-coordinating).

### Business Pulse → Product Implication
For every metric movement, Claude generates a one-sentence product implication — *"International checkout funnel dropped 14% WoW → your international payments launch timeline is at risk"* — so you don't have to do that translation yourself.

### Goal Alignment Mapping
Extracts goal statements from leadership and all-hands channels, maps them to your current projects, and shows you which of your projects is most company-strategic right now.

---

## Architecture

```
main.py                    — CLI entry point (--brief / --weekly / --tools / --live)
│
├── slack_reader.py        — Fetch messages from team channels (demo or live Slack)
├── signal_extractor.py    — Claude: classify each message into a typed signal
├── relevance_scorer.py    — Score 0–100 against PM's role context
│
├── tools_tracker.py       — SQLite: persist and search tool_built signals
├── business_pulse.py      — Extract metric signals → generate product implications
├── rhythm_tracker.py      — SQLite: channel activity baseline + anomaly detection
├── goal_alignment.py      — Extract goals → map to PM's current projects
│
├── brief_writer.py        — Claude: synthesise morning brief from all signals
├── weekly_advisor.py      — Claude: synthesise weekly strategic brief
│
├── config.py              — Tunable weights, thresholds, DB paths, mode flag
├── demo_data.py           — 12 synthetic signals across 8 teams (demo mode)
│
├── company_config.example.py  — Structure for team/channel config (gitignored)
└── role_config.example.py     — Structure for PM role context (gitignored)
```

**All Claude calls use the raw Anthropic SDK** (`claude-3-5-sonnet-20241022`). No LangChain, no agent frameworks. Each call is purpose-built — the signal extractor batches messages in one call, the brief writer synthesises in one call.

---

## Sanitisation Note

`company_config.py` and `role_config.py` are gitignored — they contain real team names, channel IDs, and project names from the company where this was used. The repo ships `.example.py` versions showing the full structure. All analysis logic (signal extraction, scoring, brief writing, anomaly detection) is fully visible.

---

## Configuration

**1. Clone and install**
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key
```

**2. Configure your company's channels**
```bash
cp company_config.example.py company_config.py
# Edit company_config.py: add your Slack workspace token, team names, channel IDs
```

**3. Configure your role context**
```bash
cp role_config.example.py role_config.py
# Edit role_config.py: your current projects, metrics you own, teams you depend on
```

**4. Run in demo mode** (no Slack needed)
```bash
python main.py              # Morning brief with synthetic signals
python main.py --weekly     # Weekly strategic advisor
python main.py --tools      # Browse tools database
```

**5. Run against live Slack**
```bash
export SLACK_BOT_TOKEN=xoxb-your-token
python main.py --live
```

---

## Sample Output

```
=================================================================
  COMPANY RADAR — MORNING BRIEF | Nov 03, 2024 08:15
=================================================================

2 items need action today — 1 compliance deadline, 1 decision that blocks your work.

🔴 ACT ON THIS
• [Compliance] RBI circular on recurring international cards — Dec 1 deadline.
  Action: Flag to your PM lead and legal today; your international payments feature
  may need to hold or scope down.

• [Leadership] New decision: pause all new international launches until fraud
  resolved. Action: Realign your Q4 roadmap this week.

🟡 GOOD TO KNOW
• [Risk & Fraud] 3DS bypass variant causing fraud spike — team has applied
  temporary auth friction. Monitor your funnel metrics for the next 48h.

• [Engineering] Gateway v2 migration: breaking change in payment session handling.
  Check if your checkout flow uses the affected endpoints.

📊 BUSINESS PULSE
• International checkout funnel: –14% WoW → Your international feature launch
  is now under risk; worth flagging in your next stakeholder update.

⚠️ ANOMALIES
• #risk-fraud: 3× more active than usual — incident likely ongoing.
```

---

## Design Decisions

**Why one brief, not a feed?**
A feed is noise with extra steps. The brief is a decision — it commits to what matters today. Claude's synthesis is the value, not the aggregation.

**Why score before generating the brief?**
Scoring separates the filtering logic from the language model. It's deterministic, auditable, and lets you tune weights to your role without touching the prompt.

**Why SQLite for tools and rhythm?**
Persistence across runs without infra. Tools and channel baselines are cumulative — they get better the longer the tool runs.

**Why is role context gitignored but visible in the code?**
The architecture is the product. The data (your team names, project names, channel IDs) is yours. Anyone who forks this drops in their own `role_config.py` and it works.

---

## Stack

- `anthropic` — Claude 3.5 Sonnet for signal extraction, scoring synthesis, brief writing
- `slack-sdk` — Slack Web API for message fetching (live mode)
- `sqlite3` — stdlib, no additional dependency; for tools DB and rhythm baseline
- `pytz` — IST-aware timestamps throughout
