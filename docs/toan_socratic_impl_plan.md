# Toán Socratic — Implementation Plan

**Vietnamese AI Math Tutor for Grade 12 · v1.0**

> A full engineering specification for building the Toán Socratic platform — Socratic dialogue engine, 3D geometry visualizer, API contracts, database schema, frontend architecture, and an 8-week sprint plan.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Socratic Engine Specification](#2-socratic-engine-specification)
3. [API Specification](#3-api-specification)
4. [3D Geometry Visualizer](#4-3d-geometry-visualizer)
5. [Database Schema](#5-database-schema)
6. [Frontend Architecture](#6-frontend-architecture)
7. [8-Week Sprint Plan](#7-8-week-sprint-plan)
8. [Environment & Testing](#8-environment--testing)

---

## 1. System Architecture

### Stack Overview

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 14, React, Tailwind CSS | Chat UI, topic browser, dashboard |
| Math rendering | KaTeX + react-katex | Inline LaTeX in chat messages |
| 3D visualization | Three.js + CSS2DRenderer | Interactive 3D geometry viewer |
| Backend | FastAPI (Python 3.11) + Uvicorn | REST API, session management, auth |
| AI | Claude claude-sonnet-4-6 (Anthropic API) | Socratic dialogue engine |
| Auth | NextAuth.js + Google OAuth + JWT | User sessions, role enforcement |
| Database | PostgreSQL 15 + pgvector | Users, sessions, problems, progress |
| Cache | Redis | Active session state, rate limiting |
| Storage | Cloudflare R2 | Static assets, OCR uploads |
| Frontend deploy | Vercel | CDN, CI/CD, preview deploys |
| Backend deploy | Railway | FastAPI + PostgreSQL + Redis managed |
| Monitoring | Sentry | Error tracking on frontend and backend |
| CI/CD | GitHub Actions | Lint, test, auto-deploy on merge to main |

---

### Layer Diagram

```
┌─────────────────────────── CLIENT LAYER ───────────────────────────┐
│  Chat UI (Next.js)  │  3D Viewer (Three.js)  │  Dashboard (Recharts) │
└────────────────────────────────┬───────────────────────────────────┘
                                 │  HTTPS / Server-Sent Events
┌────────────────────────────────▼───────────────────────────────────┐
│                          API LAYER (FastAPI)                        │
│   Session Manager  │  Auth Middleware  │  Problem Resolver (RAG)   │
└────────────────────────────────┬───────────────────────────────────┘
                                 │  Anthropic SDK
┌────────────────────────────────▼───────────────────────────────────┐
│                         AI PIPELINE                                 │
│   Socratic Engine  │  Context Builder  │  Misconception Catalog    │
│   claude-sonnet-4-6           Tool Use: render_geometry            │
└────────────────────────────────┬───────────────────────────────────┘
                                 │  SQLAlchemy / asyncpg
┌────────────────────────────────▼───────────────────────────────────┐
│                         DATA LAYER                                  │
│  PostgreSQL + pgvector  │  Redis Cache  │  Cloudflare R2           │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Data Flow — One Socratic Turn

```
Student types message
      │
      ▼
ChatPanel → POST /api/sessions/:id/message
      │
      ▼
FastAPI: validate JWT → load session history from DB
      │
      ▼
RAG Builder: retrieve problem statement + misconceptions
      │
      ▼
Anthropic SDK: send [system_prompt + history + new message] to Claude
      │
      ▼
Claude: streams response tokens
      │
      ├── If tool_use (render_geometry) → emit SSE event: tool_use
      │                                         └─→ GeometryViewer renders 3D
      │
      └── Text tokens → emit SSE event: delta → ChatPanel streams to screen
                              │
                              ▼
                        event: done → save to DB → update dialogue_state
```

---

## 2. Socratic Engine Specification

### Dialogue State Machine

The AI moves through four states in sequence. It can loop back from `RECTIFY` to `HEURISTIC` up to 3 times before escalating the hint level.

```
REVIEW → HEURISTIC → RECTIFY ─(loop max 3×)─┐
                         └────────────────────┘
                              │ (after 3 fails OR student solves)
                              ▼
                          SUMMARIZE
```

| State | AI Behavior |
|---|---|
| `REVIEW` | Restates the problem, asks what the student already knows |
| `HEURISTIC` | Asks guiding sub-questions to break the problem into steps |
| `RECTIFY` | Student made an error — AI identifies it without solving, asks why |
| `SUMMARIZE` | Student solved it — AI confirms and generalizes the concept |

---

### Hint Escalation System

| Level | Trigger | What the AI does | Example (Vietnamese) |
|---|---|---|---|
| `L0` Pure Socratic | Default | Only asks questions. States nothing directly. | *"Góc giữa SA và mặt đáy là gì? Bạn tính nó bằng cách nào?"* |
| `L1` Guided Hint | 2+ failed attempts | Names the specific theorem needed, then asks. | *"Hãy nghĩ đến định lý Pythagoras trong tam giác SAH. Em xác định được H chưa?"* |
| `L2` Scaffolded Hint | Student requests hint OR 3+ failures | Provides first calculation step explicitly. Student completes the rest. | *"AH = AB/2 = 3cm. Từ đây, em tính SA như thế nào?"* |
| `L3` Full Solution | Student types "Mình chịu rồi" or equivalent | Full worked solution shown. Immediately followed by a similar problem. | Full solution + *"Bây giờ hãy thử bài tương tự này…"* |

---

### System Prompt Architecture

The system prompt is the most critical engineering artifact. Draft, test, and iterate on it before building any UI.

```
# VAI TRÒ
Bạn là gia sư Toán Socratic cho học sinh lớp 12 Việt Nam đang ôn thi THPT.
Nhiệm vụ: giúp học sinh TỰ TÌM RA đáp án — không bao giờ đưa ra giải pháp trực tiếp.

# NGUYÊN TẮC BẮT BUỘC
1. KHÔNG BAO GIỜ đưa ra đáp án hoặc lời giải hoàn chỉnh trong một lượt,
   trừ khi học sinh đã yêu cầu gợi ý L3.
2. MỌI phản hồi phải chứa ít nhất một câu hỏi dẫn dắt.
3. Khi học sinh sai: không nói "sai", hỏi "Tại sao em nghĩ [kết quả đó]?"
4. Ngôn ngữ: Tiếng Việt, thân thiện, kiên nhẫn.
   Xưng "thầy/cô", gọi học sinh là "em".
5. Toán học: viết biểu thức theo LaTeX trong dấu $…$ hoặc $$…$$.

# PHÁT HIỆN HÌNH HỌC KHÔNG GIAN
Nếu bài toán liên quan đến hình chóp, lăng trụ, hình hộp, hình cầu, hình nón, hình trụ:
→ GỌI TOOL render_geometry với tham số từ đề bài.
→ Sau khi render: "Em nhìn vào hình 3D, em thấy điểm H nằm ở đâu?"

# TRẠNG THÁI DIALOGUE (injected per turn)
Hiện tại: {{dialogue_state}}     (REVIEW | HEURISTIC | RECTIFY | SUMMARIZE)
Số lần thất bại: {{fail_count}}
Mức gợi ý: {{hint_level}}        (0 | 1 | 2 | 3)

# NGỮ CẢNH BÀI TOÁN (injected per session)
Chủ đề: {{topic}}
Đề bài: {{problem_statement}}
Lỗi phổ biến cần để ý: {{misconceptions}}

# VÍ DỤ PHẢN HỒI
✓ Tốt:   "Em tính được AH = 3cm rồi. Từ đó, em dùng định lý nào để tìm SA?"
✗ Tránh: "Áp dụng Pythagoras: SA² = SH² + AH² = 16 + 9 = 25, vậy SA = 5."
```

---

### Claude Tool Use — Geometry Trigger

```python
GEOMETRY_TOOL = {
    "name": "render_geometry",
    "description": (
        "Renders an interactive 3D geometry figure for the student. "
        "Call this whenever the problem involves 3D solids."
    ),
    "input_schema": {
        "type": "object",
        "required": ["solid_type", "params"],
        "properties": {
            "solid_type": {
                "type": "string",
                "enum": ["pyramid", "prism", "cone", "sphere", "cylinder", "composite"]
            },
            "params": {
                "type": "object",
                "description": (
                    "Geometric parameters: base dimensions, height, "
                    "vertex labels (A,B,C…), apex label (S), "
                    "special points to highlight (foot of altitude H, etc)"
                )
            },
            "highlight_elements": {
                "type": "array",
                "description": "List of edges/faces/points to highlight",
                "items": {"type": "string"}
            },
            "show_altitude": {
                "type": "boolean",
                "description": "Whether to draw the altitude from apex to base"
            }
        }
    }
}
```

---

## 3. API Specification

All endpoints except `POST /auth/*` require `Authorization: Bearer <JWT>` header. Admin endpoints additionally check `role === "admin"` in the token payload.

---

### Session Endpoints

#### `POST /api/sessions` — Start a new Socratic session

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `topic_id` | string | ✓ | Curriculum node, e.g. `hinh-hoc.hinh-chop` |
| `problem_id` | uuid | — | Specific problem to work on; omit for free-ask mode |
| `initial_message` | string | — | Student's opening question |

**Response `201`:**

| Field | Type | Description |
|---|---|---|
| `session_id` | uuid | Use for all subsequent calls |
| `first_message` | string | AI's opening Socratic question |
| `geometry_params` | object\|null | 3D model params if geometry problem; null otherwise |

---

#### `POST /api/sessions/:id/message` — Send a message, receive streamed response

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | ✓ | Student's message |
| `hint_requested` | boolean | — | True if student clicked hint button |

**Response — Server-Sent Events stream:**

| Event | Payload | Description |
|---|---|---|
| `delta` | string | Streamed text chunk from Claude |
| `tool_use` | object | Geometry render trigger: `{solid_type, params}` |
| `done` | object | Final metadata: `{dialogue_state, hint_level, tokens_used}` |

---

#### `GET /api/sessions/:id` — Retrieve session history

**Response `200`:**

| Field | Type | Description |
|---|---|---|
| `session` | object | `id`, `topic_id`, `status`, `dialogue_state`, `hint_level`, `hint_count` |
| `messages` | array | `[{role, content, timestamp, tool_calls?}]` |
| `problem` | object\|null | Full problem object if session is problem-linked |

---

#### `PUT /api/sessions/:id/complete` — Mark session complete

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `student_rating` | int 1–5 | — | Self-rated understanding |

**Response `200`:**

| Field | Type | Description |
|---|---|---|
| `summary` | string | AI-generated session summary |
| `mastery_delta` | float | Change in mastery score for this topic |
| `next_suggested_topic` | string | AI-suggested next topic |

---

### Problem Endpoints

#### `GET /api/problems` — Fetch problems with filters

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `topic_id` | string | e.g. `giai-tich.dao-ham` |
| `difficulty` | enum | `easy` \| `medium` \| `hard` |
| `is_geometry` | boolean | Filter to 3D geometry problems |
| `limit` | int | Default 20, max 100 |

---

#### `GET /api/problems/:id/geometry` — Get 3D model parameters

**Response `200`:**

| Field | Type | Description |
|---|---|---|
| `solid_type` | string | pyramid, prism, cone, sphere, cylinder, composite |
| `params` | object | All dimensional parameters for Three.js renderer |
| `labels` | object | e.g. `{"apex": "S", "base": ["A","B","C","D"]}` |

---

### Progress Endpoints

#### `GET /api/progress/me` — Get student's mastery map

**Response `200`:**

| Field | Type | Description |
|---|---|---|
| `mastery_by_topic` | object | `{topic_id: score 0.0–1.0}` |
| `sessions_this_week` | int | For weekly activity chart |
| `suggested_topics` | array | Top 3 topics recommended (lowest mastery + most overdue) |
| `streak_days` | int | Consecutive days with completed sessions |

---

#### `GET /api/admin/stats` — Platform analytics (admin only)

**Response `200`:**

| Field | Type | Description |
|---|---|---|
| `daily_active_users` | array | DAU time series, past 30 days |
| `avg_session_duration_min` | float | Average session length in minutes |
| `top_error_topics` | array | Topics with highest hint request rates |
| `geometry_viewer_usage_pct` | float | % of geometry sessions with 3D viewer triggered |

---

## 4. 3D Geometry Visualizer

### Implementation Approach

All 3D models are **procedurally generated** from JSON parameters — not static assets. Any problem with numeric dimensions produces the correct, custom-scaled model automatically.

**Core stack:** Three.js + OrbitControls + CSS2DRenderer (vertex labels that always face the camera).

---

### Supported Geometry Types (MVP)

| Type | `solid_type` | Key Parameters |
|---|---|---|
| Pyramid (Hình chóp) | `"pyramid"` | `base_shape`, `base_side`, `height`, `apex_label`, `base_labels[]`, `show_altitude`, `altitude_foot_label` |
| Prism (Lăng trụ) | `"prism"` | `base_shape`, `base_side`, `height`, `top_labels[]`, `bottom_labels[]`, `diagonal` |
| Sphere (Hình cầu) | `"sphere"` | `radius`, `center_label`, `show_great_circle`, `show_cross_section`, `cross_section_height` |
| Cone (Hình nón) | `"cone"` | `base_radius`, `height`, `apex_label`, `show_slant_height`, `show_altitude` |
| Cuboid (Hình hộp) | `"cuboid"` | `width`, `depth`, `height`, `vertex_labels[]` (8), `show_space_diagonal`, `highlight_face` |
| Composite (Tổ hợp) | `"composite"` | `components[]` — each with `type`, `params`, and `offset: {x,y,z}` |

---

### Viewer Feature Roadmap

| Feature | Implementation | Sprint |
|---|---|---|
| Orbit rotation | OrbitControls — drag to rotate, scroll to zoom | 2 |
| Vertex labels | CSS2DRenderer — labels always face camera | 2 |
| Edge highlighting | LineSegments with per-edge color control | 2 |
| Altitude line | Dashed line from apex to foot; foot labeled | 2 |
| Cross-section plane | Slider moves a clipping plane through solid | 3 |
| Step-by-step construction | Animated draw sequence: vertices → edges → faces | 3 |
| Measurement overlay | Known dimensions annotated on edges (toggleable) | 3 |
| Mobile touch controls | Pinch-to-zoom, two-finger rotate via HammerJS | 4 |

---

### Component Interface (TypeScript)

```typescript
interface GeometryViewerProps {
  /** JSON params from API or Claude tool_use event */
  solidSpec: SolidSpec

  width?: number
  height?: number          // default: fills container

  /** Elements to highlight, e.g. ["SA", "SB", "H"] */
  highlights?: string[]

  /** Play construction animation on mount */
  animated?: boolean

  /** Show cross-section slider */
  showCrossSection?: boolean

  /** Callback when student clicks a vertex or edge */
  onElementClick?: (label: string) => void
}

// Usage in MessageBubble
function MessageBubble({ message }: Props) {
  if (message.tool_call?.name === "render_geometry") {
    return (
      <GeometryViewer
        solidSpec={message.tool_call.input}
        animated={true}
        height={360}
      />
    )
  }
  return <TextMessage content={message.content} />
}
```

---

## 5. Database Schema

### Setup

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector

-- Enums
CREATE TYPE user_role       AS ENUM ('student', 'admin');
CREATE TYPE session_status  AS ENUM ('active', 'completed', 'abandoned');
CREATE TYPE dialogue_state  AS ENUM ('review', 'heuristic', 'rectify', 'summarize');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');
```

---

### Tables

```sql
-- Users
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  avatar_url    TEXT,
  role          user_role NOT NULL DEFAULT 'student',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  last_active   TIMESTAMPTZ
);

-- Problem bank
CREATE TABLE problems (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id         TEXT NOT NULL,          -- e.g. "hinh-hoc.hinh-chop"
  statement_latex  TEXT NOT NULL,          -- KaTeX-formatted
  difficulty       difficulty_level NOT NULL,
  answer           TEXT NOT NULL,          -- hidden from students
  is_geometry      BOOLEAN DEFAULT FALSE,
  geometry_params  JSONB,                  -- null if not geometry
  source           TEXT,                   -- e.g. "THPT 2024"
  misconceptions   JSONB,                  -- array of common errors
  embedding        VECTOR(1536),           -- pgvector similarity search
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_problems_topic ON problems(topic_id);
CREATE INDEX idx_problems_geo   ON problems(is_geometry);
CREATE INDEX idx_problems_emb   ON problems USING ivfflat(embedding vector_cosine_ops);

-- Sessions
CREATE TABLE sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  problem_id      UUID REFERENCES problems(id),   -- nullable (free-ask)
  topic_id        TEXT NOT NULL,
  status          session_status DEFAULT 'active',
  dialogue_state  dialogue_state DEFAULT 'review',
  hint_level      SMALLINT DEFAULT 0,
  hint_count      SMALLINT DEFAULT 0,
  fail_count      SMALLINT DEFAULT 0,
  messages        JSONB NOT NULL DEFAULT '[]',
  summary         TEXT,                           -- AI-generated post-session
  student_rating  SMALLINT,                       -- 1–5 self-rating
  started_at      TIMESTAMPTZ DEFAULT NOW(),
  ended_at        TIMESTAMPTZ
);
CREATE INDEX idx_sessions_user ON sessions(user_id, started_at DESC);

-- Progress (one row per user × topic)
CREATE TABLE progress (
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  topic_id        TEXT,
  mastery_score   FLOAT DEFAULT 0.0,              -- 0.0 → 1.0
  sessions_count  INT DEFAULT 0,
  last_practiced  TIMESTAMPTZ,
  PRIMARY KEY (user_id, topic_id)
);
```

---

### Mastery Score Algorithm

```python
def compute_mastery_delta(session: Session) -> float:
    """
    Mastery increases on successful completion.
    Hint usage and fail count reduce the gain.
    """
    base_gain = 0.15  # max gain per completed session

    hint_penalty = session.hint_count * 0.20     # each hint = -20% of gain
    fail_penalty  = session.fail_count * 0.10    # each failure = -10% of gain
    rating_factor = (session.student_rating / 5.0) if session.student_rating else 0.7

    delta = base_gain * rating_factor * (1 - hint_penalty - fail_penalty)
    return max(0.0, min(delta, base_gain))        # clamp to [0, base_gain]

def update_mastery(user_id: str, topic_id: str, delta: float):
    # Exponential moving average — prevents instant full mastery
    new_score = min(1.0, current_score + delta * (1 - current_score))
```

---

## 6. Frontend Architecture

### App Router Structure

```
frontend/app/
├── layout.tsx                    # Root: fonts, Sentry, auth provider
├── page.tsx                      # Landing (logged out) / redirect to /dashboard
│
├── (auth)/
│   ├── login/page.tsx            # Google OAuth
│   └── register/page.tsx         # Onboarding: name, grade, goals
│
├── (student)/
│   ├── layout.tsx                # Sidebar nav + auth guard
│   ├── dashboard/page.tsx        # Mastery radar, weekly activity, suggestions
│   ├── topics/page.tsx           # Topic picker grid
│   ├── topics/[id]/page.tsx      # Chapter view + problem list
│   ├── session/
│   │   ├── new/page.tsx          # Session config (topic, difficulty, free-ask)
│   │   └── [id]/page.tsx         # Active: Chat panel + 3D viewer split
│   └── history/page.tsx          # Past sessions + transcript review
│
└── (admin)/
    ├── layout.tsx                # Admin nav + role guard
    └── dashboard/page.tsx        # Platform stats, error patterns, user list
```

---

### Core Components

| Component | Responsibility | Key Dependencies |
|---|---|---|
| `ChatPanel` | Renders conversation thread. Handles SSE stream, auto-scroll, all message types. | `useSSE` hook, react-katex |
| `MessageBubble` | Single message — text with inline KaTeX, or `GeometryViewer` if `tool_call` present. | KaTeX, GeometryViewer |
| `ChatInput` | Text area with hint button, send button. Enter-to-send, Shift+Enter for newline. | — |
| `GeometryViewer` | Three.js canvas. Accepts `SolidSpec` JSON, procedurally generates geometry. | Three.js, CSS2DRenderer |
| `ContextPanel` | Right sidebar in session: problem statement, hint level, dialogue phase badge, timer. | react-katex |
| `MasteryRadar` | Recharts RadarChart of 6 topic mastery scores. Clickable to navigate to topic. | Recharts |
| `TopicCard` | Topic picker card: name, chapter count, mastery badge, recommended indicator. | — |
| `SessionSummary` | Post-session overlay: AI summary, mastery delta, next topic suggestion, rating input. | — |
| `HintButton` | Shows current hint level (0–3). On click: confirms and posts `hint_requested: true`. | — |

---

### State Management

Use **Zustand** for global client state. Use **TanStack Query (React Query)** for all server state.

| Slice | Store | Contents |
|---|---|---|
| Auth | Zustand | `user`, `token`, `isAuthenticated` |
| Active session | Zustand | `sessionId`, `messages[]`, `dialogueState`, `hintLevel`, `isStreaming` |
| Progress / mastery | React Query | Cached from `GET /api/progress/me` |
| Problem list | React Query | Cached + paginated from `GET /api/problems` |
| Session history | React Query | Cached from `GET /api/sessions` |

---

## 7. 8-Week Sprint Plan

> **Rule:** Sprint 1 is AI-only. No UI work until Sprint 2. A working Socratic dialogue via API call is worth more than a polished interface on top of a broken AI.

---

### Sprint 1 — Socratic AI Engine (Weeks 1–2)

**Week 1 — Foundation**

- [ ] Set up FastAPI project + folder structure (`routers/`, `ai/`, `db/`)
- [ ] Configure Claude API client with async streaming
- [ ] Write Socratic system prompt v1 in Vietnamese
- [ ] Implement dialogue state machine (4 states: REVIEW → HEURISTIC → RECTIFY → SUMMARIZE)
- [ ] Build session context builder (problem statement + conversation history + misconceptions)
- [ ] Create problem bank JSON (first 50 problems, tagged by topic and difficulty)
- [ ] Test 5 full Socratic sessions end-to-end via curl / Postman

**Week 2 — Refinement**

- [ ] Implement hint escalation system (L0 → L3)
- [ ] Add geometry detection + `render_geometry` tool definition
- [ ] Set up PostgreSQL + run init migration (`001_init_schema.sql`)
- [ ] Implement session CRUD endpoints (without auth for now)
- [ ] Load misconceptions catalog per topic into context builder
- [ ] Iterate on system prompt — verify AI never reveals full answer in one turn
- [ ] Expand problem bank to 100 problems

**✓ Sprint Gate:** 10 complete Socratic sessions via API. AI never gives a direct answer in a single turn. Dialogue state transitions correctly. Geometry tool is called when appropriate.

---

### Sprint 2 — Core UI + 3D Viewer + Auth (Weeks 3–4)

**Week 3 — Scaffold**

- [ ] Next.js 14 project init + Tailwind CSS + folder structure
- [ ] Google OAuth via NextAuth.js
- [ ] JWT integration between NextAuth and FastAPI
- [ ] `ChatPanel` + `MessageBubble` components
- [ ] `useSSE` hook for Server-Sent Events streaming
- [ ] KaTeX inline math rendering in chat messages
- [ ] Topic picker page + routing

**Week 4 — 3D Viewer**

- [ ] Three.js setup + OrbitControls + CSS2DRenderer
- [ ] Pyramid renderer (square base, labeled vertices, optional altitude)
- [ ] Prism renderer (triangular + rectangular base)
- [ ] Sphere + Cone renderers
- [ ] Integrate `GeometryViewer` into `MessageBubble` (triggered by `tool_use` event)
- [ ] Session `[id]` page: split layout (chat left, context + 3D viewer right)
- [ ] Session persistence — messages saved to PostgreSQL

**✓ Sprint Gate:** Full session works end-to-end in the browser. Geometry problem automatically triggers 3D viewer. Google auth works. Messages persist across page refresh.

---

### Sprint 3 — Progress, Roles & Advanced Features (Weeks 5–6)

**Week 5 — Progress Layer**

- [ ] Mastery score computation on session completion
- [ ] `PUT /api/sessions/:id/complete` endpoint + DB update
- [ ] `GET /api/progress/me` endpoint
- [ ] Student dashboard: mastery radar chart (Recharts)
- [ ] Weekly activity chart on dashboard
- [ ] Session summary overlay (post-session)
- [ ] Next topic suggestion logic (lowest mastery + most overdue)
- [ ] Session history page with transcript review

**Week 6 — Admin + 3D Enhancements**

- [ ] Admin role + route guard (role check from JWT)
- [ ] Admin dashboard: DAU chart, top error topics, 3D viewer usage %
- [ ] Cross-section slider on 3D viewer
- [ ] Step-by-step construction animation (vertices → edges → faces)
- [ ] Measurement overlay on 3D edges (toggleable)
- [ ] Hint button + hint level indicator in chat
- [ ] Mobile-responsive layout pass (chat + viewer)

**✓ Sprint Gate:** Both student and admin roles work. Mastery scores update after each session. Admin can view platform stats. 3D viewer is usable on a mobile browser.

---

### Sprint 4 — Polish, Pilot & Launch Prep (Weeks 7–8)

**Week 7 — Pilot Launch**

- [ ] Deploy frontend to Vercel (configure env vars, custom domain if ready)
- [ ] Deploy backend + PostgreSQL + Redis to Railway
- [ ] Configure Sentry on both frontend and backend
- [ ] Set up GitHub Actions CI (lint + typecheck + tests on every PR)
- [ ] Recruit 10–15 Grade 12 pilot students (school contacts, Facebook groups)
- [ ] Onboard pilot users, collect first session feedback via Google Form
- [ ] Expand problem bank to 200+ problems

**Week 8 — Fix & Demo Prep**

- [ ] Fix top issues from pilot feedback
- [ ] Error state handling: API failures, empty states, loading skeletons
- [ ] Performance: lazy-load 3D viewer, code-split heavy chunks
- [ ] Optimistic UI for message sending
- [ ] Write `README.md` with setup guide, architecture overview, deploy instructions
- [ ] Clean Git history: remove debug logs, squash WIP commits
- [ ] Demo dry-run on production URL (no localhost)

**✓ Sprint Gate:** 10+ pilot students have completed sessions. Return rate > 40% in week 2. Live demo works on production URL without any localhost dependency.

---

### Sprint Timeline Summary

```
Week  1  2  3  4  5  6  7  8
      ├──┤  │  │  │  │  │  │
S1 AI ████  │  │  │  │  │  │
S2 UI    ├──┤  │  │  │  │  │
         ████  │  │  │  │  │
S3 Prog+    ├──┤  │  │  │  │
Roles       ████  │  │  │  │
S4 Pilot+      ├──┤  │  │  │
Launch         ████            ← Live on Vercel + Railway
```

---

## 8. Environment & Testing

### Environment Variables

```bash
# ── AI ──────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-...          # Backend only — never expose to client

# ── DATABASE ────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/toan_socratic
REDIS_URL=redis://default:pass@host:6379

# ── AUTH ────────────────────────────────────────────────────
JWT_SECRET=<64+ char random string>   # openssl rand -hex 32
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<OAuth secret>
NEXTAUTH_SECRET=<32+ char random string>
NEXTAUTH_URL=https://toan-socratic.vercel.app

# ── FRONTEND ─────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=https://api.toan-socratic.railway.app

# ── MONITORING ───────────────────────────────────────────────
SENTRY_DSN=<from Sentry project settings>

# ── STORAGE ──────────────────────────────────────────────────
R2_ACCOUNT_ID=<Cloudflare account ID>
R2_ACCESS_KEY_ID=<R2 API key>
R2_SECRET_ACCESS_KEY=<R2 secret>
```

---

### Testing Strategy

#### Backend Unit Tests (pytest)

- Mastery score computation algorithm
- Dialogue state machine transitions
- Hint level escalation logic
- Problem bank JSON schema validation
- JWT auth middleware
- Geometry params serialization

#### AI Behavior Tests

- AI does not reveal full answer in first turn
- Vietnamese language consistency across dialogue states
- Geometry tool (`render_geometry`) called on 3D problems
- Hint level correctly injected into system prompt
- LaTeX syntax correct in AI responses
- L3 hint shows complete solution and follows with a new problem

#### Frontend Component Tests (Vitest)

- `ChatPanel` renders streamed messages correctly
- `GeometryViewer` loads all 6 solid types without error
- KaTeX renders inline math without parse errors
- Auth redirect on unauthenticated access to protected routes
- Session summary modal triggers on session completion
- Hint button advances level and calls API correctly

#### E2E Tests (Playwright)

- Full session flow: login → topic → session → complete
- Geometry session: 3D viewer renders and orbits correctly
- Hint escalation: 3 requests reach L3
- Dashboard mastery score updates post-session
- Admin can view stats; student cannot access admin routes
- Mobile viewport: chat + viewer fully usable at 390px width

---

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: ruff check .          # lint
      - run: pytest tests/ -v      # unit tests

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint          # ESLint
      - run: npm run type-check    # TypeScript
      - run: npm run test          # Vitest

  # Vercel and Railway both auto-deploy on push to main
  # No manual deploy step needed after initial setup
```

---

### Minimum Product Checklist

Before demo day, every item must be checked:

- [ ] Web app deployed at a real public URL
- [ ] Google OAuth login and registration working
- [ ] Student and admin roles with distinct views and route guards
- [ ] Socratic dialogue engine working in Vietnamese with streaming
- [ ] 3D geometry viewer functional for at least 3 solid types
- [ ] Session history persists across logins
- [ ] Student mastery radar chart displayed on dashboard
- [ ] Mobile responsive at 390px viewport
- [ ] Sentry error monitoring active on frontend and backend
- [ ] GitHub repo: clean code, README with setup and deploy guide
- [ ] Live demo runs on production URL — no localhost dependency
- [ ] At least 5 real students have used the platform before demo day
