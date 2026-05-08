# Tunas-Math Frontend Rebuild Design

**Date:** 2026-05-08  
**Branch:** `feat/sprint2-frontend`  
**Scope:** Delete `frontend/` and rebuild from scratch following the Toán Socratic Implementation Plan (Section 6).

---

## 1. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Next.js 14 (App Router) | Chat UI, routing, SSR |
| Styling | Tailwind CSS 3.x | Utility-first styling |
| Math rendering | KaTeX + react-katex | Inline LaTeX in chat |
| 3D visualization | Three.js + @react-three/fiber + @react-three/drei | Interactive geometry viewer |
| Auth | NextAuth.js 4.x + Google OAuth | Session management |
| State (global) | Zustand | Auth, active session metadata |
| State (server) | TanStack Query (React Query) | Problems, progress, history |
| Charts | Recharts | Dashboard mastery radar |
| UI primitives | Radix UI | Dialog, dropdown, tabs |
| Language | TypeScript 5.x | Type safety |

Dependencies match the existing `package.json` — reinstalled via `create-next-app` with the same stack.

---

## 2. App Router Structure

```
frontend/app/
├── layout.tsx                    # Root: fonts, auth provider, Sentry
├── page.tsx                      # Landing (redirect to /dashboard if logged in)
│
├── (auth)/
│   ├── login/page.tsx            # Google OAuth button
│   └── register/page.tsx        # Onboarding: name, grade, goals
│
├── (student)/
│   ├── layout.tsx                # Sidebar nav + auth guard
│   ├── dashboard/page.tsx        # Mastery radar, weekly activity, suggestions
│   ├── topics/page.tsx           # Topic picker grid
│   ├── topics/[id]/page.tsx      # Chapter view + problem list
│   ├── session/
│   │   ├── new/page.tsx          # Session config (topic, difficulty)
│   │   └── [id]/page.tsx         # Active: Chat + 3D viewer split
│   └── history/page.tsx          # Past sessions + transcript review
│
└── (admin)/
    ├── layout.tsx                # Admin nav + role guard
    └── dashboard/page.tsx        # Platform stats, error patterns, user list
```

Route groups `(auth)`, `(student)`, `(admin)` isolate layouts. Auth guards in `(student)/layout.tsx` and `(admin)/layout.tsx`.

---

## 3. Core Components

| Component | Responsibility | Key Dependencies |
|---|---|---|
| `ChatPanel` | Renders conversation thread. Handles SSE stream, auto-scroll, message types. | `useSSE` hook, react-katex |
| `MessageBubble` | Single message — text with KaTeX, or `GeometryViewer` if tool_call. | KaTeX, GeometryViewer |
| `ChatInput` | Text area with hint button, send button. Enter-to-send, Shift+Enter newline. | — |
| `GeometryViewer` | Three.js canvas. Accepts `SolidSpec` JSON, procedurally generates geometry. | Three.js, CSS2DRenderer |
| `ContextPanel` | Right sidebar: problem statement, hint level, dialogue phase, timer. | react-katex |
| `MasteryRadar` | Recharts RadarChart of topic mastery scores. Clickable. | Recharts |
| `TopicCard` | Topic picker card: name, mastery badge, recommended indicator. | — |
| `SessionSummary` | Post-session overlay: AI summary, mastery delta, rating input. | — |
| `HintButton` | Shows hint level (0–3). On click: confirms and posts `hint_requested: true`. | — |

---

## 4. State Management

| State slice | Store | Contents |
|---|---|---|
| Auth | Zustand | `user`, `token`, `isAuthenticated` |
| Active session | Zustand | `sessionId`, `messages[]`, `dialogueState`, `hintLevel`, `isStreaming` |
| Progress / mastery | React Query | Cached from `GET /api/progress/me` |
| Problem list | React Query | Cached + paginated from `GET /api/problems` |
| Session history | React Query | Cached from `GET /api/sessions` |

Zustand for ephemeral client state. React Query for all server state — handles caching, refetching, stale-while-revalidate.

---

## 5. Key Hooks

| Hook | Purpose |
|---|---|
| `useSSE(url, body)` | Streams SSE from `/api/sessions/:id/message`, returns `{data, done, toolUse}` |
| `useAuth()` | Wraps NextAuth `useSession()`, returns `{user, token, isAuthenticated}` |
| `useDashboard()` | React Query wrapper for `GET /api/progress/me` |
| `useTopics()` | React Query wrapper for `GET /api/problems` with topic filter |

---

## 6. API Integration

All endpoints except `POST /auth/*` require `Authorization: Bearer <JWT>` header.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/sessions` | POST | Start new Socratic session |
| `/api/sessions/:id/message` | POST | Send message, receive SSE stream |
| `/api/sessions/:id` | GET | Retrieve session history |
| `/api/sessions/:id/complete` | PUT | Mark complete, update mastery |
| `/api/problems` | GET | Fetch problems with filters |
| `/api/progress/me` | GET | Student mastery map |
| `/api/admin/stats` | GET | Platform analytics (admin only) |

---

## 7. Build & Deploy

| Item | Value |
|---|---|
| Build command | `next build` |
| Dev command | `next dev` |
| Deploy target | Vercel |
| Environment | `NEXT_PUBLIC_API_URL`, `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |

---

## 8. Rebuild Steps (Execution Order)

1. Delete `frontend/` directory
2. Run `npx create-next-app@14 frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"`
3. Install dependencies: `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-tabs`, `@react-three/fiber`, `@react-three/drei`, `three`, `@types/three`, `axios`, `next-auth@4`, `@tanstack/react-query`, `katex`, `react-katex`, `recharts`, `zustand`, `class-variance-authority`, `clsx`, `tailwind-merge`
4. Create folder structure (app/(auth), app/(student), app/(admin))
5. Set up NextAuth with Google OAuth provider
6. Create Zustand stores (auth, active session)
7. Build core components: ChatPanel, MessageBubble, ChatInput, GeometryViewer
8. Build page routes: login, dashboard, topics, session/new, session/[id], history
9. Wire up API hooks: useSSE, useDashboard, useTopics
10. Add auth guards in (student)/layout.tsx and (admin)/layout.tsx
11. Test end-to-end: login → topic → session → 3D viewer → complete
