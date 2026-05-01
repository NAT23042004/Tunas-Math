# Toán Socratic — Implementation Spec v1.0

> A full engineering specification for the Toán Socratic platform — covering system architecture, Socratic dialogue design, API contracts, 3D visualizer implementation, database schema, frontend component tree, and an 8-week sprint plan.

| Metric | Value |
|---|---|
| Build Duration | 8 weeks |
| Sprints | 4 |
| API Endpoints | 16 |
| 3D Geometry Types | 6 |

---

## Table of Contents

1. [System Architecture](#01-system-architecture)
2. [Socratic Engine Spec](#02-socratic-engine-spec)
3. [API Specification](#03-api-specification)
4. [3D Geometry Visualizer Spec](#04-3d-geometry-visualizer-spec)
5. [Database Schema](#05-database-schema)
6. [Frontend Component Tree](#06-frontend-component-tree)
7. [8-Week Sprint Plan](#07-8-week-sprint-plan)
8. [Environment & Testing](#08-environment--testing)

---

## 01 — System Architecture

> Full-stack overview — how each layer connects, what technology powers it, and the data flow from student to AI and back.

### Layers

**Client Layer**
- **Chat UI** — Next.js 14 · React · Tailwind
- **3D Geometry Viewer** — Three.js · WebGL · OrbitControls
- **Math Renderer** — KaTeX · react-katex
- **Dashboard & Progress** — Recharts · Radix UI

*↕ HTTPS / WebSocket (streaming)*

**API Layer**
- **FastAPI Server** — Python 3.11 · Uvicorn · async
- **Auth Middleware** — JWT · NextAuth · Google OAuth
- **Session Manager** — Dialogue state · History mgmt
- **Problem Resolver** — Topic router · RAG retrieval

*↕ Anthropic SDK · Python*

**AI Pipeline**
- **Socratic Engine** — claude-sonnet-4-6 · System prompt
- **RAG Context Builder** — pgvector · Embedding search
- **Misconception Catalog** — JSON · Per-topic error patterns
- **Tool Use Handler** — Geometry trigger · Hint escalation

*↕ SQLAlchemy ORM · asyncpg*

**Data Layer**
- **PostgreSQL + pgvector** — Users · Sessions · Progress · Problems
- **Redis Cache** — Active session state · Rate limiting
- **Cloudflare R2** — Static assets · OCR uploads
- **Problem Bank JSON** — 200+ THPT problems · Curriculum tree

*↕ Vercel CDN · Railway PaaS*

**Infrastructure**
- **Vercel (Frontend)** — Edge network · CI/CD · Preview deploys
- **Railway (Backend)** — FastAPI · PostgreSQL · Redis
- **Sentry** — Error tracking · Performance
- **GitHub Actions** — Lint · Test · Deploy on merge

---

### Data Flow — A Single Socratic Turn

```
Student          →(HTTP POST)→   API Server       →(fetch context)→   RAG Builder
(types answer)                   (validates JWT,                       (retrieves problem
                                  loads history)                        + misconceptions)

        →(Anthropic SDK)→   Claude API          →(SSE stream)→   Tool Check
                            (Socratic prompt                      (Geometry trigger?
                             + full history)                       Hint level?)

        →(to client)→   Chat UI
                        (streams response +
                         renders 3D if needed)
```

---

## 02 — Socratic Engine Spec

> The AI dialogue design — system prompt architecture, state machine, hint escalation, and tool use for the geometry trigger.

### Dialogue State Machine

```
① REVIEW → ② HEURISTIC → ③ RECTIFY → ④ SUMMARIZE
```

| State | Description |
|---|---|
| **① REVIEW** | Restate the problem, ask student what they already know about it |
| **② HEURISTIC** | Ask guiding sub-questions to break problem into tractable steps |
| **③ RECTIFY** | Student makes error → AI identifies it without solving → guided back |
| **④ SUMMARIZE** | Student solves → AI confirms and generalizes the concept |

> RECTIFY loops back to HEURISTIC (max 3×) → if still stuck, escalate HINT LEVEL

---

### Hint Escalation System

| Level | Trigger | What the AI does | Example response |
|---|---|---|---|
| `L0` — Pure Socratic | Default state | Only asks questions. Never states a fact directly. | *"Góc giữa SA và mặt đáy là gì? Bạn tính nó bằng cách nào?"* |
| `L1` — Guided Hint | 2+ failed attempts on same step | Points to the specific tool or theorem needed, then asks. | *"Hãy nghĩ đến định lý Pythagoras trong tam giác SAH. Bạn xác định được H chưa?"* |
| `L2` — Scaffolded Hint | Student requests hint OR 3+ failures | Provides first step explicitly. Student must complete remaining. | *"AH = AB/2 = 3cm. Từ đây, bạn tính SA như thế nào?"* |
| `L3` — Full Worked Example | Student explicitly types "Mình chịu rồi" or equivalent | Shows complete solution. Immediately follows with a similar problem. | Full solution shown. *"Bây giờ hãy thử bài tương tự này…"* |

---

### System Prompt Architecture

> ⚠️ The system prompt is the most critical engineering artifact in this product. It must enforce Socratic behavior, handle Vietnamese math vocabulary precisely, and trigger the geometry visualizer via Claude's tool use. Draft, test, and iterate on this before building any UI.

```
# system_prompt.txt — Socratic Tutor Core (~800 tokens)

# VAI TRÒ
Bạn là gia sư Toán Socratic cho học sinh lớp 12 Việt Nam đang ôn thi THPT.
Nhiệm vụ của bạn: giúp học sinh TỰ TÌM RA đáp án — không bao giờ đưa ra giải pháp trực tiếp.

# NGUYÊN TẮC BẮT BUỘC
1. KHÔNG BAO GIỜ đưa ra đáp án hoặc lời giải hoàn chỉnh trong một lượt, trừ khi học sinh đã yêu cầu gợi ý L3.
2. MỌI phản hồi phải chứa ít nhất một câu hỏi dẫn dắt.
3. Khi học sinh sai: không nói "sai", hỏi "Tại sao em nghĩ [kết quả đó]?"
4. Ngôn ngữ: Tiếng Việt, thân thiện, kiên nhẫn. Xưng "thầy/cô", gọi học sinh là "em".
5. Toán học: Viết biểu thức theo LaTeX trong dấu $…$ hoặc $$…$$.

# PHÁT HIỆN HÌNH HỌC KHÔNG GIAN
Nếu bài toán liên quan đến: hình chóp, lăng trụ, hình hộp, hình cầu, hình nón, hình trụ —
→ GỌI TOOL render_geometry với tham số từ đề bài.
→ Sau khi render, hỏi: "Em nhìn vào hình 3D, em thấy điểm H nằm ở đâu?"

# TRẠNG THÁI DIALOGUE
Hiện tại: {{dialogue_state}} (REVIEW | HEURISTIC | RECTIFY | SUMMARIZE)
Số lần thất bại ở bước hiện tại: {{fail_count}}
Mức gợi ý hiện tại: {{hint_level}} (0 | 1 | 2 | 3)

# NGỮ CẢNH BÀI TOÁN
Chủ đề: {{topic}}
Đề bài: {{problem_statement}}
Lỗi phổ biến cần để ý: {{misconceptions}}

# CẤU TRÚC PHẢN HỒI
Tốt:  "Em tính được chiều cao AH = 3cm rồi. Từ đó, em dùng định lý nào để tìm SA?"
Tránh: "Áp dụng Pythagoras: SA² = SH² + AH² = 16 + 9 = 25, vậy SA = 5cm."
```

---

### Claude Tool Use — Geometry Trigger

```python
# geometry_tool_spec.py
# Tool definition sent to Claude API alongside system prompt

GEOMETRY_TOOL = {
    "name": "render_geometry",
    "description": "Renders an interactive 3D geometry figure for the student. "
                   "Call this whenever the problem involves 3D solids.",
    "input_schema": {
        "type": "object",
        "required": ["solid_type", "params"],
        "properties": {
            "solid_type": {
                "type": "string",
                "enum": ["pyramid", "prism", "cone",
                         "sphere", "cylinder", "composite"]
            },
            "params": {
                "type": "object",
                "description": "Geometric parameters: base dimensions, height, "
                               "vertex labels (A,B,C…), apex label (S), "
                               "special points to highlight (foot of altitude H, etc)"
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

## 03 — API Specification

> All backend endpoints — request parameters, response shape, and auth requirements.

> 🔐 All endpoints except `POST /auth/*` require a valid JWT in the `Authorization: Bearer <token>` header. Admin-only endpoints additionally check `role === "admin"` from the token payload.

---

### Session Endpoints

#### `POST /api/sessions` — Start a new Socratic session

**Request Body**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `topic_id` | string | required | Curriculum node ID e.g. `hinh-hoc.hinh-chop` |
| `problem_id` | uuid | optional | If provided, session starts from a specific problem; otherwise free-ask mode |
| `initial_message` | string | optional | Student's opening question or problem description |

**Response `201`**

| Field | Type | Description |
|---|---|---|
| `session_id` | uuid | New session ID for all subsequent calls |
| `first_message` | string | AI's opening Socratic question (streamed if `stream=true`) |
| `geometry_params` | object\|null | 3D model params if problem is geometry type; null otherwise |

---

#### `POST /api/sessions/:id/message` — Send a student message and receive streamed AI response

**Request Body**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content` | string | required | Student's message text |
| `hint_requested` | boolean | optional | True if student clicked the hint button — advances hint level |

**Response — Server-Sent Events stream**

| Event | Type | Description |
|---|---|---|
| `event: delta` | string | Streamed text chunk from Claude |
| `event: tool_use` | object | Geometry render trigger with `solid_type` and `params` |
| `event: done` | object | Final message metadata: `dialogue_state`, `hint_level`, `tokens_used` |

---

#### `GET /api/sessions/:id` — Retrieve full session history and current state

**Response `200`**

| Field | Type | Description |
|---|---|---|
| `session` | object | `id`, `topic_id`, `status`, `dialogue_state`, `hint_level`, `hint_count` |
| `messages` | array | Array of `{role, content, timestamp, tool_calls?}` |
| `problem` | object\|null | Full problem object if session is problem-linked |

---

#### `PUT /api/sessions/:id/complete` — Mark session complete — updates mastery score and progress

**Request Body**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `student_rating` | int 1–5 | optional | Self-rated understanding after session |

**Response `200`**

| Field | Type | Description |
|---|---|---|
| `summary` | string | AI-generated session summary (concept covered, breakthrough moment) |
| `mastery_delta` | float | Change in mastery score for this topic |
| `next_suggested_topic` | string | AI-suggested next topic based on session performance |

---

### Problem Endpoints

#### `GET /api/problems` — Fetch problems filtered by topic, difficulty, and type

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `topic_id` | string | optional | Curriculum node e.g. `giai-tich.dao-ham` |
| `difficulty` | enum | optional | `easy` \| `medium` \| `hard` |
| `is_geometry` | boolean | optional | Filter to problems with 3D geometry component |
| `limit` | int | optional | Default 20, max 100 |

---

#### `GET /api/problems/:id/geometry` — Get 3D model parameters for a geometry problem

**Response `200`**

| Field | Type | Description |
|---|---|---|
| `solid_type` | string | One of pyramid, prism, cone, sphere, cylinder, composite |
| `params` | object | All dimensional parameters needed for Three.js renderer |
| `labels` | object | Vertex/edge label map e.g. `{"apex": "S", "base": ["A","B","C","D"]}` |

---

### Progress & Analytics Endpoints

#### `GET /api/progress/me` — Get authenticated student's full mastery map

**Response `200`**

| Field | Type | Description |
|---|---|---|
| `mastery_by_topic` | object | Map of topic_id → mastery score 0.0–1.0 |
| `sessions_this_week` | int | Activity count for weekly chart |
| `suggested_topics` | array | Top 3 topics recommended for next study (lowest mastery + most overdue) |
| `streak_days` | int | Consecutive days with at least one completed session |

---

#### `GET /api/admin/stats` — Admin: platform-wide analytics (admin role required)

**Response `200`**

| Field | Type | Description |
|---|---|---|
| `daily_active_users` | array | DAU time series for the past 30 days |
| `avg_session_duration_min` | float | Average session length in minutes |
| `top_error_topics` | array | Topics with highest hint request rates |
| `geometry_viewer_usage_pct` | float | % of geometry sessions where 3D viewer was triggered |

---

## 04 — 3D Geometry Visualizer Spec

> Implementation plan for the Three.js-powered interactive geometry viewer — the platform's strongest differentiator.

> 💡 All 3D models are **procedurally generated** from JSON parameters — not static assets. This means any problem with numeric dimensions renders the correct, custom-scaled model automatically. No manual 3D modelling required.

---

### Supported Geometry Types — MVP

#### 🔺 Pyramid (Hình chóp)
```
solid_type: "pyramid"
base_shape: square|rect|triangle|regular_n
base_side: number (cm)
height: number (cm)
apex_label: string
base_labels: string[]
show_altitude: boolean
altitude_foot_label: string
```

#### ⬡ Prism (Lăng trụ)
```
solid_type: "prism"
base_shape: triangle|square|rect|regular_n
base_side: number
height: number
top_labels: string[]
bottom_labels: string[]
diagonal: boolean
```

#### 🔵 Sphere (Hình cầu)
```
solid_type: "sphere"
radius: number
center_label: string
show_great_circle: boolean
show_cross_section: boolean
cross_section_height: number
```

#### 🔶 Cone (Hình nón)
```
solid_type: "cone"
base_radius: number
height: number
apex_label: string
center_label: string
show_slant_height: boolean
show_altitude: boolean
```

#### ⬜ Cuboid / Box (Hình hộp)
```
solid_type: "cuboid"
width: number
depth: number
height: number
vertex_labels: string[] (8 vertices)
show_space_diagonal: boolean
highlight_face: string
```

#### 🔗 Composite (Tổ hợp)
```
solid_type: "composite"
components: SolidSpec[]
Each component has:
  type + params + offset: {x,y,z}
Enables pyramid-on-prism etc.
```

---

### Viewer Component Features

| Feature | Implementation | Sprint |
|---|---|---|
| Orbit rotation | Three.js OrbitControls — drag to rotate, scroll to zoom | Sprint 2 |
| Vertex labels | CSS2DRenderer overlay — labels always face camera | Sprint 2 |
| Edge highlighting | LineSegments with per-edge color control | Sprint 2 |
| Altitude line | Dashed line from apex to altitude foot; foot labeled | Sprint 2 |
| Cross-section plane | Slider control moves a clipping plane through the solid | Sprint 3 |
| Step-by-step construction | Animated draw sequence — vertices → edges → faces in order | Sprint 3 |
| Measurement overlay | Toggle to show known dimensions as annotations on edges | Sprint 3 |
| Mobile touch controls | Pinch-to-zoom, two-finger rotate via HammerJS | Sprint 4 |

---

### Component API

```typescript
// GeometryViewer.tsx — Component interface

interface GeometryViewerProps {
  /** JSON params from API or Claude tool_use */
  solidSpec: SolidSpec

  /** Width of viewer canvas (default: fills container) */
  width?: number
  height?: number

  /** Elements to highlight — e.g. ["SA", "SB", "H"] */
  highlights?: string[]

  /** Show construction animation on mount */
  animated?: boolean

  /** Enable cross-section slider */
  showCrossSection?: boolean

  /** Callback when student clicks a vertex/edge */
  onElementClick?: (label: string) => void
}

/** Usage in Chat component */
function ChatMessage({ message }: Props) {
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

## 05 — Database Schema

> Full PostgreSQL schema with indexes, relationships, and migration order.

```sql
-- 001_init_schema.sql

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector

-- Enums
CREATE TYPE user_role AS ENUM ('student', 'admin');
CREATE TYPE session_status AS ENUM ('active', 'completed', 'abandoned');
CREATE TYPE dialogue_state AS ENUM ('review', 'heuristic', 'rectify', 'summarize');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');

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

-- Problems bank
CREATE TABLE problems (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id         TEXT NOT NULL,          -- e.g. "hinh-hoc.hinh-chop"
  statement_latex  TEXT NOT NULL,          -- KaTeX-formatted problem
  difficulty       difficulty_level NOT NULL,
  answer           TEXT NOT NULL,           -- hidden from student
  is_geometry      BOOLEAN DEFAULT FALSE,
  geometry_params  JSONB,                   -- null if not geometry
  source           TEXT,                    -- e.g. "THPT 2024"
  misconceptions   JSONB,                   -- array of common errors
  embedding        VECTOR(1536),            -- for similarity search
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_problems_topic ON problems(topic_id);
CREATE INDEX idx_problems_geo ON problems(is_geometry);
CREATE INDEX idx_problems_emb ON problems USING ivfflat(embedding vector_cosine_ops);

-- Sessions
CREATE TABLE sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  problem_id      UUID REFERENCES problems(id),  -- nullable
  topic_id        TEXT NOT NULL,
  status          session_status DEFAULT 'active',
  dialogue_state  dialogue_state DEFAULT 'review',
  hint_level      SMALLINT DEFAULT 0,
  hint_count      SMALLINT DEFAULT 0,
  fail_count      SMALLINT DEFAULT 0,
  messages        JSONB NOT NULL DEFAULT '[]',
  summary         TEXT,
  student_rating  SMALLINT,                       -- 1-5 self-rating
  started_at      TIMESTAMPTZ DEFAULT NOW(),
  ended_at        TIMESTAMPTZ
);
CREATE INDEX idx_sessions_user ON sessions(user_id, started_at DESC);

-- Progress (one row per user × topic)
CREATE TABLE progress (
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  topic_id        TEXT,
  mastery_score   FLOAT DEFAULT 0.0,          -- 0.0 → 1.0
  sessions_count  INT DEFAULT 0,
  last_practiced  TIMESTAMPTZ,
  PRIMARY KEY (user_id, topic_id)
);
```

---

### Mastery Score Algorithm

```python
# mastery.py — Score update logic

def compute_mastery_delta(session: Session) -> float:
    """
    Mastery increases on successful completion.
    Hint usage and fail count penalize the gain.
    """
    base_gain = 0.15  # max gain per completed session

    # Penalty for hints used (each hint = -20% of gain)
    hint_penalty = session.hint_count * 0.20

    # Penalty for repeated failures
    fail_penalty = session.fail_count * 0.10

    # Student's self-rating bonus (5 stars = no penalty)
    rating_factor = (session.student_rating / 5.0) if session.student_rating else 0.7

    delta = base_gain * rating_factor * (1 - hint_penalty - fail_penalty)
    return max(0.0, min(delta, base_gain))  # clamp to [0, base_gain]

def update_mastery(user_id: str, topic_id: str, delta: float):
    # Exponential moving average — prevents instant mastery
    new_score = min(1.0, current_score + delta * (1 - current_score))
```

---

## 06 — Frontend Component Tree

> Next.js App Router structure, component responsibilities, and state management approach.

### App Router Structure

```
app/
├── layout.tsx               # Root layout: fonts, Sentry, auth provider
├── page.tsx                 # Landing page (logged out) / redirect to /dashboard
│
├── (auth)/
│   ├── login/page.tsx       # Google OAuth button
│   └── register/page.tsx    # Onboarding (name, class, goals)
│
├── (student)/
│   ├── layout.tsx           # Sidebar nav + auth guard
│   ├── dashboard/page.tsx   # Mastery radar, weekly activity, suggestions
│   ├── topics/page.tsx      # Topic picker grid
│   ├── topics/[id]/page.tsx # Chapter view + problem list
│   ├── session/
│   │   ├── new/page.tsx     # Session config (topic, difficulty, free-ask)
│   │   └── [id]/page.tsx   # Active session: Chat + 3D Viewer split
│   └── history/page.tsx     # Past sessions list + review
│
└── (admin)/
    ├── layout.tsx           # Admin nav + role guard
    └── dashboard/page.tsx   # Platform stats, error patterns, user list
```

---

### Core Components

| Component | Responsibility | Key deps |
|---|---|---|
| `ChatPanel` | Renders conversation thread. Handles SSE stream, auto-scroll, message types (text, tool_use, latex). Parent of all message types. | react-katex, useSSE hook |
| `MessageBubble` | Single message — renders text with inline KaTeX, code blocks, or GeometryViewer if tool_call present. | KaTeX, GeometryViewer |
| `ChatInput` | Text area with hint button, send button, character count. Handles Enter-to-send vs Shift+Enter newline. | — |
| `GeometryViewer` | Three.js canvas. Accepts SolidSpec JSON. Procedurally generates geometry. OrbitControls, CSS2D labels, edge highlights. | Three.js, CSS2DRenderer |
| `ContextPanel` | Right sidebar in session view. Shows problem statement (KaTeX), hint level indicator, dialogue phase badge, session timer. | react-katex |
| `MasteryRadar` | Recharts RadarChart showing 6 topic mastery scores. Clickable — click topic → navigate to it. | Recharts |
| `TopicCard` | Card in topic picker. Shows topic name, chapter count, user's mastery badge, recommended indicator. | — |
| `SessionSummary` | Post-session overlay. AI summary text, mastery delta visualization, next topic suggestion, rating input. | — |
| `HintButton` | Shows current hint level (0–3). On click: confirms hint request, posts to API with `hint_requested: true`. | — |

---

### State Management

> 🗂️ Use **Zustand** for global state (auth, active session metadata). Use **React Query (TanStack Query)** for all server state (problems, progress, session history). Keep component local state minimal — only UI state like panel width or animation phase.

| State slice | Store | Contents |
|---|---|---|
| Auth | Zustand | `user`, `token`, `isAuthenticated` |
| Active session | Zustand | `sessionId`, `messages[]`, `dialogueState`, `hintLevel`, `isStreaming` |
| Progress / mastery | React Query | Cached from `GET /api/progress/me` |
| Problem list | React Query | Cached + paginated from `GET /api/problems` |
| Session history | React Query | Cached from `GET /api/sessions` |

---

## 07 — 8-Week Sprint Plan

> Week-by-week task breakdown. AI pipeline first — no UI work in Sprint 1.

---

### Sprint 1 — Socratic AI Engine (Weeks 1–2)

**Week 1 — Foundation** *(Days 1–7)*
- Set up FastAPI project + folder structure
- Configure Claude API client with streaming
- Write Socratic system prompt v1 (Vietnamese)
- Implement dialogue state machine (4 states)
- Build session context builder (problem + history + misconceptions)
- Create problem bank JSON (first 50 problems)
- Test 5 full Socratic sessions via curl/Postman

**Week 2 — Refinement** *(Days 8–14)*
- Implement hint escalation system (L0–L3)
- Add geometry detection + render_geometry tool spec
- Set up PostgreSQL + run init migration
- Implement session CRUD endpoints (without auth)
- Load misconceptions catalog per topic
- Prompt iteration — test AI never gives direct answer
- Expand problem bank to 100 problems

> ✓ **Gate:** 10 full Socratic sessions end-to-end via API. AI never reveals full answer in single turn. Dialogue state transitions correctly.

---

### Sprint 2 — Core UI + 3D Viewer + Auth (Weeks 3–4)

**Week 3 — Scaffold** *(Days 15–21)*
- Next.js 14 project init + Tailwind + folder structure
- Google OAuth via NextAuth.js
- JWT integration with FastAPI backend
- Basic ChatPanel + MessageBubble components
- SSE streaming hook (useSSE)
- KaTeX inline math rendering in messages
- Topic picker page + routing

**Week 4 — 3D Viewer** *(Days 22–28)*
- Three.js setup + OrbitControls + CSS2DRenderer
- Pyramid renderer (square base, labeled vertices)
- Prism renderer (triangular + rectangular)
- Sphere + Cone renderers
- Integrate GeometryViewer into MessageBubble
- Session/[id] page: split chat + context panel
- Session persistence — messages saved to DB

> ✓ **Gate:** End-to-end session in browser. Geometry problem triggers 3D viewer automatically. Auth works. Messages persist across refresh.

---

### Sprint 3 — Progress, Roles & Polish (Weeks 5–6)

**Week 5 — Progress Layer** *(Days 29–35)*
- Mastery score computation + DB update on session complete
- Progress API endpoints (GET /api/progress/me)
- Student dashboard: mastery radar chart (Recharts)
- Weekly activity chart on dashboard
- Session summary overlay (post-session)
- Next topic suggestion logic
- Session history page

**Week 6 — Admin + 3D Features** *(Days 36–42)*
- Admin role + route guard
- Admin dashboard: DAU chart, top errors, viewer usage
- Cross-section slider on 3D viewer
- Step-by-step construction animation
- Measurement overlay on 3D edges
- Hint button + hint level indicator in chat
- Mobile responsive layout pass (chat + viewer)

> ✓ **Gate:** Both roles work. Mastery scores update after each session. Admin can see platform stats. 3D viewer works on mobile browser.

---

### Sprint 4 — Polish, Pilot & Launch Prep (Weeks 7–8)

**Week 7 — Pilot Launch** *(Days 43–49)*
- Deploy frontend to Vercel
- Deploy backend + DB to Railway
- Configure Sentry on frontend + backend
- Set up GitHub Actions CI (lint + test on PR)
- Recruit 10–15 Grade 12 pilot students
- Onboard pilots — collect first session feedback
- Expand problem bank to 200+ problems

**Week 8 — Fix & Demo Prep** *(Days 50–56)*
- Fix top issues from pilot feedback
- Error state handling (API failures, empty states)
- Loading skeletons + optimistic UI
- Performance: lazy-load 3D viewer, split bundle
- Write README + setup + deploy guide
- Clean Git history + remove debug logs
- Demo dry-run on production URL

> ✓ **Gate:** 10+ pilot students have completed sessions. Return rate > 40%. Demo works live on production URL without any localhost dependency.

---

## 08 — Environment & Testing

> All environment variables, testing strategy, and CI/CD pipeline.

### Environment Variables

| Variable | Value |
|---|---|
| `ANTHROPIC_API_KEY` | sk-ant-... (backend only, never exposed to client) |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@host:5432/toansc |
| `REDIS_URL` | redis://default:pass@host:6379 |
| `JWT_SECRET` | 64+ char random string (generate with openssl rand -hex 32) |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 secret (backend only) |
| `NEXTAUTH_SECRET` | Random 32+ char string for NextAuth session encryption |
| `NEXTAUTH_URL` | https://toan-socratic.vercel.app (production URL) |
| `NEXT_PUBLIC_API_URL` | https://api.toan-socratic.railway.app |
| `SENTRY_DSN` | From Sentry project settings (both frontend + backend) |
| `R2_ACCOUNT_ID` | Cloudflare R2 for asset storage |
| `R2_ACCESS_KEY_ID / SECRET` | R2 API credentials |

---

### Testing Strategy

#### 🧪 Backend Unit Tests
- Mastery score computation algorithm
- Dialogue state machine transitions
- Hint level escalation logic
- Problem bank JSON schema validation
- JWT auth middleware
- Geometry params serialization

#### 🤖 AI Behavior Tests
- AI does not reveal full answer in first turn
- Vietnamese language consistency
- Geometry tool triggered on 3D problems
- Hint level respected in prompt injection
- LaTeX syntax correct in AI responses
- L3 hint shows complete solution

#### 🖥️ Frontend Component Tests
- ChatPanel renders streamed messages correctly
- GeometryViewer loads for all 6 solid types
- KaTeX renders inline math without errors
- Auth redirect on unauthenticated access
- Session summary triggers on completion
- Hint button advances level correctly

#### 🌐 E2E Tests (Playwright)
- Full session flow: login → topic → session → complete
- Geometry session: 3D viewer renders and rotates
- Hint escalation: 3 requests reach L3
- Dashboard mastery updates post-session
- Admin can view stats (student cannot)
- Mobile viewport: chat + viewer usable

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
      - run: pytest tests/ -v       # unit tests

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint           # ESLint
      - run: npm run type-check     # TypeScript
      - run: npm run test           # Vitest component tests

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [backend, frontend]
    steps:
      # Vercel deploys automatically on push to main
      # Railway deploys automatically via GitHub integration
      - run: echo "✅ All checks passed — auto-deploying"
```

---

*Toán Socratic · Implementation Spec v1.0 · 8 weeks · 4 sprints · Next.js + FastAPI + Claude + Three.js*
