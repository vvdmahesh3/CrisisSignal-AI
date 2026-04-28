<p align="center">
  <strong>🚨 CrisisSignal AI</strong><br/>
  <em>Rapid Crisis Response Intelligence Platform</em>
</p>

<p align="center">
  <code>GDG Solution Challenge 2026 — Open Innovation Track</code><br/>
  <code>Master Technical Documentation — v1.0 Final Edition</code>
</p>

---

# CrisisSignal AI — Master Technical Documentation

> **Document Type:** Comprehensive System Design, Architecture, API & Deployment Reference  
> **Version:** 1.0 — Final Production Edition  
> **Competition:** Google Developer Groups (GDG) Solution Challenge 2026  
> **Track:** Open Innovation — Rapid Crisis Response  
> **Status:** Production-Ready  

---

## Table of Contents

| § | Section | What It Covers |
|:---:|---|---|
| **1** | [Executive Summary](#1-executive-summary) | One-paragraph pitch, key capabilities, competitive thesis |
| **2** | [Problem Statement](#2-problem-statement) | Real scenarios, stakeholder pain, four structural failures |
| **3** | [Proposed Solution](#3-proposed-solution) | Three-pillar architecture, step-by-step resolution |
| **4** | [Theory — Core Concepts](#4-theory--core-concepts) | State machine, confidence formula, reliability scoring, evidence scoring |
| **5** | [System Architecture](#5-system-architecture) | Component map, module responsibilities, technology stack |
| **6** | [Backend — Deep Dive](#6-backend--deep-dive) | App factory, models, services, routes, state machine, AI engine |
| **7** | [AI Engine — Design & Logic](#7-ai-engine--design--logic) | Classification pipeline, urgency amplifiers, confidence formula, X-Logic |
| **8** | [Database Design](#8-database-design) | Schema, ER diagram, field reference, relationships |
| **9** | [API Reference](#9-api-reference) | All endpoints, request/response examples |
| **10** | [Frontend — Deep Dive](#10-frontend--deep-dive) | Design system, component library, JS engine, templates |
| **11** | [Real-Time Layer (WebSocket)](#11-real-time-layer-websocket) | SocketIO events, event architecture, client handlers |
| **12** | [End-to-End Workflows](#12-end-to-end-workflows) | Complete data flows with diagrams |
| **13** | [Security & Hardening](#13-security--hardening) | Rate limiting, auth, CSRF, headers, Sentry |
| **14** | [Deployment Guide](#14-deployment-guide) | Local dev, Docker, Nginx, PostgreSQL migration |
| **15** | [Build Roadmap](#15-build-roadmap) | Phase 0–4, what was built in each phase |
| **16** | [SDG Alignment](#16-sdg-alignment) | UN Goals 3, 11, 16 mapping |
| **17** | [Demo Plan](#17-demo-plan) | 5-minute judge script with scripted scenarios |
| **18** | [Future Roadmap](#18-future-roadmap) | Next features, ML upgrade path |
| **19** | [Risk Analysis](#19-risk-analysis) | Identified risks and mitigations |
| **20** | [Glossary](#20-glossary) | All terms defined |

---

## 1. Executive Summary

### 1.1 One-Paragraph Pitch

**CrisisSignal AI** is an AI-powered, crowd-verified crisis alert platform that transforms unstructured emergency reports into structured, trustworthy, and actionable intelligence. It uses lightweight, explainable rule-based NLP to classify incidents and publish them as `Unverified`, then a community confirmation/rejection mechanism continuously updates a dynamic confidence score that drives each alert through a formal lifecycle — from `New` through `Verifying` to `Verified` or `Critical`. The result is a system that improves over time based on measurable evidence and crowd wisdom, not a single one-shot prediction — replacing informal panic (group chats, phone trees, word-of-mouth) with structured, verified, explainable crisis intelligence.

### 1.2 Key Capabilities

| Capability | Description |
|---|---|
| **Structured Reporting** | Free-text incident submission with AI-suggested classification, location zone capture, photo evidence |
| **AI Classification (X-Logic)** | Rule-based NLP engine: categorizes, scores severity, assigns confidence, generates human-readable reasoning |
| **Crowd Verification** | Community confirm/reject voting where each vote is weighted by the voter's individual reliability score |
| **Dynamic Confidence** | A continuously evolving "trust meter" merging AI evidence (40%) + crowd consensus (40%) + reporter reliability (20%) |
| **Alert State Machine** | Formal lifecycle: `new → awaiting_review → verifying → verified → critical → resolved` |
| **Duplicate Detection** | Jaccard-similarity text hashing + location proximity merging within a 30-minute window |
| **Self-Learning Trust** | Per-user reliability scores (0.0–1.0) that evolve based on crowd outcome accuracy |
| **Role-Based Views** | Three distinct interfaces: User/Reporter, Admin/Warden, Security/Responder |
| **Real-Time Updates** | WebSocket push for live confidence bar updates, new alert notifications, status changes |
| **Production Infrastructure** | Docker + Nginx + PostgreSQL + Gunicorn + Sentry + structured JSON logging |

### 1.3 Competitive Thesis

CrisisSignal AI differentiates itself because it **operationalizes trust as a measurable, evolving metric**. Early alerts are explicitly labeled `Unverified` and must earn verification through crowd consensus and reliability-weighted confidence updates. The alert is never a static record — it evolves through a defined lifecycle, making system behavior concrete, observable, and defensible. No existing campus crisis system combines AI explainability + dynamic crowd trust + formal alert lifecycle + self-learning user credibility into a single cohesive platform.

---

## 2. Problem Statement

### 2.1 The Real-World Scenario

> *It's 11:42 PM. University Hostel, Block C, 3rd Floor. A student smells smoke. She opens WhatsApp, types "there might be fire in the corridor," and sends it to a group of 200 people. Five people react with a fire emoji. Someone says "already reported." Nobody calls the warden. Nobody alerts security. The warden discovers the incident 18 minutes later when smoke fills the common area. By then, two students have been hospitalized.*

This scenario is not hypothetical. It describes the systemic communication failure present in virtually every closed institution worldwide — university campuses, student hostels, hospitals, and residential societies.

### 2.2 Stakeholder Impact Analysis

| Stakeholder | Pain Point |
|---|---|
| **Students / Residents** | No structured, centralized channel to make emergency reports; rely on informal, noisy social media |
| **Wardens / Administrators** | No real-time, prioritized feed of verified incidents; drown in unfiltered noise |
| **Security Personnel** | Respond reactively based on phone calls, not proactively on structured data |
| **The Institution** | No audit trail, no accountability, no systematic learning from past incidents |

### 2.3 The Four Structural Failures

**Failure 1 — No Structured Reporting Channel**  
Emergency information travels through informal, high-noise channels (group chats, phone calls, hallway conversations). There is no structured input mechanism that ensures consistent, machine-parseable incident data.

**Failure 2 — No Intelligent Triage**  
Without AI classification, every incoming message demands identical cognitive effort. "Someone dropped coffee in the corridor" and "there's an armed person at the gate" arrive as identical plain-text with no automated priority differentiation.

**Failure 3 — Fake Alert Pollution & Trust Erosion**  
Even basic reporting systems quickly become polluted with false alerts, exaggerations, and pranks. Without verification, responders must react to everything — leading to alert fatigue and eventual disengagement. One false alarm today makes people ignore the real fire tomorrow.

**Failure 4 — Static, Non-Evolving Alerts**  
A fire reported once looks exactly the same on a dashboard whether confirmed by 50 people or zero. Alert severity does not update as more information arrives. There is no lifecycle, no state progression, no evolution.

### 2.4 Concrete Crisis Scenarios

| Scenario | Who Suffers | What Goes Wrong | Trust-Breaker |
|---|---|---|---|
| **Campus Lab Fire** — Unclear location, noisy first report | Students and lab staff needing fast evacuation | System broadcasts "High Severity" without verification — people panic unnecessarily or ignore future alerts | A later "actually it was a drill" post spreads confusion; the app loses credibility permanently |
| **Hostel Medical Emergency** — Ambiguous text, confidence gap | Injured resident needing timely care | Fragmented reports like "someone fell, might be bleeding" lead to under-escalation (delay) or over-escalation (wasted resources) | Subsequent contradicting reports leave the system unable to self-correct |
| **Event Crowd Panic** — Prank/fake alerts, social reinforcement | Attendees in crowded areas | One message like "bomb threat???" triggers immediate high severity; the system lacks anti-prank design | Prank messages cause real panic, permanently harming future responsiveness |

---

## 3. Proposed Solution

CrisisSignal AI resolves all four structural failures through a **layered three-pillar architecture**:

1. **Structured AI Intelligence** — Normalizes and classifies all input
2. **Community-Powered Verification** — Crowd validates AI judgements
3. **Trustworthy Alert Lifecycle** — Formal state machine tracks evolution

### 3.1 Step-by-Step Resolution

**Step 1: Structured Input → Solves Failure 1**

Users submit reports via a structured form capturing: incident description (free text, 500 chars max), incident type (AI-suggested), location (zone selector + GPS), timestamp (auto-captured), optional photo evidence. This replaces informal WhatsApp messages with machine-parseable data.

**Step 2: AI Triage → Solves Failure 2**

The AI engine processes submissions in under 200ms: classifies incident type, assigns severity (1–10), calculates initial confidence (0.0–1.0), generates plain-language X-Logic explanation. Responders see `"FIRE | Severity 9 | Confidence 0.78 | Reason: Contains smoke, floor 3, immediately"` — not a text blob.

**Step 3: Crowd Verification → Solves Failure 3**

Every submitted alert enters `VERIFYING` state. Other users confirm or reject, each vote weighted by the voter's User Reliability Score. Alerts with sufficient crowd confirmation rise in confidence; rejected alerts are flagged. Reports containing suspicion language receive an initial trust penalty overcomeable only by strong crowd confirmation.

**Step 4: Alert Lifecycle → Solves Failure 4**

Alerts are dynamic entities that evolve through defined states. A new report is not treated the same as a mass-confirmed critical incident. The dashboard reflects real-time state for every active alert, and the full evolution history is preserved in an immutable audit trail.

### 3.2 What Makes CrisisSignal AI Different

| Dimension | Typical Emergency App | CrisisSignal AI |
|---|---|---|
| Alert Input | Manual dropdown / button press | Free text + AI classification with explanation |
| Trust Mechanism | None | Weighted crowd verification with reliability scoring |
| Alert Evolution | Static; never updates | Formal state machine with visible lifecycle |
| AI Reasoning | Black box ("Detected: Fire") | Explainable X-Logic with triggered evidence |
| Duplicate Handling | None; 30 reports = 30 alerts | Intelligent merging; duplicates boost confidence |
| User Credibility | All users treated equally | Dynamic, self-learning reliability score per user |
| Demo Behavior | Single prediction, no evolution | Multi-stage lifecycle visible to judges in real-time |

---

## 4. Theory — Core Concepts

### 4.1 The Alert Lifecycle (State Machine)

Every alert passes through strictly validated states with enforced transition rules:

```
[Submitted] → new
                ↓
          awaiting_review ←→ rejected
                ↓
            verifying  ←→  rejected
                ↓
            verified
                ↓
            critical  (auto if conf ≥ 0.85 AND severity ≥ 8)
                ↓
            resolved  ← terminal — admin must resolve
```

**Valid Transitions:**

| From State | Can Transition To |
|---|---|
| `new` | `verifying`, `awaiting_review`, `rejected`, `resolved` |
| `awaiting_review` | `verifying`, `verified`, `rejected`, `resolved` |
| `verifying` | `verified`, `rejected`, `critical`, `resolved` |
| `verified` | `critical`, `resolved` |
| `critical` | `resolved` |
| `rejected` | `resolved` |
| `resolved` | *(terminal — no exit)* |

**State Trigger Logic:**

```python
def determine_new_status(alert):
    conf     = alert.confidence
    sev      = alert.severity
    rej      = alert.weighted_rejects
    conf_pos = alert.weighted_confirms

    if rej > conf_pos * 2:
        return "rejected"
    elif conf >= 0.85 and sev >= 8:
        return "critical"
    elif conf >= 0.70:
        return "verified"
    elif conf >= 0.30:
        return "verifying"
    else:
        return "new"
```

**State Machine Diagram:**

```mermaid
stateDiagram-v2
    [*] --> new : User submits report
    new --> verifying : AI processes, initial confidence ≥ 0.30
    new --> awaiting_review : Flagged user or low confidence
    awaiting_review --> verifying : Admin reviews
    awaiting_review --> rejected : Admin rejects
    verifying --> verified : Confidence ≥ 0.70
    verifying --> rejected : Crowd majority rejects
    verifying --> critical : Confidence ≥ 0.85 AND severity ≥ 8
    verified --> critical : Auto-escalation or admin action
    verified --> resolved : Admin resolves
    critical --> resolved : Admin resolves
    rejected --> resolved : Admin archives
    resolved --> [*]
```

### 4.2 The Confidence Score (0.0 → 1.0)

The core trust metric — calculated using the **Triangulated Trust Model**:

```
Confidence = (AI_Base × 0.40) + (Crowd_Consensus × 0.40) + (Reliability_Bonus × 0.20)

Where:
  AI_Base        = Initial confidence from classification engine (0.0–1.0)
  Crowd_Consensus = Σ(confirm_votes × voter_reliability) /
                    Σ(all_votes × voter_reliability)
  Reliability_Bonus = 0.10 if reporter_reliability > 0.75, else 0.0
```

**Confidence → Status Thresholds:**

| Range | Assigned Status |
|---|---|
| 0.00 – 0.29 | `new` — insufficient data |
| 0.30 – 0.69 | `verifying` — awaiting crowd input |
| 0.70 – 0.84 | `verified` — sufficient crowd confirmation |
| 0.85 – 1.00 + severity ≥ 8 | `critical` — auto-escalate |

**Rejection Override:** If `weighted_rejects > weighted_confirms × 2`, confidence drops below 0.20 and status transitions to `rejected` regardless of AI score.

**Example Evolution:**

```
Report submitted:       AI score 0.62  → Status: verifying (62%)
+3 reliable confirms:   Score rises    → Status: verifying (73%)
+2 more confirms:       Score rises    → Status: verified  (83%)
Severity = 9, conf=0.86:               → Status: critical  (86%) 🔴
```

### 4.3 User Reliability Score (0.0 → 1.0)

Each user has a self-learning reputation score that evolves based on accuracy:

| Event | Score Change |
|---|---|
| Alert confirmed by crowd (≥ 5 confirmations) | +0.05 |
| Alert escalated to CRITICAL | +0.15 |
| Alert rejected by crowd | −0.10 |
| Alert manually rejected by admin | −0.15 |
| Accurate vote (matched final outcome) | +0.02 |
| Wrong vote (disagreed with outcome) | −0.03 |

**Rules:**
- All new users start at **0.50** (neutral; moderate influence)
- Maximum: **1.0** (highly trusted member)
- Minimum: **0.0** (account flagged; alerts auto-reviewed)
- 3+ rejections → account flagged (`is_flagged = True`)

**Why It Matters:**  
A security guard with reliability 0.90 has **3.6× more influence** than a known prankster at 0.25. The system trains prank users out over time — their degraded scores reduce their vote weight and flag their reports, automatically improving system-wide signal quality.

### 4.4 Evidence Score (0 → 100)

A signal-quality metric calculated at submission time:

| Signal | Points |
|---|---|
| Each matched keyword | +15 (up to 60 max) |
| High urgency ("urgent", "help", "dying") | +20 |
| Medium urgency ("asap", "serious") | +10 |
| Harm indicators ("bleeding", "unconscious") | +10 each |
| Photo evidence attached | +10 |
| Multiple locations mentioned | +5 |

**Evidence Strength Tiers:**

| Score Range | Strength Label |
|---|---|
| 0 – 29 | Weak |
| 30 – 59 | Moderate |
| 60 – 79 | Strong |
| 80 – 100 | Critical Evidence |

### 4.5 Duplicate Detection

When a fire breaks out, 30 people report it simultaneously. Without deduplication, 30 separate low-confidence alerts clutter the dashboard.

**Algorithm:**
1. On new submission, compute **Jaccard similarity** on tokenized text of recent alerts (within 30 minutes, same location zone)
2. If similarity > 0.60 → mark as duplicate, link via `parent_alert_id`
3. Increment `confirmations_count` on parent; do NOT create new dashboard row
4. **Effect:** 30 reports of the same fire → 1 alert with `confirmations_count = 30` and very high confidence

```python
def detect_duplicate(new_message, new_location, time_window_minutes=30):
    recent_alerts = db.get_recent_alerts(new_location, time_window_minutes)
    for alert in recent_alerts:
        similarity = jaccard_similarity(
            tokenize(new_message), tokenize(alert.message)
        )
        if similarity > 0.60:
            return alert.id   # Return parent alert ID
    return None               # No duplicate found
```

---
## 5. System Architecture

### 5.1 High-Level Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CRISISSIGNAL AI                              │
│                                                                     │
│  ┌──────────────────────┐      ┌──────────────────────────────────┐  │
│  │    USER INTERFACE    │      │         AI ENGINE                │  │
│  │   (Jinja2 + CSS/JS)  │      │                                  │  │
│  │                      │─────►│  Classifier (NLP + Rules)        │  │
│  │  • Report Form       │      │  Severity Scorer                 │  │
│  │  • Admin Dashboard   │      │  Confidence Calculator           │  │
│  │  • Security Map      │      │  Duplicate Detector              │  │
│  │  • User Dashboard    │      │  X-Logic Explainer               │  │
│  │  • Audit Log View    │      └──────────────┬───────────────────┘  │
│  └──────────────────────┘                     │                      │
│           │  HTTP/WS                          │                      │
│           ▼                                   ▼                      │
│  ┌──────────────────────┐      ┌──────────────────────────────────┐  │
│  │   BACKEND (Flask)    │      │        DATABASE                  │  │
│  │                      │      │  SQLite (dev) / PostgreSQL (prod)│  │
│  │  Auth Blueprint      │─────►│                                  │  │
│  │  Alerts Blueprint    │      │  users                           │  │
│  │  Votes Blueprint     │      │  alerts                          │  │
│  │  Admin Blueprint     │      │  crowd_votes                     │  │
│  │  API Blueprint       │      │  audit_log                       │  │
│  │  Health Blueprint    │      └──────────────────────────────────┘  │
│  └──────────────────────┘                                            │
│           │  WebSocket                                               │
│           ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  PRODUCTION STACK                                            │    │
│  │  Nginx (TLS termination) → Gunicorn (WSGI) → Flask App      │    │
│  │  Sentry (error tracking) + JSON Logging (Datadog-compat.)   │    │
│  │  Docker Compose (app + db + nginx)                          │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Module-Level Flow (Mermaid)

```mermaid
flowchart TD
    subgraph UI ["User Interface (HTML/CSS/JS)"]
        RF[Report Form]
        AD[Admin Dashboard]
        UD[User Dashboard]
        SM[Security Map]
        AL[Audit Log]
    end

    subgraph Backend ["Backend Logic (Flask)"]
        AIE[AI Engine]
        CS[Confidence Service]
        SM2[State Machine]
        RS[Reliability Service]
        NS[Notification Service]
        AS[Audit Service]
    end

    subgraph Data ["Storage (SQLite / PostgreSQL)"]
        DB[(alerts · votes · users · audit_log)]
    end

    subgraph RT ["Real-Time (SocketIO)"]
        WS[WebSocket Server]
    end

    RF -->|POST /submit| AIE
    AIE -->|classification + score| CS
    CS -->|recalculate| SM2
    SM2 -->|status change| AS
    SM2 -->|outcome| RS
    RS -->|weight update| CS
    SM2 -->|push event| NS
    NS --> WS
    WS -->|live update| AD
    WS -->|confidence bar| UD
    SM2 -.->|persist| DB
    DB -.->|read| AD
    DB -.->|read| AL
    SM -.->|active alerts| DB
```

### 5.3 Module Responsibilities

| Module | File | Responsibility |
|---|---|---|
| **App Factory** | `app/__init__.py` | Creates Flask app, registers blueprints, initializes extensions, wires Sentry + logging |
| **Configuration** | `app/config.py` | Dev/Prod/Test config classes; mandatory env-var assertions in ProductionConfig |
| **Models** | `app/models.py` | SQLAlchemy ORM: User, Alert, CrowdVote, AuditLog, EvidenceFile |
| **AI Engine** | `app/ai_engine.py` | Keyword classification, severity scoring, confidence calculation, X-Logic generation |
| **Confidence Service** | `app/services/confidence_service.py` | Triangulated confidence recalculation after each vote |
| **Alert Service** | `app/services/alert_service.py` | Create alert, duplicate detection, state machine transitions |
| **Reliability Service** | `app/services/reliability_service.py` | User score updates on alert resolution |
| **Evidence Service** | `app/services/evidence_service.py` | Pillow-validated image uploads, evidence scoring |
| **Audit Service** | `app/services/audit_service.py` | Immutable event logging with actor, action, old→new values |
| **Notification Service** | `app/services/notification_service.py` | WebSocket push events to rooms |
| **Auth Blueprint** | `app/routes/auth.py` | Register, login, logout — Flask-Login session management |
| **Alerts Blueprint** | `app/routes/alerts.py` | Submit, detail, history — rate-limited by Flask-Limiter |
| **Votes Blueprint** | `app/routes/votes.py` | Confirm/reject voting — deduplication via UNIQUE constraint |
| **Admin Blueprint** | `app/routes/admin.py` | Dashboard, resolve, escalate, CSV export, user management |
| **API Blueprint** | `app/routes/api.py` | Pure JSON REST API for programmatic access |
| **Health Blueprint** | `app/routes/health.py` | `/health` (liveness) + `/health/ready` (readiness with DB check) |
| **Dark Intelligence CSS** | `app/static/css/dark-intelligence.css` | Premium UI overrides: nav indicator, metric typography, status borders |
| **Dark Intelligence JS** | `app/static/js/dark-intelligence.js` | IO reveal, counter animation, confidence bars, scroll blur, ripple, toast API |

### 5.4 Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | HTML5, Vanilla CSS, Vanilla JavaScript | Zero build step, maximum control, instant load |
| **Icons** | Lucide Icons (CDN) | Modern SVG icons, superior to FontAwesome |
| **Maps** | Leaflet.js (CDN) | Open-source, touch-friendly, zero API key |
| **Charts** | Chart.js (CDN) | Animated analytics widgets |
| **Fonts** | Google Fonts — Inter + JetBrains Mono | Premium feel, consistent cross-platform |
| **Backend** | Python 3.11+, Flask 3.x | Lightweight, excellent AI integration, rapid iteration |
| **ORM** | Flask-SQLAlchemy + Alembic | Clean models, migration support |
| **Auth** | Flask-Login + Werkzeug | Session-based, role-based access |
| **Real-Time** | Flask-SocketIO + gevent | WebSocket push — gevent required for Python 3.11+ |
| **Rate Limiting** | Flask-Limiter | Protect against flooding and abuse |
| **Image Processing** | Pillow | Evidence file validation (format, size, dimensions) |
| **Database (Dev)** | SQLite | Zero-config, portable, instant demo |
| **Database (Prod)** | PostgreSQL + psycopg2 | Production scalability, full ACID compliance |
| **WSGI Server** | Gunicorn | Production-grade Python app server |
| **Reverse Proxy** | Nginx | TLS termination, WebSocket upgrade, HSTS headers |
| **Containerization** | Docker + Docker Compose | Reproducible builds, multi-service orchestration |
| **Error Tracking** | Sentry SDK | Real-time exception capture with stack traces |
| **Logging** | Custom JSONFormatter | Structured logs — Datadog/Cloud Logging compatible |

---

## 6. Backend — Deep Dive

### 6.1 Application Factory Pattern

The app uses the factory pattern (`create_app()`) — a Flask best practice that enables:
- Multiple configurations (dev/test/prod)
- Clean blueprint registration
- Testing in isolation without global state

```python
# app/__init__.py (simplified)
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, async_mode='gevent')
    limiter.init_app(app)

    # Register blueprints
    from app.routes.auth   import auth_bp
    from app.routes.alerts import alerts_bp
    from app.routes.admin  import admin_bp
    from app.routes.api    import api_bp
    from app.routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp,    url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/health')

    # Production: Sentry + ProxyFix + JSON logging
    if app.config['ENV'] == 'production':
        init_sentry(app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
        configure_json_logging(app)

    return app
```

### 6.2 Configuration Classes

```python
# app/config.py

class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///crisis_dev.db'
    SECRET_KEY = 'dev-secret-key'

class ProductionConfig:
    DEBUG = False
    TESTING = False

    def __init__(self):
        # Hard assertions — app WILL NOT start without these
        assert os.environ.get('SECRET_KEY'), "SECRET_KEY must be set"
        assert os.environ.get('DATABASE_URL'), "DATABASE_URL must be set"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
```

### 6.3 Database Models

```python
# app/models.py (abridged — key fields)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(100), nullable=False)
    email             = db.Column(db.String(150), unique=True, nullable=False)
    password_hash     = db.Column(db.String(256), nullable=False)
    role              = db.Column(db.String(20), default='user')  # user|admin|security
    reliability_score = db.Column(db.Float, default=0.5)
    total_reports     = db.Column(db.Integer, default=0)
    confirmed_reports = db.Column(db.Integer, default=0)
    rejected_reports  = db.Column(db.Integer, default=0)
    is_flagged        = db.Column(db.Boolean, default=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id                  = db.Column(db.Integer, primary_key=True)
    message             = db.Column(db.Text, nullable=False)
    type                = db.Column(db.String(20), default='general')
    severity            = db.Column(db.Integer, default=1)  # 1–10
    location            = db.Column(db.String(100))
    confidence          = db.Column(db.Float, default=0.5)  # 0.0–1.0
    initial_confidence  = db.Column(db.Float, default=0.5)
    confirmations_count = db.Column(db.Integer, default=0)
    rejections_count    = db.Column(db.Integer, default=0)
    weighted_confirms   = db.Column(db.Float, default=0.0)
    weighted_rejects    = db.Column(db.Float, default=0.0)
    status              = db.Column(db.String(20), default='new')
    evidence_score      = db.Column(db.Integer, default=0)
    explanation         = db.Column(db.Text)
    timestamp           = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at         = db.Column(db.DateTime)
    resolution_note     = db.Column(db.Text)
    parent_alert_id     = db.Column(db.Integer, db.ForeignKey('alerts.id'))
    reported_by         = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to         = db.Column(db.Integer, db.ForeignKey('users.id'))

class CrowdVote(db.Model):
    __tablename__ = 'crowd_votes'
    id          = db.Column(db.Integer, primary_key=True)
    alert_id    = db.Column(db.Integer, db.ForeignKey('alerts.id', ondelete='CASCADE'))
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    vote        = db.Column(db.String(10))   # 'confirm' or 'reject'
    vote_weight = db.Column(db.Float)        # voter's reliability at vote time
    voted_at    = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('alert_id', 'user_id', name='one_vote_per_user_per_alert'),
    )

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id             = db.Column(db.Integer, primary_key=True)
    alert_id       = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=True)
    actor_id       = db.Column(db.Integer, db.ForeignKey('users.id'))  # NULL = system
    action         = db.Column(db.String(50))
    previous_value = db.Column(db.Text)
    new_value      = db.Column(db.Text)
    logged_at      = db.Column(db.DateTime, default=datetime.utcnow)
```

### 6.4 Service Layer

**Architecture principle:** Routes are thin — they validate input, call a service, return a response. ALL business logic lives in services. This makes testing trivial and keeps routes readable.

```
Route (HTTP request)
    → Input validation
    → Service call (business logic)
        → Model query / AI engine / confidence calculation
        → Audit log write
        → WebSocket push
    → HTTP response
```

**Alert Service — Core Create Flow:**

```python
# services/alert_service.py
def create_alert(message, location, user_id):
    # 1. Run AI pipeline
    ai_result = ai_engine.process_alert(message, location)

    # 2. Check for duplicates
    parent = detect_duplicate(message, location)
    if parent:
        parent.confirmations_count += 1
        parent.confidence = recalculate_confidence(parent)
        audit_service.log("DUPLICATE_MERGED", parent.id, user_id)
        return parent, "duplicate"

    # 3. Create new alert
    alert = Alert(
        message=message, location=location,
        type=ai_result['type'], severity=ai_result['severity'],
        confidence=ai_result['confidence'],
        explanation=ai_result['explanation'],
        evidence_score=ai_result['evidence_score'],
        reported_by=user_id, status='new'
    )
    db.session.add(alert)
    db.session.commit()

    # 4. Audit
    audit_service.log("ALERT_CREATED", alert.id, user_id)

    # 5. Real-time push
    notification_service.push_new_alert(alert)

    return alert, "created"
```

**State Machine — Transition Enforcement:**

```python
VALID_TRANSITIONS = {
    'new':            ['verifying', 'awaiting_review', 'rejected', 'resolved'],
    'awaiting_review': ['verifying', 'verified', 'rejected', 'resolved'],
    'verifying':      ['verified', 'rejected', 'critical', 'resolved'],
    'verified':       ['critical', 'resolved'],
    'critical':       ['resolved'],
    'rejected':       ['resolved'],
    # 'resolved' is terminal
}

def transition_alert(alert, new_status, actor_id, reason=""):
    if new_status not in VALID_TRANSITIONS.get(alert.status, []):
        raise ValueError(f"Invalid: {alert.status} → {new_status}")
    old = alert.status
    alert.status = new_status
    if new_status == 'resolved':
        alert.resolved_at = datetime.utcnow()
    db.session.commit()
    audit_service.log("STATUS_CHANGE", alert.id, actor_id,
                      f"{old} → {new_status}: {reason}")
    notification_service.push_status_change(alert, old, new_status)
```

### 6.5 Route Blueprints Summary

| Blueprint | Prefix | Key Routes |
|---|---|---|
| `auth_bp` | `/` | `GET/POST /login`, `GET/POST /register`, `GET /logout` |
| `alerts_bp` | `/alerts` | `GET /submit` (form), `POST /submit` (rate-limited), `GET /<id>`, `GET /history` |
| `votes_bp` | `/vote` | `POST /vote/<id>` (confirm/reject) |
| `admin_bp` | `/admin` | `GET /dashboard`, `POST /resolve/<id>`, `POST /escalate/<id>`, `GET /export/csv`, `POST /flag-user/<id>` |
| `api_bp` | `/api` | `GET /alerts`, `POST /alerts`, `GET /alerts/<id>`, `POST /alerts/<id>/vote`, `GET /alerts/preview` |
| `health_bp` | `/health` | `GET /` (liveness → `{"status":"ok"}`), `GET /ready` (readiness → DB check) |

---

## 7. AI Engine — Design & Logic

### 7.1 Design Philosophy

| Principle | Implementation |
|---|---|
| **Genuinely useful** | Multi-stage pipeline: keyword → urgency → severity → confidence → explanation |
| **Transparent** | Every decision annotated with X-Logic; no black-box behavior |
| **Fast** | Complete processing in < 200ms; no heavy ML model dependencies |
| **Practical** | Rule-based NLP that ships out-of-the-box; ML upgrade path documented |

### 7.2 Stage 1 — Keyword Classification

```python
CATEGORY_KEYWORDS = {
    "fire":     ["fire", "smoke", "burning", "flame", "blaze", "ash", "sparks", "heat"],
    "medical":  ["fainted", "unconscious", "bleeding", "hurt", "ambulance",
                 "heart", "not responding", "breathing", "injury"],
    "theft":    ["stolen", "theft", "robbed", "pickpocket", "missing", "snatched"],
    "violence": ["fight", "attack", "weapon", "assault", "threat",
                 "hitting", "beating", "knife", "gun"],
    "infra":    ["leak", "short circuit", "flood", "power cut",
                 "broken", "gas", "elevator stuck"],
}

def classify_text(text):
    text_lower = text.lower()
    scores = {cat: sum(1 for kw in kws if kw in text_lower)
              for cat, kws in CATEGORY_KEYWORDS.items()}
    top = max(scores, key=scores.get)
    return ("general", 0) if scores[top] == 0 else (top, scores[top])
```

### 7.3 Stage 2 — Urgency Amplifiers

```python
URGENCY_PHRASES = {
    "high":   ["immediately", "right now", "urgent", "emergency",
               "call police", "help", "dying", "call ambulance"],
    "medium": ["quickly", "asap", "need help", "please come"],
    "low":    ["might be", "i think", "maybe", "not sure", "possibly"],
}

def get_urgency_weight(text):
    text_lower = text.lower()
    for level, phrases in URGENCY_PHRASES.items():
        for phrase in phrases:
            if phrase in text_lower:
                return {"high": 3, "medium": 1, "low": -1}[level]
    return 0
```

### 7.4 Stage 3 — Severity Scoring

```python
CATEGORY_BASE_SEVERITY = {
    "fire": 7, "violence": 7, "medical": 6,
    "theft": 4, "infra": 4, "general": 1
}
HARM_INDICATORS     = ["bleeding", "unconscious", "trapped", "cannot breathe", "injury"]
LOCATION_MULTIPLIERS = ["main gate", "children", "crowded", "hostel", "parking"]

def calculate_severity(category, text, urgency_weight):
    base = CATEGORY_BASE_SEVERITY.get(category, 1)
    text_lower = text.lower()
    harm_bonus     = sum(2 for h in HARM_INDICATORS if h in text_lower)
    location_bonus = sum(1 for l in LOCATION_MULTIPLIERS if l in text_lower)
    return max(1, min(10, base + urgency_weight + harm_bonus + location_bonus))
```

### 7.5 Stage 4 — Initial Confidence Calculation

```python
def calculate_initial_confidence(keyword_match_count):
    if keyword_match_count == 0:   return 0.25   # No evidence
    elif keyword_match_count == 1: return 0.50   # Single keyword
    elif keyword_match_count >= 2: return 0.65   # Multiple keywords
    return 0.40

def update_confidence_with_crowd(initial, confirms_w, rejects_w, reporter_reliability):
    crowd_score      = confirms_w / (confirms_w + rejects_w + 0.001)
    reliability_bonus = 0.10 if reporter_reliability > 0.75 else 0.0
    result = (initial * 0.40) + (crowd_score * 0.40) + (reliability_bonus * 0.20)
    return round(max(0.0, min(1.0, result)), 4)
```

### 7.6 Stage 5 — X-Logic Explanation Generator

Produces human-readable reasoning attached to every alert:

```python
def generate_explanation(alert_type, keywords_found, severity,
                         urgency_phrases, confidence, crowd_data):
    parts = []
    if keywords_found:
        parts.append(f"Detected keywords: {', '.join(keywords_found)}")
    if urgency_phrases:
        parts.append(f"Urgency phrases: {', '.join(urgency_phrases)}")
    if crowd_data["confirmations"] > 0:
        parts.append(
            f"Confidence boosted by {crowd_data['confirmations']} crowd "
            f"confirmations (avg. reliability {crowd_data['avg_reliability']:.2f})"
        )
    return ". ".join(parts) + "."
```

**Example Output:**
```
FIRE | Severity 8 | Confidence 0.82
Reason: "Detected keywords: smoke (fire indicator), burning smell (fire indicator),
floor 3 (location context). Urgency phrase detected: immediately. Severity elevated
by 2 for body proximity indicator cannot breathe. Confidence boosted by crowd
verification: 9 confirmations from users with avg. reliability 0.71."
```

### 7.7 AI Processing Pipeline — Complete Flow

```mermaid
flowchart LR
    A[Raw text input] --> B[Preprocess\nlowercase, strip]
    B --> C[Keyword Classification\n→ alert_type + match_count]
    C --> D[Urgency Detection\n→ urgency_weight]
    D --> E[Severity Scoring\nbase + urgency + harm + location]
    E --> F[Suspicion Check\nbomb, fake, joke → penalty]
    F --> G[Initial Confidence\nkeyword density]
    G --> H[Evidence Score\n0-100]
    H --> I[Duplicate Detection\nJaccard similarity]
    I --> J[X-Logic Generation\nhuman explanation]
    J --> K[Result Object\ntype, severity, confidence,\nevidence_score, explanation]
```

---

## 8. Database Design

### 8.1 Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ ALERTS : "reports"
    USERS ||--o{ CROWD_VOTES : "casts"
    USERS ||--o{ AUDIT_LOG : "performs"
    ALERTS ||--o{ CROWD_VOTES : "receives"
    ALERTS ||--o{ AUDIT_LOG : "generates"
    ALERTS ||--o{ ALERTS : "parent/child (duplicates)"

    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string role
        float reliability_score
        int total_reports
        int confirmed_reports
        int rejected_reports
        bool is_flagged
        datetime created_at
    }

    ALERTS {
        int id PK
        text message
        string type
        int severity
        string location
        float confidence
        float initial_confidence
        int confirmations_count
        int rejections_count
        float weighted_confirms
        float weighted_rejects
        string status
        int evidence_score
        text explanation
        datetime timestamp
        datetime resolved_at
        text resolution_note
        int parent_alert_id FK
        int reported_by FK
        int assigned_to FK
    }

    CROWD_VOTES {
        int id PK
        int alert_id FK
        int user_id FK
        string vote
        float vote_weight
        datetime voted_at
    }

    AUDIT_LOG {
        int id PK
        int alert_id FK
        int actor_id FK
        string action
        text previous_value
        text new_value
        datetime logged_at
    }
```

### 8.2 Schema Reference

**`users` table:**

| Column | Type | Constraint | Purpose |
|---|---|---|---|
| `id` | INTEGER | PK | Unique identifier |
| `name` | VARCHAR(100) | NOT NULL | Display name |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | Login credential |
| `password_hash` | VARCHAR(256) | NOT NULL | Werkzeug Bcrypt hash |
| `role` | VARCHAR(20) | NOT NULL, default='user' | `user` / `admin` / `security` |
| `reliability_score` | FLOAT | default=0.5 | 0.0–1.0 self-learning trust |
| `is_flagged` | BOOLEAN | default=False | 3+ rejections = flagged |

**`alerts` table:**

| Column | Type | Constraint | Purpose |
|---|---|---|---|
| `id` | INTEGER | PK | Unique identifier |
| `message` | TEXT | NOT NULL | Original report text |
| `type` | VARCHAR(20) | NOT NULL | fire/medical/theft/violence/infra/general |
| `severity` | INTEGER | 1–10 | Computed severity score |
| `confidence` | FLOAT | 0.0–1.0 | Live evolving trust score |
| `status` | VARCHAR(20) | NOT NULL | Alert lifecycle state |
| `weighted_confirms` | FLOAT | default=0.0 | Sum of reliability-weighted confirmations |
| `weighted_rejects` | FLOAT | default=0.0 | Sum of reliability-weighted rejections |
| `explanation` | TEXT | — | X-Logic reasoning text |
| `parent_alert_id` | INTEGER | FK | Links duplicate to parent |

**`crowd_votes` table:**

| Column | Type | Constraint | Purpose |
|---|---|---|---|
| `id` | INTEGER | PK | Unique identifier |
| `alert_id` | INTEGER | FK, CASCADE DELETE | Which alert was voted on |
| `user_id` | INTEGER | FK | Who voted |
| `vote` | VARCHAR(10) | NOT NULL | `confirm` or `reject` |
| `vote_weight` | FLOAT | NOT NULL | Voter's reliability at vote time (snapshot) |
| — | — | UNIQUE(`alert_id`, `user_id`) | Prevents duplicate votes |

**`audit_log` table:**

| Column | Type | Constraint | Purpose |
|---|---|---|---|
| `id` | INTEGER | PK | Unique identifier |
| `alert_id` | INTEGER | FK, NULLABLE | NULL for global admin actions |
| `actor_id` | INTEGER | FK, NULLABLE | NULL for system-triggered actions |
| `action` | VARCHAR(50) | NOT NULL | `ALERT_CREATED`, `STATUS_CHANGE`, `VOTE_CAST`, etc. |
| `previous_value` | TEXT | — | Before state |
| `new_value` | TEXT | — | After state |

### 8.3 Key Design Decisions

| Decision | Rationale |
|---|---|
| `parent_alert_id` self-reference | Duplicate detection merges children into parent without deleting data |
| `vote_weight` snapshot | Records reliability AT VOTE TIME — prevents retroactive changes corrupting history |
| `actor_id` nullable in audit_log | System-triggered events (auto-escalation) have no human actor |
| UNIQUE on `(alert_id, user_id)` in votes | Database-enforced deduplication — one vote per user per alert |
| Separate `weighted_confirms` / `weighted_rejects` | Denormalized for O(1) confidence recalculation without summing all votes |

---
## 9. API Reference

### 9.1 Authentication Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| GET/POST | `/login` | Public | Login form + session creation |
| GET/POST | `/register` | Public | Registration form |
| GET | `/logout` | Required | Session destroy |

### 9.2 Alert Endpoints

| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/alerts/submit` | Required | — | Render report form |
| POST | `/alerts/submit` | Required | 5/10min | Submit alert → AI pipeline |
| GET | `/alerts/<id>` | Required | — | Alert detail + timeline |
| GET | `/alerts/history` | Required | — | User's own alert history |
| GET | `/api/alerts` | Required | — | JSON list (filterable) |
| POST | `/api/alerts` | Required | 5/10min | JSON submit |
| GET | `/api/alerts/preview` | Required | — | AI preview without saving |
| GET | `/api/alerts/<id>` | Required | — | JSON detail |

**POST /alerts/submit — Request:**
```json
{
  "message": "Heavy smoke from staircase, burning smell, people running",
  "location": "Block C, Floor 3",
  "alert_type": "fire",
  "emergency_flag": true
}
```

**POST /alerts/submit — Response:**
```json
{
  "alert_id": 42,
  "status": "verifying",
  "type": "fire",
  "severity": 8,
  "confidence": 0.65,
  "evidence_score": 75,
  "explanation": "Detected keywords: smoke, burning smell. Urgency phrase: people running.",
  "message": "Alert submitted. Awaiting verification."
}
```

### 9.3 Vote Endpoint

| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| POST | `/vote/vote/<alert_id>` | Required | 20/min | Cast confirm or reject |

**POST /vote/vote/42 — Request:**
```json
{ "vote": "confirm" }
```

**Response:**
```json
{
  "success": true,
  "new_confidence": 0.78,
  "new_status": "verified",
  "confirmations": 5,
  "rejections": 1
}
```

### 9.4 Admin Endpoints

| Method | Route | Auth (Admin) | Description |
|---|---|---|---|
| GET | `/admin/dashboard` | Admin | Priority-sorted alert feed |
| POST | `/admin/resolve/<id>` | Admin | Mark resolved + note |
| POST | `/admin/escalate/<id>` | Admin | Force-escalate to critical |
| POST | `/admin/reject/<id>` | Admin | Admin reject |
| GET | `/admin/export/csv` | Admin | Streaming CSV export |
| POST | `/admin/flag-user/<id>` | Admin | Flag user account |
| POST | `/admin/assign/<id>` | Admin | Assign responder |

### 9.5 Health Endpoints

| Method | Route | Description | Response |
|---|---|---|---|
| GET | `/health` | Liveness probe | `{"status":"ok","timestamp":"..."}` |
| GET | `/health/ready` | Readiness probe (DB check) | `{"status":"ready","users":8,"alerts":42}` |

---

## 10. Frontend — Deep Dive

### 10.1 Design System Overview

The "Dark Intelligence" design system follows banking-app + emergency-system aesthetics:

**Core Rules:**
- No clutter, no heavy animations — clarity first
- Speed feel + trust feel (not flashy)
- Think: *emergency system + Apple-level smoothness*

### 10.2 CSS Architecture (5-file system)

```
static/css/
├── variables.css       ← Design tokens (colors, spacing, fonts, shadows)
├── base.css            ← Reset, typography, scrollbar, utilities
├── layout.css          ← Sidebar, main content grid, responsive
├── components.css      ← Cards, buttons, badges, bars, forms, modals
├── animations.css      ← Keyframes, transitions, entrance effects
└── dark-intelligence.css ← Premium overrides (loads last = wins)
```

### 10.3 Design Token Specification

| Token Category | Spec Value | Usage |
|---|---|---|
| `--bg-ground` | `#0a0c0f` | Page background |
| `--bg-surface` | `#111318` | Cards, panels |
| `--bg-elevated` | `#181c23` | Dropdowns, tooltips |
| `--border-card` | `#1E293B` | Card borders |
| `--text-primary` | `#E5E7EB` | Main readable text |
| `--text-secondary` | `#94A3B8` | Supporting text |
| `--text-muted` | `#4B5563` | Labels, timestamps |
| `--color-critical` | `#EF4444` | Critical status |
| `--color-verified` | `#22C55E` | Verified status |
| `--color-verifying` | `#F59E0B` | Verifying status |
| `--color-new` | `#3B82F6` | New status |
| `--color-awaiting` | `#8B5CF6` | Awaiting review |
| Body font size | `13px` (0.8125rem) | Spec exact |
| Section labels | `11px / uppercase / 0.12em` | Enterprise feel |
| Metric values | `26px / weight 600 / -0.02em` | Dashboard numbers |
| Transition speed | `200ms ease` | Snappy, not slow |

### 10.4 Component Library

**Alert Card** — Left border color-coded by status:
```css
.alert-card.status-critical  { border-left: 2px solid #EF4444; }
.alert-card.status-verified  { border-left: 2px solid #22C55E; }
.alert-card.status-verifying { border-left: 2px solid #F59E0B; }
.alert-card.status-new       { border-left: 2px solid #3B82F6; }
```

**Status Badges:**
```
🔴 Critical   → red bg + red text
🟡 Verifying  → amber bg + amber text
🟢 Verified   → green bg + green text
🔵 New        → blue bg + blue text
⚫ Rejected   → grey bg + grey text
```

**Confidence Bar** — Animated fill with premium easing:
```css
.confidence-fill {
    transition: width 0.8s cubic-bezier(.16, 1, .3, 1);
}
```
JS: `bar.style.width = percent + '%'` triggers CSS animation.

**Vote Buttons** — Transparent by default, color reveals on hover:
```css
.btn-confirm:hover { background: rgba(34,197,94,0.10); color: #22C55E; }
.btn-reject:hover  { background: rgba(239,68,68,0.10);  color: #EF4444; }
```

### 10.5 JavaScript Engine (dark-intelligence.js)

9 self-contained modules in one IIFE — zero dependencies:

| Module | Trigger | What It Does |
|---|---|---|
| **IO Reveal** | Scroll | `.reveal` elements fade up into view |
| **Counter Animation** | Viewport entry | `data-counter="42"` counts up from 0 |
| **Confidence Bar Fill** | Page load | Animates 0 → `data-width`% |
| **SVG Ring** | Page load | `stroke-dashoffset` animation on confidence ring |
| **Scroll Blur** | Scroll | Adds `.scrolled` to body → CSS blurs topbar |
| **Click Ripple** | Any `.btn` click | Expanding circle for tactile feedback |
| **Status Classes** | DOM ready | `data-status="critical"` → adds `.status-critical` class |
| **Evidence Strength** | `#message` input | Live 3-bar quality preview as user types |
| **Toast API** | `CrisisUI.toast()` | Programmatic toast notifications |

**Public API:**
```javascript
CrisisUI.toast("Alert saved successfully", "success");
CrisisUI.toast("Rate limit exceeded", "error");
CrisisUI.toast("Verifying crowd votes...", "info");
```

### 10.6 Template Structure

```
templates/
├── base.html                  ← Master layout (sidebar, nav, flash, WS)
├── auth/
│   ├── login.html             ← Dark premium login form
│   └── register.html          ← Registration form
├── dashboard/
│   ├── admin.html             ← Admin command center
│   ├── user.html              ← Reporter dashboard + badges
│   └── security.html          ← Security map view (Leaflet)
├── alerts/
│   ├── report.html            ← Incident report form
│   ├── detail.html            ← Full detail + timeline + X-Logic
│   └── history.html           ← User's alert history
└── components/
    ├── alert_card.html        ← Reusable alert card partial
    └── confidence_bar.html    ← Live confidence meter
```

### 10.7 Gamification — Reputation Badges

Users earn visible tier badges displayed on their dashboard:

| Tier | Reliability Range | Badge | Color |
|---|---|---|---|
| Crisis Guardian | ≥ 0.90 | 🛡️ | Gold |
| Trusted Reporter | ≥ 0.75 | ⭐ | Silver |
| Community Helper | ≥ 0.60 | 🤝 | Bronze |
| New Member | ≥ 0.40 | 🌱 | Grey |
| Under Review | < 0.40 | ⚠️ | Red |

---

## 11. Real-Time Layer (WebSocket)

### 11.1 Architecture

Flask-SocketIO with **gevent** async mode (required for Python 3.11+):

```python
# extensions.py
from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent')
```

### 11.2 Room Architecture

| Room | Members | Events Received |
|---|---|---|
| `dashboard` | All authenticated users | `new_alert`, `status_change` |
| `alert_{id}` | Users viewing a specific alert | `vote_update`, `confidence_update` |
| `all` | Every connected client | `critical_alert` (broadcast) |

### 11.3 Server-Side Events

```python
# Backend emits:
socketio.emit('new_alert',          alert_data,   room='dashboard')
socketio.emit('vote_update',        vote_data,    room=f'alert_{alert_id}')
socketio.emit('status_change',      status_data,  room='dashboard')
socketio.emit('confidence_update',  conf_data,    room=f'alert_{alert_id}')
socketio.emit('critical_alert',     alert_data,   broadcast=True)
```

### 11.4 Client-Side Handlers

```javascript
// Frontend listens:
socket.on('new_alert', (data) => {
    prependAlertCard(data);     // Add to dashboard top
    updateAlertCount();          // Increment counter badge
    CrisisUI.toast(`New alert: ${data.type}`, 'warning');
});

socket.on('confidence_update', (data) => {
    animateConfidenceBar(data.alert_id, data.new_confidence);
    updateStatusBadge(data.alert_id, data.status);
});

socket.on('critical_alert', (data) => {
    showCriticalBanner(data);   // Top-of-page red banner
});
```

---

## 12. End-to-End Workflows

### 12.1 Report Submission Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as Flask Route
    participant AI as AI Engine
    participant DB as Database
    participant WS as WebSocket
    participant D as Admin Dashboard

    U->>F: POST /alerts/submit (message, location)
    F->>F: Auth check + Rate limit check
    F->>AI: process_alert(message, location)
    AI->>AI: classify → severity → confidence → evidence → explanation
    AI-->>F: {type, severity, confidence, explanation}
    F->>DB: Check for duplicates (Jaccard similarity)
    DB-->>F: No duplicate found
    F->>DB: INSERT alert (status='new')
    F->>DB: INSERT audit_log (ALERT_CREATED)
    F->>WS: emit('new_alert', alert_data, room='dashboard')
    WS->>D: Live push → new card appears
    F-->>U: Redirect to alert detail page
```

### 12.2 Crowd Voting Flow

```mermaid
sequenceDiagram
    participant V as Voter Browser
    participant F as Flask Route
    participant CS as Confidence Service
    participant SM as State Machine
    participant DB as Database
    participant WS as WebSocket

    V->>F: POST /vote/vote/42 {vote: "confirm"}
    F->>DB: Check: has this user already voted? (UNIQUE constraint)
    DB-->>F: No existing vote
    F->>DB: READ voter reliability_score
    F->>DB: INSERT crowd_votes (vote, vote_weight=reliability)
    F->>CS: recalculate_confidence(alert)
    CS->>CS: (AI_base×0.40) + (crowd×0.40) + (bonus×0.20)
    CS-->>F: new_confidence = 0.78
    F->>SM: determine_new_status(alert)
    SM-->>F: "verified"
    F->>DB: UPDATE alert (confidence=0.78, status='verified')
    F->>DB: INSERT audit_log (VOTE_CAST, STATUS_CHANGE)
    F->>WS: emit('confidence_update', {alert_id, new_confidence, status})
    WS->>V: Live confidence bar animates to 78%
```

### 12.3 Alert Resolution & Reliability Update

```
Admin clicks RESOLVE
    │
    ▼
transition_alert(alert, 'resolved', admin_id, note)
    │
    ├── alert.status = 'resolved'
    ├── alert.resolved_at = now()
    ├── alert.resolution_note = note
    │
    ├── audit_service.log("RESOLVED", alert_id, admin_id, note)
    │
    └── reliability_service.update_all_voters(alert)
            │
            ├── For each voter who voted CONFIRM on a VERIFIED/CRITICAL alert:
            │       user.reliability_score += 0.02  (accurate vote)
            │
            └── For each voter who voted REJECT on a VERIFIED/CRITICAL alert:
                    user.reliability_score -= 0.03  (wrong vote)
```

---

## 13. Security & Hardening

### 13.1 Authentication

- **Password hashing:** `werkzeug.security.generate_password_hash()` (PBKDF2-SHA256)
- **Session management:** Flask-Login with `SESSION_COOKIE_SECURE=True` (prod)
- **Role enforcement:** `@login_required` + `@admin_required` decorators on all protected routes

### 13.2 Rate Limiting (Flask-Limiter)

| Endpoint | Limit | Rationale |
|---|---|---|
| Alert submission | 5 / user / 10 min | Prevents flooding AI engine |
| Voting | 20 / IP / min | Prevents vote manipulation |
| Login attempts | 10 / IP / min | Brute-force protection |
| Global default | 200 / day | Catch-all safety net |

### 13.3 Input Validation

- All POST data validated before passing to services
- Photo uploads validated by **Pillow**: format whitelist (JPEG, PNG, WEBP), max 10MB, min 100×100px
- SQL injection: impossible via SQLAlchemy parameterized queries
- XSS: Jinja2 auto-escaping on all template variables

### 13.4 Security Headers (Nginx)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header Referrer-Policy strict-origin-when-cross-origin;
add_header Content-Security-Policy "default-src 'self'; ...";
```

### 13.5 Error Tracking (Sentry)

```python
import sentry_sdk
sentry_sdk.init(
    dsn=app.config.get('SENTRY_DSN'),
    traces_sample_rate=0.2,
    environment=app.config['ENV']
)
```

### 13.6 Structured Logging

Custom `JSONFormatter` outputs machine-readable logs compatible with Datadog/Cloud Logging:

```json
{
  "timestamp": "2026-04-28T06:00:00Z",
  "level": "INFO",
  "logger": "app.routes.alerts",
  "message": "Alert 42 created",
  "alert_id": 42,
  "user_id": 3,
  "severity": 8
}
```

---

## 14. Deployment Guide

### 14.1 Local Development

```bash
# 1. Clone & enter project
git clone <repo-url>
cd CrisisSignal-AI

# 2. Create virtualenv
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum

# 5. Run dev server
python run.py
# App starts at http://localhost:5000
```

### 14.2 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **YES** | Random 32-byte hex string |
| `FLASK_ENV` | YES | `development` / `production` |
| `DATABASE_URL` | Prod only | `postgresql://user:pass@host/db` |
| `POSTGRES_PASSWORD` | Prod only | Database password |
| `SENTRY_DSN` | Optional | Sentry project DSN |
| `LOG_LEVEL` | Optional | `INFO` / `DEBUG` / `WARNING` |
| `JSON_LOGS` | Optional | `true` for structured JSON output |

### 14.3 Docker Production Deployment

**Services (docker-compose.yml):**

| Service | Image | Role |
|---|---|---|
| `app` | Custom multi-stage build | Gunicorn + Flask app |
| `db` | `postgres:16-alpine` | PostgreSQL database |
| `nginx` | `nginx:alpine` | TLS + reverse proxy |

```bash
# 1. Configure .env (all production variables)
cp .env.example .env

# 2. Generate TLS certificates
mkdir -p nginx/certs
# Option A: Let's Encrypt
certbot certonly --standalone -d yourdomain.com
# Option B: Self-signed (testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/privkey.pem \
  -out nginx/certs/fullchain.pem -subj "/CN=localhost"

# 3. Build and start
docker compose up --build -d

# 4. Verify health
curl https://yourdomain.com/health
curl https://yourdomain.com/health/ready
```

### 14.4 SQLite → PostgreSQL Migration

```bash
# 1. Export from SQLite
sqlite3 crisis_dev.db .dump > backup.sql

# 2. Set DATABASE_URL in .env
DATABASE_URL=postgresql://crisissignal:PASSWORD@db:5432/crisissignal

# 3. Run migrations
flask db upgrade

# 4. Re-seed demo users
flask seed
```

### 14.5 Health Check Endpoints

- **`GET /health`** — Liveness probe: returns `{"status":"ok"}` if app is running
- **`GET /health/ready`** — Readiness probe: queries DB, checks seed data present

Used by Docker health checks and Kubernetes/ECS orchestrators.

---

## 15. Build Roadmap

### Phase 0 — Showstopper Fixes

| Fix | Problem | Solution Applied |
|---|---|---|
| Plain-text passwords in seed.py | Security breach if repo is public | `generate_password_hash()` at seed time |
| No rate limiting | Flooding attack possible | Flask-Limiter: 5 alerts/10min per user |
| eventlet + Python 3.13 crash | WebSocket falls back to HTTP polling silently | Switched to `gevent` async mode |

### Phase 1 — Security & Stability Hardening

- CSRF protection on all state-mutating forms
- `@admin_required` decorator on all admin routes
- Input length validation (message ≤ 500 chars)
- `SECRET_KEY` mandatory assertion in ProductionConfig
- HTTP security headers via Nginx
- XSS: Jinja2 auto-escape audit

### Phase 2 — AI Engine Upgrade

- Multi-keyword scoring (not just single keyword match)
- Urgency amplifier system (+3/+1/−1 weights)
- Harm indicator detection (+2 per indicator)
- Location multipliers (+1 per match)
- Evidence score system (0–100)
- X-Logic explanation generator
- Suspicion penalty for prank language

### Phase 3 — Product Feature Upgrades

- Photo evidence upload with Pillow validation
- Drag-and-drop evidence UI
- Emergency flagging on report form
- CSV export (streaming for large datasets)
- Responder assignment (`assigned_to` field)
- Manual user flagging by admin
- Reputation tier badges (5 tiers)
- `AuditLog.alert_id` nullable for global actions

### Phase 4 — Real-World Readiness

- Multi-stage Dockerfile (builder + runtime stages)
- `docker-compose.yml` (app + PostgreSQL + Nginx)
- Sentry SDK integration
- Custom `JSONFormatter` for structured logging
- `ProxyFix` middleware for HTTPS behind Nginx
- HSTS + security headers in `nginx.conf`
- `/health` + `/health/ready` endpoints
- `ProductionConfig` hard assertions
- `dark-intelligence.css` premium UI overrides
- `dark-intelligence.js` micro-interactions engine

---

## 16. SDG Alignment

| SDG | Goal | How CrisisSignal AI Contributes |
|---|---|---|
| **SDG 3** | Good Health & Well-Being | Faster, verified medical emergency response reduces harm from delayed treatment |
| **SDG 11** | Sustainable Cities & Communities | Structured crisis communication for campuses, hostels, public venues |
| **SDG 16** | Peace, Justice & Strong Institutions | Immutable audit trails, accountable reporting, anti-prank trust mechanisms |

---

## 17. Demo Plan (5 Minutes — Judge Script)

### Setup (Pre-demo)
- Browser open at admin dashboard
- 3 demo accounts ready: admin, student, security
- Demo mode: 5 simulated users with preset reliability scores

### 0:00–0:30 — Open with the Trust Promise
*Say:* "CrisisSignal AI is not a one-shot alarm system. It earns trust through a visible verification lifecycle." Point to status labels: `New → Verifying → Verified → Critical`.

### 0:30–2:15 — Demo A: Fire Alert (Verified Path)

1. Login as `student_alpha` → Report: *"Heavy smoke from staircase, burning smell, people running, floor 3"*
2. Show AI result: `FIRE | Severity 8 | Confidence 0.65 | Status: Verifying`
3. Show X-Logic: *"Detected: smoke, burning smell. Urgency: people running."*
4. Cast 3 crowd confirms (mock users: u_hero, u_watch, u_skeptic)
5. Confidence bar animates: 0.65 → 0.73 → **0.82 → Verified** ✅
6. Dashboard status badge changes live via WebSocket

### 2:15–4:30 — Demo B: Suspicious Alert → Critical

1. Login as `student_beta` → Report: *"Crowd screaming, someone said bomb... not sure if joke. People panicking."*
2. Show AI result: `Confidence 0.46 | Suspicion penalty applied | Status: Verifying`
3. Mixed votes: u_prank confirms, u_skeptic rejects, u_hero confirms, u_watch confirms
4. Confidence rises despite prank language: *"Evidence-driven — not keyword-only"*
5. Add 2 more confirms → **Confidence 0.88, Severity 8 → AUTO-ESCALATES TO CRITICAL** 🔴
6. Show critical banner + notification

### 4:30–5:00 — Close: System Behavior Over Time
- Show audit log: every vote, every state change, timestamped
- Show reliability scores: u_prank declining, u_hero increasing
- *"The system trains itself — prank users lose influence over time"*

### Demo User Profiles

| User | Reliability | Role | Notes |
|---|---|---|---|
| `u_hero` | 0.90 | Security | Highest influence — 3.6× prank weight |
| `u_watch` | 0.70 | Student | Reliable regular user |
| `u_skeptic` | 0.60 | Student | Reliable rejector for drills |
| `u_random` | 0.50 | Student | Neutral new user |
| `u_prank` | 0.25 | Student | Low influence — known prankster |

---

## 18. Future Roadmap

### Near-Term (Next 3 Months)

| Feature | Description |
|---|---|
| **ML Classifier Upgrade** | Replace rule-based NLP with fine-tuned `distilbert-base-uncased` for 15–20% accuracy improvement |
| **Mobile App (PWA)** | Progressive Web App with offline report queuing + push notifications |
| **GPS Integration** | Browser Geolocation API for auto-location capture |
| **WhatsApp Bot** | Twilio-powered WhatsApp reporting channel |
| **Multi-Institution** | Multi-tenant support — separate campuses in one deployment |

### Medium-Term (3–6 Months)

| Feature | Description |
|---|---|
| **Predictive Escalation** | Time-series analysis of confidence trajectories to pre-warn before threshold |
| **Heatmap Analytics** | Historical incident density maps per campus zone |
| **Integration API** | Webhook delivery of critical alerts to external systems |
| **Responder App** | Native mobile app for security personnel with one-tap status updates |

### ML Upgrade Path

The AI engine is designed for seamless ML integration:

```python
# Current (rule-based):
result = classify_text(message)   # keyword matching

# Future (ML):
from app.ml.classifier import MLClassifier
result = MLClassifier.predict(message)  # fine-tuned transformer
# Same interface — drop-in replacement, zero route changes needed
```

---

## 19. Risk Analysis

| Risk | Level | Impact | Mitigation Applied |
|---|---|---|---|
| **Fake alert flooding** | HIGH | Crashes trust system | Rate limiting 5/10min + User Reliability Score degradation |
| **Prankster manipulation** | HIGH | Dashboard noise, real alerts ignored | Suspicion penalty + crowd rejection + account flagging |
| **Weak AI (keyword-only)** | MEDIUM | Technical judges see shallow classification | Multi-stage pipeline + X-Logic makes reasoning defensible |
| **No real users in demo** | MEDIUM | Crowd verification looks empty | Demo mode with 5 pre-seeded reliability-scored users |
| **CRUD perception** | HIGH | Judges dismiss as basic app | Dynamic confidence + live WebSocket updates + state machine lifecycle |
| **Privacy/anonymity** | MEDIUM | Users won't report sensitive incidents | Anonymous reporting option (stored internally, not shown to peers) |
| **Scalability** | LOW (demo) | Performance degradation at scale | PostgreSQL + Gunicorn workers + Nginx ready; Redis cache documented |
| **TLS/HTTPS** | LOW (prod) | Man-in-the-middle attacks | Nginx HTTPS + HSTS + Let's Encrypt documented |

---

## 20. Glossary

| Term | Definition |
|---|---|
| **Alert** | A reported incident record that evolves through defined lifecycle states |
| **Confidence Score** | A 0.0–1.0 trust metric combining AI evidence, crowd votes, and reporter reliability |
| **Crowd Vote** | A user's confirm or reject action on an alert, weighted by their reliability score |
| **Evidence Score** | A 0–100 signal-quality metric calculated from keyword density, urgency, and harm indicators |
| **Reliability Score** | A per-user 0.0–1.0 self-learning credibility metric updated based on reporting accuracy |
| **State Machine** | The formal set of lifecycle states and allowed transitions that govern every alert |
| **X-Logic** | The human-readable explanation attached to every alert explaining AI reasoning |
| **Duplicate Detection** | Jaccard similarity algorithm that merges related reports into one alert thread |
| **Alert Lifecycle** | `new → awaiting_review → verifying → verified → critical → resolved` |
| **Triangulated Trust** | Confidence formula: AI_base × 0.40 + crowd_consensus × 0.40 + reliability_bonus × 0.20 |
| **Weighted Vote** | A vote whose influence equals the voter's current reliability score |
| **Suspicion Penalty** | Confidence reduction applied when prank/fake language is detected |
| **ProxyFix** | WSGI middleware that correctly reads client IP when behind an Nginx reverse proxy |
| **Liveness Probe** | `/health` endpoint confirming the app process is running |
| **Readiness Probe** | `/health/ready` endpoint confirming the app can serve traffic (DB seeded) |
| **Gevent** | Python async library required for Flask-SocketIO WebSocket support on Python 3.11+ |
| **HSTS** | HTTP Strict Transport Security — forces HTTPS-only connections for 1 year |
| **JSONFormatter** | Custom Python logging formatter producing machine-readable structured log lines |
| **Dark Intelligence** | The "Dark Command Center" UI design system used across all CrisisSignal dashboards |

---

<p align="center">
  <strong>CrisisSignal AI — Master Technical Documentation</strong><br/>
  <em>GDG Solution Challenge 2026 | Built with purpose. Designed to be trusted.</em>
</p>
