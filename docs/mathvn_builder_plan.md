# Toán Socratic Learning Platform
## AI Builder Flow — Full Project Plan

> A 7-step plan to design, build, and deploy an AI-powered Vietnamese math tutor for Grade 12 students — applying the Socratic method with interactive 3D visualization.

| | |
|---|---|
| **Target users** | Grade 12 students (VN) |
| **Core AI feature** | Socratic dialogue engine |
| **Differentiator** | 3D geometry visualizer |
| **Build timeline** | 4 sprints (~8 weeks) |

---

## Table of Contents

1. [Problem Brief](#step-01--problem-brief)
2. [PRD — Product Requirements](#step-02--prd--product-requirements)
3. [Data Collection & Preparation](#step-03--data-collection--preparation)
4. [Architecture & Tech Stack](#step-04--architecture--tech-stack)
5. [Build — Sprint Plan](#step-05--build--sprint-plan)
6. [Deploy & Operate](#step-06--deploy--operate)
7. [Demo & Final Report](#step-07--demo--final-report)

---

## Step 01 — Problem Brief

> **Understand the user before writing code.**
> Define who we're building for, what pain we're solving, and how we're different from what already exists.

### User Personas

#### Nguyễn Minh Khoa
*Grade 12 student · Hanoi or HCMC · 17 years old*

**Daily problem:** Struggles to understand *why* math solutions work, not just how to execute them. Has access to answer keys and worked solutions but cannot bridge the gap between a memorized procedure and a problem he hasn't seen before.

**Context:** Preparing for the THPT national exam. Uses Zalo, YouTube, and TikTok daily. Studies 2–3 hours per night. Already uses HOCMAI or Vuihoc for video lessons but feels passive — he watches but doesn't understand deeply.

**3D geometry pain:** Cannot visualize solids from flat diagrams. When a problem says "a pyramid with apex S and base ABCD…" he draws something wrong, then the whole solution collapses.

---

#### Trần Thị Lan
*Grade 12 student · Provincial city · 17 years old*

**Daily problem:** Has no access to quality tutors. Family can't afford premium tutoring centers. Relies entirely on self-study with textbooks. When stuck, she watches YouTube videos but generic content isn't aligned to her specific curriculum gap.

**Context:** Self-motivated but isolated. Needs a patient, always-available tutor who won't make her feel judged for asking "dumb questions." Mobile-first — her phone is her primary device.

**Willingness to pay:** Low individually; but if the platform is good enough, parents will pay — they already spend heavily on education.

---

### Problem Statement

Vietnamese Grade 12 students preparing for the THPT exam have access to video lessons and answer keys, but no tool that *actively teaches* them to reason — the skill the new exam format now explicitly tests. They can memorize procedures but cannot think flexibly under novel problem conditions.

---

### Competitor Analysis

| Product | Does well | Falls short | Our edge |
|---|---|---|---|
| **HOCMAI / Vuihoc** | Large content library, THPT-aligned video lessons, trusted brand | Passive video watching; no dialogue; no adaptive feedback; no visualization | Active Socratic dialogue vs. passive video |
| **Photomath / Socratic App** | Instant step-by-step solutions, photo input, free | Hands answers — kills reasoning development; not Vietnamese; no 3D | Guides to answer vs. giving it; curriculum-specific |
| **ChatGPT / Gemini** | Flexible, can explain concepts, multilingual | Not aligned to THPT; tendency to give full solutions; no visualization; no session structure | Structured Socratic loop + integrated 3D visualizer |
| **Khan Academy / Khanmigo** | Excellent Socratic AI tutor, proven pedagogy | No Vietnamese language; not aligned to THPT; no 3D geometry focus | Vietnamese, THPT-specific, 3D-first for geometry |

---

## Step 02 — PRD — Product Requirements

> **Turn the brief into a concrete spec.**
> User stories, feature priorities, and wireframe descriptions that define what we build and in what order.

### User Stories

**[Student]** As a Grade 12 student, I want to **ask a math question in Vietnamese and receive guiding questions back** — not a direct answer — so that I arrive at the solution myself and actually understand it.

**[Student]** As a student struggling with 3D geometry, I want to **interact with a rotatable 3D model of the solid in my problem** so that I can see spatial relationships I couldn't imagine from the flat diagram.

**[Student]** As a student with a specific weak topic (e.g. limits, trigonometry), I want the platform to **identify my gap from my conversation history** and suggest focused practice sessions so I'm not wasting time on things I already know.

**[Student]** As a student on my phone, I want to **take a photo of a textbook problem** and start a Socratic session on it so I don't have to retype the problem manually.

**[Admin / Teacher]** As an admin, I want to **view aggregate usage data and common error patterns** across student sessions so I can improve the AI's dialogue quality over time.

---

### Feature Priority Matrix (MoSCoW)

#### 🔴 Must Have — MVP
- Socratic dialogue engine (Vietnamese)
- THPT Grade 12 curriculum scope
- Session history & continuity
- 3D geometry visualizer (pyramids, prisms, spheres)
- User auth (register / login)
- Topic selection & session start flow

#### 🟡 Should Have — v1.1
- Photo / OCR problem input
- Weakness detection & topic suggestions
- Progress / concept mastery map
- Math formula rendering (KaTeX)
- Hint escalation system (3 levels)

#### 🟢 Could Have — v2
- Worked example library (post-Socratic)
- Parent dashboard
- Teacher / class management
- Gamification (streaks, badges)
- Grade 10–11 expansion

#### ⬜ Won't Build Yet
- Exam mode / mock tests
- Peer collaboration
- Live video tutoring
- Native mobile app

---

### Wireframe Descriptions — Core Screens

| Screen | Layout description | Key interactions |
|---|---|---|
| **Home / Topic picker** | Grid of math topic cards (Giải tích, Hình học, Xác suất…). Each card shows topic name, chapter count, and a difficulty badge. Search bar at top. | Tap a card → chapter list → problem picker or free-ask entry |
| **Chat / Socratic session** | Split layout: left 60% is conversation thread (student messages right, AI messages left with a distinctive style). Right 40% is context panel — shows LaTeX-rendered problem statement, a visualization pane (3D or graph), and session progress. | Type or speak message; request hint; trigger visualizer; end session |
| **3D Geometry viewer** | Full-width interactive Three.js canvas. Controls: rotate (drag), zoom (scroll), slice plane (slider), show/hide labels, step-by-step construction mode (plays through drawing the figure). | Triggered inline from chat when a geometry problem is detected; can also open standalone |
| **Session summary** | Card showing: concept identified, questions asked by AI, moments of breakthrough (where student got it right after hints), suggested next topic. Option to review conversation. | Save to history; start related session; share with teacher |
| **Dashboard (student)** | Left sidebar navigation. Main area: weekly activity chart, mastery radar chart across 6 main topic groups, recently studied, and AI-suggested next session. | Click topic in radar → go to topic; click session in history → review transcript |

---

## Step 03 — Data Collection & Preparation

> **Source and structure the data the AI needs.**
> Raw data is never ready. Every input needs collection, cleaning, and validation before it powers the AI.

> **Strategy:** Start with a small, high-quality synthetic dataset to validate the Socratic dialogue engine. Don't wait for "real data" to start building — real data follows the working product.

### Data Pipeline

**Curriculum scope**
*Source:* Vietnam Ministry of Education Grade 12 Math syllabus (publicly available).
*Action:* Extract topic tree (chapters → concepts → problem types) and encode as structured JSON. This becomes the navigation schema for the entire app.

**Problem bank**
*Source:* THPT past exam papers (2018–2025), textbook exercises (Sách giáo khoa Toán 12).
*Action:* Manually curate 200–300 high-quality problems, tag each by topic, subtopic, difficulty, and problem type. Store as structured JSON with LaTeX-formatted expressions.

**Socratic dialogues**
*Source:* Synthetic generation using Claude API.
*Action:* For each problem in the bank, generate 3–5 Socratic dialogue examples — AI asks guiding questions, student makes mistakes, AI rectifies without giving the answer. Use as few-shot examples in the system prompt. Target: 500–1000 dialogue turns before launch.

**3D geometry models**
*Source:* Procedurally generated using Three.js + code.
*Action:* For each geometry problem type (pyramid, prism, cone, sphere, composite solids), write parameterized renderers that generate the 3D model from problem data (dimensions, labels, relationships). No static models — everything generated from parameters.

**Common misconceptions**
*Source:* Teacher interviews (3–5 math teachers), Vietnamese math forums (toán học tuổi thơ), THPT exam analysis reports.
*Action:* Catalog the 30–50 most common student errors per topic. Feed into AI system prompt as "known mistakes to watch for." This is what makes the Socratic tutoring feel smart.

**User session logs**
*Source:* Collected once the platform launches (pilot users).
*Action:* Log conversation turns, topics, hint requests, session duration, and post-session ratings. Used iteratively to improve dialogue quality. Start logging from day one — data is an asset.

---

### Validation Rules

| Data type | Validation check | Rejection criteria |
|---|---|---|
| Problem bank | LaTeX renders without error; topic tag exists in curriculum tree; answer is verified | Ambiguous problem statement; missing tags; unverified answer |
| Synthetic dialogues | AI never reveals the full solution in a single turn; at least 3 Socratic turns before answer is reachable | Dialogue that hands the answer; dialogue with hallucinated math steps |
| 3D models | Model loads in < 1s on mobile; all labels visible; dimensions match problem parameters | Rendering error; label overlap; mismatched dimensions |

---

## Step 04 — Architecture & Tech Stack

> **Design the full system before writing code.**
> Frontend, backend, AI pipeline, database, and auth — every layer decided before implementation begins.

### System Architecture

```
Frontend — Client
  Next.js 14 (React) | Three.js — 3D visualizer | KaTeX — math rendering | Tailwind CSS

          ↓ REST / WebSocket ↓

Backend — API Server
  FastAPI (Python) | Auth: NextAuth / JWT | Session manager | Problem resolver

          ↓ SDK calls ↓

AI Pipeline
  Claude API (claude-sonnet-4-6) | Socratic system prompt | RAG — problem context injection | Misconception catalog

          ↓ Read / Write ↓

Database & Storage
  PostgreSQL — users, sessions, progress | Pinecone / pgvector — problem embeddings | S3 / Cloudflare R2 — assets
```

---

### Tech Stack Rationale

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | Next.js 14 | SSR for SEO; App Router for clean layout nesting; strong React ecosystem for Three.js and KaTeX integration |
| 3D rendering | Three.js | Best-in-class WebGL; procedural geometry from parameters; works in browser without install |
| Math rendering | KaTeX | Faster than MathJax; inline rendering in chat bubbles; Vietnamese-compatible |
| Backend | FastAPI (Python) | Easy Claude SDK integration; async streaming; fast prototyping; team likely Python-fluent |
| AI model | Claude claude-sonnet-4-6 | Strong reasoning for math; excellent Vietnamese; streaming responses; tool use for visualizer triggers |
| Database | PostgreSQL + pgvector | Relational for users/sessions; vector search for similar problem retrieval without separate infra |
| Auth | NextAuth.js | Easy Google/Facebook OAuth; Vietnamese students already have Google accounts; JWT session handling |

---

### Database Schema (core tables)

**Table: users**

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | primary key |
| name | text | display name |
| email | text | unique, indexed |
| role | enum | student \| admin |
| created_at | timestamp | |

**Table: sessions**

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK | → users |
| topic_id | text | e.g. "hinh-hoc.hinh-chop" |
| problem_id | uuid FK | → problems (nullable) |
| messages | jsonb | full conversation array |
| status | enum | active \| completed \| abandoned |
| hint_count | int | how many hints were requested |
| started_at / ended_at | timestamp | |

**Table: problems**

| Field | Type | Notes |
|---|---|---|
| id | uuid PK | |
| topic_id | text | curriculum tree reference |
| statement_latex | text | KaTeX-formatted problem |
| difficulty | enum | easy \| medium \| hard |
| geometry_params | jsonb | null if not geometry; else 3D model params |
| answer | text | verified answer (not shown to student) |
| embedding | vector(1536) | pgvector for similarity search |

**Table: progress**

| Field | Type | Notes |
|---|---|---|
| user_id | uuid FK | → users |
| topic_id | text | curriculum node |
| mastery_score | float | 0.0 – 1.0, updated per session |
| sessions_count | int | |
| last_practiced | timestamp | for spaced repetition suggestions |

---

### API Endpoints (core)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/sessions` | Start a new Socratic session for a topic/problem |
| `POST` | `/api/sessions/:id/message` | Send student message, receive streaming AI response |
| `GET` | `/api/sessions/:id` | Retrieve session history and status |
| `PUT` | `/api/sessions/:id/complete` | Mark session complete, update progress scores |
| `GET` | `/api/problems?topic=&difficulty=` | Fetch problems filtered by topic and difficulty |
| `GET` | `/api/progress/:userId` | Get full mastery map for a user |
| `GET` | `/api/geometry/:problemId` | Return 3D model parameters for a geometry problem |
| `GET` | `/api/admin/stats` | Admin: usage analytics, common errors, session metrics |

---

## Step 05 — Build — Sprint Plan

> **Ship incrementally. AI feature first, UI second.**
> Four focused sprints, each building on the last. A working demo exists at the end of every sprint.

> ⚠️ **Rule:** Sprint 1 is AI-only. Do not spend any time on UI polish in Sprint 1. A CLI or raw API test that proves the Socratic dialogue works is worth more than a beautiful interface on top of a broken AI.

---

### Sprint 1 — Socratic AI Engine *(Weeks 1–2)*

- Design Socratic system prompt in Vietnamese
- Implement dialogue state machine (review → hint → rectify → summarize)
- Integrate Claude API with streaming
- Build problem context injection (RAG from problem bank)
- Load misconception catalog into system prompt
- Test: 10+ complete Socratic sessions via CLI/Postman
- **Gate:** AI never reveals full answer in 1 turn ✓

### Sprint 2 — Core UI + 3D Viewer + Auth *(Weeks 3–4)*

- Next.js project setup + Tailwind + KaTeX
- Auth flow: Google OAuth via NextAuth
- Chat UI with streaming AI responses
- Three.js 3D geometry viewer (pyramid, prism, sphere)
- Topic picker and problem selector screens
- PostgreSQL + session persistence
- **Gate:** End-to-end session works in browser ✓

### Sprint 3 — Progress, Roles & Polish *(Weeks 5–6)*

- Student dashboard with mastery radar chart
- Session summary screen (post-session review)
- Admin dashboard: usage stats, error patterns
- Hint escalation system (3 levels of help)
- Progress tracking and mastery score updates
- Mobile-responsive layout
- **Gate:** Two roles work; data persists ✓

### Sprint 4 — UX Polish, Testing & Launch Prep *(Weeks 7–8)*

- Full mobile responsiveness pass
- Error state handling (API failures, empty states)
- Loading states and skeleton screens
- Performance: lazy-load 3D viewer, optimize bundle
- 5–10 real student pilot users → collect feedback
- Bug fixes from pilot feedback
- **Gate:** Pilot users return for a second session ✓

---

### Git & Code Standards

| Practice | Standard |
|---|---|
| Branch naming | `feat/socratic-engine`, `fix/three-geometry-labels`, `chore/db-schema` |
| Commit messages | Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:` |
| PR requirement | At least one review before merging to main; no direct pushes to main |
| Env vars | All secrets in `.env.local`; never committed; `.env.example` in repo |

---

## Step 06 — Deploy & Operate

> **"Works on my machine" is not acceptable.**
> The product must run on a real public URL with SSL, monitoring, and real users testing it before the demo.

### Deployment & Infrastructure

🚀 **Frontend — Vercel**
Deploy Next.js to Vercel. Automatic CI/CD from main branch. Free SSL. Preview deployments for each PR. Custom domain when ready.

⚙️ **Backend — Railway**
FastAPI on Railway. Managed PostgreSQL with pgvector extension. Environment variables via Railway dashboard. Auto-restart on crash.

📊 **Monitoring — Sentry**
Sentry free tier for error tracking on both frontend and backend. Know when something breaks before users report it. Log AI API failures separately.

📝 **Logging — Railway logs**
Structured logging with timestamps on every API call. Log session starts, AI response times, and error types. Review weekly during sprint 4.

🧪 **Pilot testing**
Recruit 10–15 Grade 12 students (friends, Facebook groups, school contacts). Give them 2 weeks of free access. Collect feedback via Google Form after each session.

🔁 **Feedback loop**
Weekly sync to review pilot feedback, Sentry errors, and session analytics. Fix the top 3 issues each week. Track whether users return voluntarily — the key success signal.

---

### Success Metrics for Pilot

| Metric | Target | Why it matters |
|---|---|---|
| Session completion rate | > 60% | Students start and finish sessions, not just drop out |
| Return rate (week 2) | > 40% | Voluntary return = the core loop has real value |
| Average session length | 12–20 min | Too short = not engaging; too long = frustrating |
| Hint request rate | 1–3 hints/session | Calibrates dialogue difficulty — too many hints = problems too hard |
| 3D viewer engagement | > 70% of geometry sessions | Validates the 3D visualizer is genuinely useful, not just decorative |

---

## Step 07 — Demo & Final Report

> **Present live on the production URL.**
> No slides, no recorded video, no localhost. The product runs in front of the panel on the real URL.

### Demo Flow (10–12 minutes)

```
1. Problem       →   2. Solution      →   3. Architecture   →   4. Live demo       →   5. Lessons
   Who & what           How it               Key tech              Real URL,              What you'd
   pain                 solves it            decisions             real session           do differently
```

---

### Live Demo Script

| Step | What to demo | What to highlight |
|---|---|---|
| 1. Login | Google OAuth → student dashboard | Mastery radar chart showing progress state |
| 2. Pick a problem | Select Hình học không gian → pyramid volume problem | Curriculum alignment, difficulty level |
| 3. Socratic session | Deliberately give a wrong first answer. Show AI asking a guiding question, not giving the answer. | The Socratic dialogue — this is the core differentiator |
| 4. 3D visualizer | Trigger the 3D pyramid viewer mid-session. Rotate it, show the cross-section tool. | Interactive 3D that no competitor has |
| 5. Session summary | Complete the session, show the summary card and updated mastery score | Closes the learning loop — student sees their progress |
| 6. Admin view | Switch to admin account, show session analytics and common error patterns | Two roles, data-driven improvement capability |

---

### Minimum Product Checklist

- [ ] Web app deployed at real public URL (Vercel + Railway)
- [ ] Google OAuth login and registration working
- [ ] Two roles: student and admin, with distinct views
- [ ] Socratic dialogue engine working in Vietnamese with streaming
- [ ] 3D geometry viewer functional for at least 3 solid types
- [ ] Session history persists across logins
- [ ] Student progress / mastery map displayed on dashboard
- [ ] Mobile responsive — usable on a phone
- [ ] Sentry error monitoring active
- [ ] GitHub repo: clean code, README with setup + deploy guide
- [ ] Live demo possible without localhost or personal environment
- [ ] At least 5 real students have used the platform before demo day

---

### GitHub Repository Structure

```
/ root
├── frontend/               # Next.js app
│   ├── app/                # App Router pages
│   ├── components/         # Chat, Viewer, Dashboard
│   └── lib/                # API clients, hooks
├── backend/                # FastAPI app
│   ├── routers/            # sessions, problems, progress
│   ├── ai/                 # Socratic engine, prompts
│   └── db/                 # models, migrations
├── data/                   # Problem bank JSON, curriculum tree
├── README.md               # Setup, architecture, deploy guide
└── .env.example            # All required env vars documented
```

---

*Toán Socratic — AI Builder Plan · 7 steps · 4 sprints · 8 weeks · 1 live product*
