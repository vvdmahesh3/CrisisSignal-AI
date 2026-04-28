<div align="center">

<img src="https://img.shields.io/badge/🚨_CrisisSignal_AI-Production_Ready-red?style=for-the-badge" alt="CrisisSignal AI"/>

# CrisisSignal AI
### *Rapid Crisis Detection · Crowd-Verified Alerts · Real-Time Response*

[![GDG Solution Challenge 2026](https://img.shields.io/badge/GDG-Solution_Challenge_2026-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/community/gdsc-solution-challenge)
[![Track](https://img.shields.io/badge/Track-Open_Innovation-FF6D00?style=for-the-badge)](https://developers.google.com/community/gdsc-solution-challenge)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

[![SDG 3](https://img.shields.io/badge/SDG_3-Good_Health-%234C9F38?style=flat-square)](https://sdgs.un.org/goals/goal3)
[![SDG 11](https://img.shields.io/badge/SDG_11-Sustainable_Cities-%23FD9D24?style=flat-square)](https://sdgs.un.org/goals/goal11)
[![SDG 16](https://img.shields.io/badge/SDG_16-Peace_%26_Justice-%2300689D?style=flat-square)](https://sdgs.un.org/goals/goal16)

> **"When every second counts, CrisisSignal AI turns raw panic into structured, crowd-verified, life-saving intelligence."**

[🚀 Quick Start](#-quick-start) · [🎬 Demo Mode](#-demo-mode) · [🏗️ Architecture](#️-architecture) · [📖 Docs](#-documentation)

</div>

---

## 📋 Table of Contents

1. [What Is This?](#-what-is-this)
2. [The Problem](#-the-problem)
3. [How It Works](#-how-it-works)
4. [Features](#-features)
5. [Architecture](#️-architecture)
6. [AI Engine](#-ai-engine)
7. [Tech Stack](#️-tech-stack)
8. [Project Structure](#-project-structure)
9. [Quick Start](#-quick-start)
10. [Demo Mode](#-demo-mode)
11. [Default Accounts](#-default-accounts)
12. [API Reference](#-api-reference)
13. [Deployment](#-deployment)
14. [SDG Alignment](#-sdg-alignment)

---

## 🌟 What Is This?

**CrisisSignal AI** is a production-grade, real-time crisis response platform built for closed communities — university campuses, apartment buildings, hostels, hospitals, and any multi-tenant environment.

It solves a simple but deadly problem: **when something bad happens, there is no fast, trusted way for the right person to know.**

Instead of scattered WhatsApp messages or panic phone calls, CrisisSignal provides:

- ✅ **Structured incident reporting** with AI-powered instant classification
- ✅ **Crowd verification** — the community confirms or rejects every alert
- ✅ **Live-updating confidence scores** — trust is earned, not assumed
- ✅ **Role-based dashboards** for residents, admins, and security
- ✅ **Full audit trail** — every action, vote, and escalation is logged
- ✅ **Multi-community isolation** — Building A never sees Building B's alerts

---

## 🔥 The Problem

> 📍 *11:42 PM. University Hostel, Block C, 3rd Floor.*
>
> A student smells smoke. She sends "there might be fire" to a WhatsApp group of 200. Five people react with 🔥. Nobody calls the warden. The warden finds out 18 minutes later — when smoke fills the corridor.
>
> **A system existed. Messages were sent. Nobody knew what was real.**

| Who Suffers | The Gap |
|---|---|
| **Residents / Students** | No structured way to report; messages drown in group chats |
| **Wardens / Admins** | No prioritized, verified feed; rely on word-of-mouth |
| **Security Teams** | No real-time dashboard; respond reactively, not proactively |
| **Institutions** | No audit trail; liability gaps when incidents are disputed |

---

## 💡 How It Works

### The 5-Step Flow

```
1. USER reports incident in plain words
        ↓
2. AI ENGINE classifies in < 1 second
   → Type: FIRE | Severity: 8/10 | Confidence: 65%
        ↓
3. COMMUNITY VOTES — Confirm ✅ or Reject ❌
   → Trusted users' votes carry more weight
        ↓
4. CONFIDENCE updates live → Status evolves
   NEW → VERIFYING → VERIFIED → CRITICAL 🔴
        ↓
5. ADMIN resolves → Audit log records everything
```

### Alert Lifecycle State Machine

```
[NEW] ──────────────────► [VERIFYING]
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              [REJECTED]             [VERIFIED]
              (crowd rejects)            │
                                 (high confidence
                                  + high severity)
                                         │
                                    [CRITICAL] ──► [RESOLVED]
```

---

## ⚡ Features

### Core Platform

| Feature | Description |
|---|---|
| 🚨 **Incident Reporting** | Structured form: description, location, optional photo, emergency flag |
| 🤖 **AI Classification** | Auto-classifies into Fire, Medical, Theft, Violence, Infrastructure, General |
| 📊 **Severity Scoring** | 1–10 score based on keywords, urgency phrases, harm indicators |
| 🎯 **Confidence Engine** | Dynamic score combining AI (40%) + Crowd (40%) + Reporter Trust (20%) |
| 👥 **Crowd Verification** | Community confirms/rejects alerts; votes weighted by reliability |
| 🧠 **X-Logic Explanation** | Human-readable AI reasoning shown to every responder |
| 🔁 **Duplicate Detection** | Merges repeated reports into the parent alert as confirmations |
| 📡 **Real-Time Updates** | WebSocket (Socket.IO) live push — no page refresh needed |
| 🗺️ **Security Map** | Leaflet.js interactive map with color-coded alert pins |
| 🏢 **Multi-Community** | Full tenant isolation — each building/campus is a private group |

### Security & Trust

| Feature | Description |
|---|---|
| 🔐 **CSRF Protection** | Flask-WTF on all state-changing forms and AJAX calls |
| 🚦 **Rate Limiting** | Flask-Limiter: 5 reports per 10 min per user |
| 🛡️ **Reliability Score** | Self-learning trust score (0–100%) per user — adjusts on every outcome |
| 📋 **Audit Log** | Every action logged with actor, timestamp, before/after values |
| 🔑 **Role-Based Access** | `user`, `admin`, `security` — strict route-level enforcement |

### Admin & Operations

| Feature | Description |
|---|---|
| 🖥️ **Command Center** | Priority-sorted live dashboard — critical alerts on top |
| 📈 **Analytics** | Trend charts, alert volume, type distribution, resolution times |
| 👤 **User Management** | View, flag, and manage all community members |
| 🎬 **Demo Mode** | Scripted live scenarios with simulated crowd voting for presentations |
| 📤 **Export** | Audit and alert export for institutional records |
| 🔄 **Health Endpoint** | `/health` and `/health/ready` for load balancer probes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CrisisSignal AI                       │
├──────────────┬──────────────┬──────────────┬────────────┤
│   FRONTEND   │   BACKEND    │  AI ENGINE   │  DATABASE  │
│              │              │              │            │
│ Jinja2 HTML  │ Flask 3.1    │ classify_    │ SQLite     │
│ Vanilla CSS  │ Blueprints   │ text()       │ (dev)      │
│ Vanilla JS   │ Flask-Login  │ Keyword +    │            │
│ Socket.IO    │ Flask-WTF    │ Urgency +    │ PostgreSQL │
│ Lucide Icons │ Flask-Limiter│ ML (TF-IDF) │ (prod)     │
│ Leaflet Maps │ Flask-Migrate│ Confidence  │            │
│              │ Socket.IO    │ Recalculator │ SQLAlchemy │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### Request Flow

```
Browser POST /report
    → Flask route (alerts.py)
    → AlertService.create_alert()
        → ai_engine.process_alert()      ← AI pipeline runs here
            → classify_text()            ← type + keywords
            → get_urgency_info()         ← urgency level
            → calculate_severity()       ← score 1-10
            → calculate_initial_confidence()
            → generate_explanation()     ← X-Logic text
        → _detect_duplicate()            ← merge if dupe
        → Alert saved to DB
        → AuditService.log_event()
        → NotificationService.push_new_alert()  ← WebSocket
    → Redirect to alert detail page
```

### Service Layer

```
app/services/
├── alert_service.py        ← Alert creation, duplicate detection, lifecycle
├── confidence_service.py   ← Confidence recalculation + status determination
├── reliability_service.py  ← User trust score updates + badge assignment
├── audit_service.py        ← Immutable audit log writer
├── notification_service.py ← WebSocket push events (community-scoped)
└── evidence_service.py     ← Photo upload validation (Pillow)
```

---

## 🧠 AI Engine

### Classification Pipeline (`ai_engine.py`)

**Stage 1 — Multi-language Keyword Matching**
```python
CATEGORY_KEYWORDS = {
    "fire":     ["fire", "smoke", "burning", "flame", "blaze", "aag", ...],
    "medical":  ["fainted", "unconscious", "bleeding", "ambulance", ...],
    "theft":    ["stolen", "robbed", "missing", "pickpocket", ...],
    "violence": ["fight", "attack", "weapon", "assault", "threat", ...],
    "infra":    ["leak", "short circuit", "flood", "power cut", ...],
}
# Includes Hindi/Hinglish keywords for inclusive reporting
```

**Stage 2 — Negation Detection**
> *"There is NO smoke"* → smoke keyword filtered out via `_is_negated()`

**Stage 3 — Urgency Amplifiers**
```python
URGENCY_PHRASES = {
    "high":   ["right now", "immediately", "help", "calling police"],
    "medium": ["urgent", "please hurry", "someone is hurt"],
    "low":    ["maybe", "possibly", "not sure"],
}
```

**Stage 4 — ML Classifier (Optional)**
> TF-IDF + LinearSVC model. When trained and available, blends with keyword score (60% ML + 40% keyword). Falls back gracefully if model not found.

**Stage 5 — Confidence Formula**
```
Confidence = (AI_Base × 0.4) + (Weighted_Confirms × 0.4) + (Reporter_Trust × 0.2)

Where:
  Weighted_Confirms = Σ(vote × voter_reliability) / total_votes
  Reporter_Trust    = original reporter's reliability_score
```

**Stage 6 — X-Logic Explanation**
> Every alert gets a plain-English reason: *"Classified as FIRE. Keywords: 'smoke', 'burning smell'. Urgency: HIGH. Confidence boosted by 4 crowd confirmations from trusted users."*

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| **Language** | Python | 3.11+ |
| **Web Framework** | Flask | 3.1.0 |
| **ORM** | Flask-SQLAlchemy | 3.1.1 |
| **Auth** | Flask-Login | 0.6.3 |
| **Real-Time** | Flask-SocketIO (Socket.IO) | 5.5.1 |
| **Migrations** | Flask-Migrate (Alembic) | 4.1.0 |
| **CSRF** | Flask-WTF | 1.2.1 |
| **Rate Limiting** | Flask-Limiter | 3.5.0 |
| **ML** | scikit-learn (TF-IDF + LinearSVC) | 1.5.2 |
| **Image Validation** | Pillow | 11.2.1 |
| **Production Server** | Gunicorn | 23.0.0 |
| **Database (Dev)** | SQLite | built-in |
| **Database (Prod)** | PostgreSQL | 15+ |
| **Reverse Proxy** | Nginx | (see `nginx/nginx.conf`) |
| **Containerization** | Docker + Docker Compose | — |
| **Frontend Maps** | Leaflet.js | CDN |
| **Icons** | Lucide Icons | CDN |

---

## 📁 Project Structure

```
CrisisSignal-AI/
├── run.py                          ← Entry point
├── requirements.txt                ← All dependencies
├── Dockerfile                      ← Production container
├── docker-compose.yml              ← Full stack orchestration
├── .env.example                    ← Environment variable template
│
├── app/
│   ├── __init__.py                 ← Application factory
│   ├── config.py                   ← Dev / Prod / Testing config
│   ├── extensions.py               ← Flask extensions (db, auth, csrf...)
│   ├── models.py                   ← SQLAlchemy models
│   ├── ai_engine.py                ← Full AI classification pipeline
│   ├── seed.py                     ← Demo data seeding
│   ├── logger.py                   ← Structured logging
│   │
│   ├── routes/
│   │   ├── auth.py                 ← Login, register, logout
│   │   ├── alerts.py               ← Report, detail, user dashboard
│   │   ├── admin.py                ← Admin command center
│   │   ├── votes.py                ← Confirm/Reject voting
│   │   ├── demo.py                 ← Demo scenario engine
│   │   ├── api.py                  ← REST API endpoints
│   │   └── health.py               ← /health, /health/ready
│   │
│   ├── services/
│   │   ├── alert_service.py        ← Alert creation + lifecycle
│   │   ├── confidence_service.py   ← Confidence recalculation
│   │   ├── reliability_service.py  ← User trust scoring
│   │   ├── audit_service.py        ← Audit log writing
│   │   ├── notification_service.py ← WebSocket push events
│   │   └── evidence_service.py     ← Photo upload handling
│   │
│   ├── ml/
│   │   └── classifier.py           ← TF-IDF + LinearSVC ML model
│   │
│   ├── templates/
│   │   ├── base.html               ← Dark Intelligence design shell
│   │   ├── landing.html            ← Public homepage
│   │   ├── auth/                   ← Login + Register
│   │   ├── alerts/                 ← Report form + detail view
│   │   ├── dashboard/              ← User, Admin, Analytics, Security, Audit
│   │   ├── demo/                   ← Live demo mode
│   │   └── errors/                 ← 400, 403, 404, 500 pages
│   │
│   └── static/
│       ├── css/                    ← Dark Intelligence design system
│       └── js/                     ← WebSocket engine + voting logic
│
└── nginx/
    └── nginx.conf                  ← TLS termination + proxy config
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/CrisisSignal-AI.git
cd CrisisSignal-AI

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac

# Edit .env — minimum required:
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///crisisSignal.db
```

### 3. Run

```bash
python run.py
```

Open **http://localhost:5000** in your browser.

> The database is auto-created and seeded with demo accounts on first run.

---

## 🎬 Demo Mode

Navigate to **Demo Mode** in the sidebar (admin login required).

Three live scenarios run automatically with simulated crowd voting:

| Scenario | What Happens | Expected Outcome |
|---|---|---|
| 🔥 **Fire in the Hostel** | Realistic fire report, 5 trusted voters confirm | Escalates to **CRITICAL** |
| 🚑 **Student Collapsed** | Medical emergency, one sceptic vote, nurse confirms | Reaches **VERIFIED** |
| 🎭 **Fake Bomb Rumour** | Vague prank-like message, 4 trusted users reject | Auto-**REJECTED** |

Watch the confidence bar animate, votes slide in live, and the status pill change in real time.

---

## 👤 Default Accounts

Auto-seeded on first run:

| Role | Email | Password | Access |
|---|---|---|---|
| **Admin** | `admin@crisis.ai` | `admin123` | Full command center, demo mode, user management |
| **Security** | `security@crisis.ai` | `security123` | Security map, alert feed |
| **User** | `alpha@student.edu` | `student123` | Report incidents, vote on alerts |

> ⚠️ Change all passwords before any production deployment.

---

## 📡 API Reference

All API endpoints are under `/api/` and return JSON.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/alerts` | List all alerts (community-scoped) | ✅ Required |
| `GET` | `/api/alerts/<id>` | Get single alert detail | ✅ Required |
| `POST` | `/api/alerts/<id>/vote` | Cast a confirm/reject vote | ✅ Required |
| `GET` | `/api/stats` | Community statistics | ✅ Required |
| `GET` | `/health` | Basic health check | ❌ Public |
| `GET` | `/health/ready` | DB readiness probe | ❌ Public |

**Example Vote Request:**
```bash
curl -X POST http://localhost:5000/api/alerts/5/vote \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"vote": "confirm"}'
```

**Example Response:**
```json
{
  "success": true,
  "new_confidence": 0.84,
  "new_status": "verified",
  "confirmations": 4,
  "rejections": 1
}
```

---

## 🐳 Deployment

### Docker Compose (Recommended)

```bash
# Copy and configure production env
cp .env.example .env
# Set: FLASK_ENV=production, DATABASE_URL=postgresql://..., SECRET_KEY=<strong-key>

# Build and start
docker-compose up -d --build

# Access at https://localhost (Nginx handles TLS)
```

The stack includes:
- **Flask + Gunicorn** — application server
- **PostgreSQL** — production database
- **Nginx** — TLS termination + static file serving + reverse proxy

### Manual Production

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Run with Gunicorn
gunicorn -w 4 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
         -b 0.0.0.0:5000 "app:create_app('production')"
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Strong random string (min 32 chars) |
| `DATABASE_URL` | ✅ | `sqlite:///dev.db` or `postgresql://user:pass@host/db` |
| `FLASK_ENV` | ✅ | `development` or `production` |
| `SENTRY_DSN` | ⬜ | Sentry error tracking DSN (optional) |

---

## 🌍 SDG Alignment

| SDG | Goal | How CrisisSignal Contributes |
|---|---|---|
| ![SDG3](https://img.shields.io/badge/SDG_3-Good_Health-4C9F38?style=flat-square) | Good Health & Well-Being | Faster medical emergency detection → faster ambulance dispatch |
| ![SDG11](https://img.shields.io/badge/SDG_11-Sustainable_Cities-FD9D24?style=flat-square) | Sustainable Cities | Safer communities through structured, verified alert systems |
| ![SDG16](https://img.shields.io/badge/SDG_16-Peace_%26_Justice-00689D?style=flat-square) | Peace, Justice & Institutions | Transparent, auditable incident management with full accountability |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📖 Documentation

| Document | Description |
|---|---|
| [`MASTER_DOCUMENTATION.md`](MASTER_DOCUMENTATION.md) | Full technical reference — architecture, AI engine, API, DB schema |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Step-by-step production deployment guide |
| [`.env.example`](.env.example) | All environment variables with descriptions |

---

<div align="center">

## 🏁 Built for GDG Solution Challenge 2026

**Open Innovation Track · Rapid Crisis Response**

---

*CrisisSignal AI — Turning raw panic into structured, crowd-verified, actionable truth.*

Made with ❤️ for communities that deserve better than a WhatsApp group in an emergency.

</div>
