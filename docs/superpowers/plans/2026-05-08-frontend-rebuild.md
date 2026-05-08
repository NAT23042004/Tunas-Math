# Frontend Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete the broken frontend/ directory and rebuild it from scratch following the Toán Socratic Implementation Plan Section 6 (Frontend Architecture).

**Architecture:** Next.js 14 App Router with route groups `(auth)`, `(student)`, `(admin)` for isolated layouts. Zustand for global client state (auth, active session). TanStack Query for all server state (problems, progress, history). Three.js for procedural 3D geometry rendering. NextAuth.js with Google OAuth for authentication.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS 3.x, KaTeX + react-katex, Three.js + @react-three/fiber + @react-three/drei, NextAuth.js 4.x, Zustand, TanStack Query 5.x, Recharts, Radix UI

---

## File Structure

```
frontend/
├── app/
│   ├── layout.tsx                     # Root layout: fonts, auth provider
│   ├── page.tsx                       # Landing / redirect to /dashboard
│   ├── (auth)/
│   │   ├── login/page.tsx             # Google OAuth button
│   │   └── register/page.tsx          # Onboarding page
│   ├── (student)/
│   │   ├── layout.tsx                 # Sidebar nav + auth guard
│   │   ├── dashboard/page.tsx         # Mastery radar, weekly activity
│   │   ├── topics/page.tsx            # Topic picker grid
│   │   ├── topics/[id]/page.tsx       # Chapter view + problem list
│   │   ├── session/
│   │   │   ├── new/page.tsx           # Session config page
│   │   │   └── [id]/page.tsx         # Active session: Chat + 3D viewer
│   │   └── history/page.tsx           # Past sessions list
│   └── (admin)/
│       ├── layout.tsx                 # Admin nav + role guard
│       └── dashboard/page.tsx         # Platform stats
├── components/
│   ├── ChatPanel.tsx                 # Conversation thread + SSE stream
│   ├── MessageBubble.tsx             # Single message renderer
│   ├── ChatInput.tsx                 # Text input + hint button
│   ├── GeometryViewer.tsx            # Three.js 3D geometry renderer
│   ├── ContextPanel.tsx              # Right sidebar in session
│   ├── MasteryRadar.tsx             # Recharts radar chart
│   ├── TopicCard.tsx                 # Topic picker card
│   ├── SessionSummary.tsx            # Post-session overlay
│   └── HintButton.tsx                # Hint level indicator + button
├── lib/
│   ├── authStore.ts                  # Zustand auth store
│   ├── sessionStore.ts               # Zustand active session store
│   ├── api.ts                        # Axios instance + API functions
│   ├── useSSE.ts                     # SSE streaming hook
│   ├── useAuth.ts                    # Auth hook wrapping NextAuth
│   ├── useDashboard.ts               # React Query for progress/me
│   └── useTopics.ts                  # React Query for problems
├── types/
│   └── index.ts                      # Shared TypeScript types
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

---

### Task 1: Delete broken frontend/ directory

**Files:**
- Delete: `frontend/` (entire directory)

- [ ] **Step 1: Remove the entire frontend directory**

```bash
rm -rf /home/natus/Project/Tunas-Math/frontend
```

- [ ] **Step 2: Verify deletion**

```bash
ls /home/natus/Project/Tunas-Math/frontend 2>&1
# Expected: "No such file or directory"
```

- [ ] **Step 3: Commit the deletion**

```bash
git add -A
git commit -m "chore: remove broken frontend directory for rebuild"
```

---

### Task 2: Scaffold Next.js 14 project

**Files:**
- Create: `frontend/` (via create-next-app)
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`

- [ ] **Step 1: Create Next.js 14 project with TypeScript and Tailwind**

```bash
cd /home/natus/Project/Tunas-Math
npx create-next-app@14 frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
```

- [ ] **Step 2: Verify project created**

```bash
ls /home/natus/Project/Tunas-Math/frontend/package.json
# Expected: file exists
```

- [ ] **Step 3: Create .env.example file**

```bash
cat > /home/natus/Project/Tunas-Math/frontend/.env.example << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=generate_with_openssl_rand_-hex_32
NEXTAUTH_URL=http://localhost:3000
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
NEXT_PUBLIC_SITE_URL=http://localhost:3000
EOF
```

- [ ] **Step 4: Commit scaffold**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js 14 project with TypeScript and Tailwind"
```

---

### Task 3: Install dependencies

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install UI and state management dependencies**

```bash
cd /home/natus/Project/Tunas-Math/frontend
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs @tanstack/react-query zustand axios class-variance-authority clsx tailwind-merge katex react-katex recharts
```

- [ ] **Step 2: Install 3D visualization dependencies**

```bash
npm install @react-three/fiber @react-three/drei three
```

- [ ] **Step 3: Install NextAuth**

```bash
npm install next-auth@4
```

- [ ] **Step 4: Install dev dependencies for types**

```bash
npm install -D @types/three @types/node @types/react @types/react-dom
```

- [ ] **Step 5: Verify installations**

```bash
npm list --depth=0 | grep -E "next-auth|@tanstack|zustand|three|recharts|katex"
# Expected: all packages shown
```

- [ ] **Step 6: Commit package changes**

```bash
git add package.json package-lock.json
git commit -m "feat: add frontend dependencies (NextAuth, React Query, Zustand, Three.js, Recharts, KaTeX)"
```

---

### Task 4: Create TypeScript types

**Files:**
- Create: `frontend/types/index.ts`

- [ ] **Step 1: Write shared types**

```typescript
// frontend/types/index.ts

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: 'student' | 'admin';
}

export interface Session {
  id: string;
  user_id: string;
  problem_id?: string;
  topic_id: string;
  status: 'active' | 'completed' | 'abandoned';
  dialogue_state: 'review' | 'heuristic' | 'rectify' | 'summarize';
  hint_level: number;
  hint_count: number;
  fail_count: number;
  messages: Message[];
  summary?: string;
  student_rating?: number;
  started_at: string;
  ended_at?: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  tool_call?: ToolCall;
}

export interface ToolCall {
  name: string;
  input: Record<string, unknown>;
}

export interface Problem {
  id: string;
  topic_id: string;
  statement_latex: string;
  difficulty: 'easy' | 'medium' | 'hard';
  is_geometry: boolean;
  geometry_params?: GeometryParams;
  source?: string;
}

export interface GeometryParams {
  solid_type: 'pyramid' | 'prism' | 'cone' | 'sphere' | 'cylinder' | 'composite';
  params: Record<string, unknown>;
  labels?: Record<string, string>;
}

export interface MasteryData {
  mastery_by_topic: Record<string, number>;
  sessions_this_week: number;
  suggested_topics: string[];
  streak_days: number;
}

export interface SolidSpec {
  solid_type: 'pyramid' | 'prism' | 'cone' | 'sphere' | 'cylinder' | 'composite';
  params: Record<string, unknown>;
  highlights?: string[];
  animated?: boolean;
}

export interface SessionCreateRequest {
  topic_id: string;
  problem_id?: string;
  initial_message?: string;
}

export interface SessionMessageRequest {
  content: string;
  hint_requested?: boolean;
}

export interface SessionCompleteRequest {
  student_rating?: number;
}
```

- [ ] **Step 2: Commit types**

```bash
git add types/
git commit -m "feat: add shared TypeScript types for frontend"
```

---

### Task 5: Create API client

**Files:**
- Create: `frontend/lib/api.ts`

- [ ] **Step 1: Write API client with axios**

```typescript
// frontend/lib/api.ts
import axios from 'axios';
import type { SessionCreateRequest, SessionMessageRequest, SessionCompleteRequest, Problem, MasteryData } from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export async function createSession(data: SessionCreateRequest): Promise<{ session_id: string; first_message: string; geometry_params: unknown }> {
  const res = await api.post('/api/sessions', data);
  return res.data;
}

export async function sendMessage(sessionId: string, data: SessionMessageRequest): Promise<ReadableStream> {
  const res = await fetch(`${api.defaults.baseURL}/api/sessions/${sessionId}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
    body: JSON.stringify(data),
  });
  return res.body!;
}

export async function completeSession(sessionId: string, data: SessionCompleteRequest): Promise<{ summary: string; mastery_delta: number; next_suggested_topic: string }> {
  const res = await api.put(`/api/sessions/${sessionId}/complete`, data);
  return res.data;
}

export async function getProblems(topicId?: string, difficulty?: string, isGeometry?: boolean): Promise<Problem[]> {
  const params = new URLSearchParams();
  if (topicId) params.set('topic_id', topicId);
  if (difficulty) params.set('difficulty', difficulty);
  if (isGeometry !== undefined) params.set('is_geometry', String(isGeometry));
  const res = await api.get(`/api/problems?${params.toString()}`);
  return res.data;
}

export async function getMyProgress(): Promise<MasteryData> {
  const res = await api.get('/api/progress/me');
  return res.data;
}

export async function getSessionHistory(sessionId: string): Promise<{ session: unknown; messages: unknown[]; problem: unknown }> {
  const res = await api.get(`/api/sessions/${sessionId}`);
  return res.data;
}

export default api;
```

- [ ] **Step 2: Commit lib files**

```bash
git add lib/api.ts
git commit -m "feat: add API client with axios"
```

---

### Task 6: Create Zustand stores

**Files:**
- Create: `frontend/lib/authStore.ts`
- Create: `frontend/lib/sessionStore.ts`

- [ ] **Step 1: Write auth store**

```typescript
// frontend/lib/authStore.ts
import { create } from 'zustand';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  setAuth: (user, token) => {
    localStorage.setItem('accessToken', token);
    set({ user, token, isAuthenticated: true });
  },
  clearAuth: () => {
    localStorage.removeItem('accessToken');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
```

- [ ] **Step 2: Write session store**

```typescript
// frontend/lib/sessionStore.ts
import { create } from 'zustand';
import type { Message } from '@/types';

interface SessionState {
  sessionId: string | null;
  messages: Message[];
  dialogueState: string;
  hintLevel: number;
  isStreaming: boolean;
  setSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  setStreaming: (val: boolean) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  messages: [],
  dialogueState: 'review',
  hintLevel: 0,
  isStreaming: false,
  setSession: (id) => set({ sessionId: id, messages: [], dialogueState: 'review', hintLevel: 0 }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setStreaming: (val) => set({ isStreaming: val }),
  clearSession: () => set({ sessionId: null, messages: [], dialogueState: 'review', hintLevel: 0, isStreaming: false }),
}));
```

- [ ] **Step 3: Commit stores**

```bash
git add lib/authStore.ts lib/sessionStore.ts
git commit -m "feat: add Zustand stores for auth and session state"
```

---

### Task 7: Create React Query hooks

**Files:**
- Create: `frontend/lib/useAuth.ts`
- Create: `frontend/lib/useDashboard.ts`
- Create: `frontend/lib/useTopics.ts`

- [ ] **Step 1: Write useAuth hook**

```typescript
// frontend/lib/useAuth.ts
import { useSession } from 'next-auth/react';
import { useAuthStore } from './authStore';

export function useAuth() {
  const { data: session, status } = useSession();
  const { setAuth, clearAuth } = useAuthStore();

  const isAuthenticated = status === 'authenticated' && !!session;

  return { session, status, isAuthenticated, setAuth, clearAuth };
}
```

- [ ] **Step 2: Write useDashboard hook**

```typescript
// frontend/lib/useDashboard.ts
import { useQuery } from '@tanstack/react-query';
import { getMyProgress } from './api';
import type { MasteryData } from '@/types';

export function useDashboard() {
  return useQuery<MasteryData, Error>({
    queryKey: ['progress', 'me'],
    queryFn: getMyProgress,
  });
}
```

- [ ] **Step 3: Write useTopics hook**

```typescript
// frontend/lib/useTopics.ts
import { useQuery } from '@tanstack/react-query';
import { getProblems } from './api';
import type { Problem } from '@/types';

export function useTopics(topicId?: string, difficulty?: string, isGeometry?: boolean) {
  return useQuery<Problem[], Error>({
    queryKey: ['problems', topicId, difficulty, isGeometry],
    queryFn: () => getProblems(topicId, difficulty, isGeometry),
  });
}
```

- [ ] **Step 4: Commit hooks**

```bash
git add lib/useAuth.ts lib/useDashboard.ts lib/useTopics.ts
git commit -m "feat: add React Query hooks for auth, dashboard, and topics"
```

---

### Task 8: Build core components - Chat

**Files:**
- Create: `frontend/components/ChatPanel.tsx`
- Create: `frontend/components/MessageBubble.tsx`
- Create: `frontend/components/ChatInput.tsx`

- [ ] **Step 1: Write ChatInput component**

```tsx
// frontend/components/ChatInput.tsx
'use client';

import { useState } from 'react';

interface ChatInputProps {
  onSend: (content: string, hintRequested?: boolean) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [content, setContent] = useState('');

  const handleSubmit = (hintRequested?: boolean) => {
    if (!content.trim() && !hintRequested) return;
    onSend(content, hintRequested);
    setContent('');
  };

  return (
    <div className="flex gap-2 p-4 border-t">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
        }}
        placeholder="Nhập câu trả lời của bạn..."
        className="flex-1 resize-none rounded border p-2 text-sm"
        rows={2}
        disabled={disabled}
      />
      <button
        onClick={() => handleSubmit()}
        disabled={disabled || !content.trim()}
        className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        Gửi
      </button>
      <button
        onClick={() => handleSubmit(true)}
        disabled={disabled}
        className="rounded border px-4 py-2 text-sm disabled:opacity-50"
      >
        Gợi ý
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Write MessageBubble component**

```tsx
// frontend/components/MessageBubble.tsx
'use client';

import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import type { Message } from '@/types';
import GeometryViewer from './GeometryViewer';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const renderContent = (text: string) => {
    const parts = text.split(/(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)/g);
    return parts.map((part, i) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        return <BlockMath key={i} math={part.slice(2, -2)} />;
      } else if (part.startsWith('$') && part.endsWith('$')) {
        return <InlineMath key={i} math={part.slice(1, -1)} />;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
        {message.tool_call?.name === 'render_geometry' ? (
          <GeometryViewer solidSpec={message.tool_call.input as Record<string, unknown>} height={300} />
        ) : (
          <div className="text-sm">{renderContent(message.content)}</div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Write ChatPanel component**

```tsx
// frontend/components/ChatPanel.tsx
'use client';

import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import type { Message } from '@/types';

interface ChatPanelProps {
  messages: Message[];
  isStreaming: boolean;
  streamingText: string;
  onSend: (content: string, hintRequested?: boolean) => void;
}

export default function ChatPanel({ messages, isStreaming, streamingText, onSend }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {isStreaming && streamingText && (
          <div className="flex justify-start mb-3">
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900">
              <div className="text-sm">{streamingText}</div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={onSend} disabled={isStreaming} />
    </div>
  );
}
```

- [ ] **Step 4: Commit chat components**

```bash
git add components/ChatPanel.tsx components/MessageBubble.tsx components/ChatInput.tsx
git commit -m "feat: add ChatPanel, MessageBubble, and ChatInput components"
```

---

### Task 9: Build GeometryViewer component

**Files:**
- Create: `frontend/components/GeometryViewer.tsx`

- [ ] **Step 1: Write GeometryViewer component (pyramid only for MVP)**

```tsx
// frontend/components/GeometryViewer.tsx
'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';

interface GeometryViewerProps {
  solidSpec: { solid_type: string; params: Record<string, unknown>; highlights?: string[]; animated?: boolean };
  width?: number;
  height?: number;
}

function PyramidMesh({ params }: { params: Record<string, unknown> }) {
  const baseSide = (params.base_side as number) || 4;
  const height = (params.height as number) || 6;
  const baseShape = (params.base_shape as string) || 'square';

  const vertices: number[] = [];
  const indices: number[] = [];

  if (baseShape === 'square') {
    vertices.push(-baseSide / 2, 0, -baseSide / 2);
    vertices.push(baseSide / 2, 0, -baseSide / 2);
    vertices.push(baseSide / 2, 0, baseSide / 2);
    vertices.push(-baseSide / 2, 0, baseSide / 2);
    vertices.push(0, height, 0);

    indices.push(0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4);
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();

  return (
    <group>
      <mesh geometry={geometry}>
        <meshStandardMaterial color="#88ccee" transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>
      <lineSegments>
        <wireframeGeometry attach="geometry" args={[geometry]} />
        <lineBasicMaterial color="#444" />
      </lineSegments>
    </group>
  );
}

function VertexLabel({ position, label }: { position: [number, number, number]; label: string }) {
  return (
    <Text position={position} fontSize={0.4} color="#000" anchorX="center" anchorY="middle">
      {label}
    </Text>
  );
}

export default function GeometryViewer({ solidSpec, width = 400, height = 300 }: GeometryViewerProps) {
  const { solid_type, params, highlights } = solidSpec;

  if (solid_type !== 'pyramid') {
    return <div className="flex items-center justify-center h-full text-gray-500">Geometry type not yet supported: {solid_type}</div>;
  }

  const apexLabel = (params.apex_label as string) || 'S';
  const baseLabels = (params.base_labels as string[]) || ['A', 'B', 'C', 'D'];
  const baseSide = (params.base_side as number) || 4;
  const pyramidHeight = (params.height as number) || 6;

  return (
    <div style={{ width, height }} className="border rounded bg-gray-50">
      <Canvas camera={{ position: [8, 8, 8], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={0.8} />
        <PyramidMesh params={params} />
        <VertexLabel position={[0, pyramidHeight, 0]} label={apexLabel} />
        <VertexLabel position={[-baseSide / 2, 0, -baseSide / 2]} label={baseLabels[0]} />
        <VertexLabel position={[baseSide / 2, 0, -baseSide / 2]} label={baseLabels[1]} />
        <VertexLabel position={[baseSide / 2, 0, baseSide / 2]} label={baseLabels[2]} />
        <VertexLabel position={[-baseSide / 2, 0, baseSide / 2]} label={baseLabels[3]} />
        {params.show_altitude && (
          <lineSegments>
            <bufferGeometry>
              <float32BufferAttribute attach="attributes-position" args={[[0, pyramidHeight, 0, 0, 0, 0]]} count={2} itemSize={3} />
            </bufferGeometry>
            <lineDashedMaterial color="red" dashSize={0.2} gapSize={0.1} />
          </lineSegments>
        )}
        <OrbitControls />
        <gridHelper args={[10, 10]} />
      </Canvas>
    </div>
  );
}
```

- [ ] **Step 2: Commit GeometryViewer**

```bash
git add components/GeometryViewer.tsx
git commit -m "feat: add GeometryViewer component with pyramid renderer"
```

---

### Task 10: Build remaining UI components

**Files:**
- Create: `frontend/components/ContextPanel.tsx`
- Create: `frontend/components/MasteryRadar.tsx`
- Create: `frontend/components/TopicCard.tsx`
- Create: `frontend/components/SessionSummary.tsx`
- Create: `frontend/components/HintButton.tsx`

- [ ] **Step 1: Write HintButton**

```tsx
// frontend/components/HintButton.tsx
'use client';

interface HintButtonProps {
  level: number;
  onRequest: () => void;
}

export default function HintButton({ level, onRequest }: HintButtonProps) {
  return (
    <button
      onClick={onRequest}
      className="flex items-center gap-1 rounded border px-3 py-1 text-sm hover:bg-gray-50"
    >
      <span>Gợi ý</span>
      <span className="rounded bg-gray-200 px-1.5 py-0.5 text-xs">L{level}</span>
    </button>
  );
}
```

- [ ] **Step 2: Write TopicCard**

```tsx
// frontend/components/TopicCard.tsx
'use client';

interface TopicCardProps {
  topicId: string;
  name: string;
  mastery?: number;
  isRecommended?: boolean;
  onClick: () => void;
}

export default function TopicCard({ name, mastery = 0, isRecommended, onClick }: TopicCardProps) {
  return (
    <button
      onClick={onClick}
      className="rounded-lg border p-4 text-left hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{name}</h3>
        {isRecommended && <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">Gợi ý</span>}
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${mastery * 100}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-500">Thành thạo: {Math.round(mastery * 100)}%</p>
    </button>
  );
}
```

- [ ] **Step 3: Write a minimal MasteryRadar (placeholder for Recharts integration)**

```tsx
// frontend/components/MasteryRadar.tsx
'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import type { MasteryData } from '@/types';

interface MasteryRadarProps {
  data: MasteryData;
}

export default function MasteryRadar({ data }: MasteryRadarProps) {
  const chartData = Object.entries(data.mastery_by_topic).map(([topic, score]) => ({
    topic: topic.split('.').pop(),
    score: score * 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={chartData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="topic" />
        <Radar name="Thành thạo" dataKey="score" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 4: Write ContextPanel**

```tsx
// frontend/components/ContextPanel.tsx
'use client';

import { InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import type { Message } from '@/types';

interface ContextPanelProps {
  problemStatement?: string;
  dialogueState: string;
  hintLevel: number;
  messages: Message[];
}

export default function ContextPanel({ problemStatement, dialogueState, hintLevel }: ContextPanelProps) {
  return (
    <div className="h-full overflow-y-auto border-l p-4">
      <h3 className="text-sm font-medium">Trạng thái hội thoại</h3>
      <div className="mt-2 rounded border p-2 text-sm">
        <span className="font-mono">{dialogueState}</span>
      </div>
      <div className="mt-2 text-sm">
        Mức gợi ý: <span className="font-mono">L{hintLevel}</span>
      </div>
      {problemStatement && (
        <div className="mt-4">
          <h4 className="text-sm font-medium">Đề bài</h4>
          <div className="mt-1 text-sm"><InlineMath math={problemStatement} /></div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Write SessionSummary**

```tsx
// frontend/components/SessionSummary.tsx
'use client';

import { useState } from 'react';

interface SessionSummaryProps {
  summary: string;
  masteryDelta: number;
  nextTopic: string;
  onRate: (rating: number) => void;
  onContinue: () => void;
}

export default function SessionSummary({ summary, masteryDelta, nextTopic, onRate, onContinue }: SessionSummaryProps) {
  const [rating, setRating] = useState(0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="rounded-lg bg-white p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold">Hoàn thành phiên học!</h2>
        <p className="mt-2 text-sm text-gray-600">{summary}</p>
        <div className="mt-3 text-sm">Tiến bộ: <span className="text-green-600">+{Math.round(masteryDelta * 100)}%</span></div>
        <div className="mt-4">
          <p className="text-sm">Bạn thấy bài này thế nào?</p>
          <div className="mt-1 flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button key={star} onClick={() => setRating(star)} className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}>
                ★
              </button>
            ))}
          </div>
        </div>
        <p className="mt-3 text-sm">Chủ đề tiếp theo: <span className="font-medium">{nextTopic}</span></p>
        <div className="mt-4 flex gap-2">
          <button onClick={() => { onRate(rating); onContinue(); }} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Tiếp tục</button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Commit remaining components**

```bash
git add components/
git commit -m "feat: add ContextPanel, MasteryRadar, TopicCard, SessionSummary, HintButton"
```

---

### Task 11: Set up NextAuth with Google OAuth

**Files:**
- Create: `frontend/app/api/auth/[...nextauth]/route.ts`
- Modify: `frontend/app/layout.tsx`
- Create: `frontend/app/(auth)/login/page.tsx`
- Create: `frontend/app/(auth)/register/page.tsx`

- [ ] **Step 1: Write NextAuth route handler**

```typescript
// frontend/app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as Record<string, unknown>).accessToken = token.accessToken;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
```

- [ ] **Step 2: Update root layout with NextAuth SessionProvider**

```tsx
// frontend/app/layout.tsx
import type { Metadata } from 'next';
import { SessionProvider } from 'next-auth/react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Toán Socratic - Gia sư Toán thông minh',
  description: 'Hệ thống gia sư Toán Socratic cho học sinh lớp 12',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Write login page**

```tsx
// frontend/app/(auth)/login/page.tsx
'use client';

import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleSignIn = async () => {
    await signIn('google', { callbackUrl: '/dashboard' });
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-sm rounded-lg border p-6">
        <h1 className="text-xl font-semibold text-center">Đăng nhập</h1>
        <p className="mt-2 text-center text-sm text-gray-600">Chào mừng đến với Toán Socratic</p>
        <button
          onClick={handleGoogleSignIn}
          className="mt-4 w-full rounded bg-blue-600 py-2 text-white hover:bg-blue-700"
        >
          Đăng nhập với Google
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Write register page (simple redirect to login)**

```tsx
// frontend/app/(auth)/register/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const router = useRouter();
  useEffect(() => { router.push('/login'); }, [router]);
  return null;
}
```

- [ ] **Step 5: Create minimal globals.css**

```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

- [ ] **Step 6: Commit auth setup**

```bash
git add app/api/auth/[...nextauth]/route.ts app/layout.tsx app/globals.css app/\(auth\)/
git commit -m "feat: set up NextAuth with Google OAuth provider"
```

---

### Task 12: Create (student) route group with auth guard

**Files:**
- Create: `frontend/app/(student)/layout.tsx`
- Create: `frontend/app/(student)/dashboard/page.tsx`
- Create: `frontend/app/(student)/topics/page.tsx`

- [ ] **Step 1: Write student layout with auth guard**

```tsx
// frontend/app/(student)/layout.tsx
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status, router]);

  if (status === 'loading') return <div className="p-8 text-center">Đang tải...</div>;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r p-4">
        <h2 className="text-lg font-semibold">Toán Socratic</h2>
        <nav className="mt-6 space-y-2">
          <a href="/dashboard" className="block rounded px-3 py-2 hover:bg-gray-100">Dashboard</a>
          <a href="/topics" className="block rounded px-3 py-2 hover:bg-gray-100">Chủ đề</a>
          <a href="/history" className="block rounded px-3 py-2 hover:bg-gray-100">Lịch sử</a>
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
```

- [ ] **Step 2: Write dashboard page (basic)**

```tsx
// frontend/app/(student)/dashboard/page.tsx
'use client';

import MasteryRadar from '@/components/MasteryRadar';
import { useDashboard } from '@/lib/useDashboard';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <div className="p-8">Đang tải...</div>;
  if (error) return <div className="p-8 text-red-600">Lỗi: {error.message}</div>;
  if (!data) return <div className="p-8">Không có dữ liệu</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Thành thạo theo chủ đề</h2>
          <div className="mt-4 h-80">
            <MasteryRadar data={data} />
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Hoạt động tuần này</h2>
          <p className="mt-4 text-3xl font-bold">{data.sessions_this_week}</p>
          <p className="text-sm text-gray-500">phiên học</p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Chuỗi ngày học</h2>
          <p className="mt-4 text-3xl font-bold">{data.streak_days}</p>
          <p className="text-sm text-gray-500">ngày liên tiếp</p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Write topics page (basic)**

```tsx
// frontend/app/(student)/topics/page.tsx
'use client';

import { useTopics } from '@/lib/useTopics';
import TopicCard from '@/components/TopicCard';

export default function TopicsPage() {
  const { data: topics, isLoading } = useTopics();

  if (isLoading) return <div className="p-8">Đang tải...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Chủ đề</h1>
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {topics?.map((topic) => (
          <TopicCard key={topic.id} topicId={topic.topic_id} name={topic.topic_id.split('.').pop() || topic.topic_id} mastery={0.5} />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit student routes**

```bash
git add app/\(student\)/
git commit -m "feat: add student layout with auth guard, dashboard, and topics pages"
```

---

### Task 13: Create session pages

**Files:**
- Create: `frontend/app/(student)/session/new/page.tsx`
- Create: `frontend/app/(student)/session/[id]/page.tsx`

- [ ] **Step 1: Write session new page (config page)**

```tsx
// frontend/app/(student)/session/new/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createSession } from '@/lib/api';

export default function NewSessionPage() {
  const [topicId, setTopicId] = useState('hinh-hoc.hinh-chop');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await createSession({ topic_id: topicId });
      router.push(`/session/${res.session_id}`);
    } catch {
      alert('Không thể tạo phiên học');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Bắt đầu phiên học mới</h1>
      <div className="mt-6 max-w-sm space-y-4">
        <div>
          <label className="block text-sm font-medium">Chủ đề</label>
          <select value={topicId} onChange={(e) => setTopicId(e.target.value)} className="mt-1 w-full rounded border p-2">
            <option value="hinh-hoc.hinh-chop">Hình học - Hình chóp</option>
            <option value="hinh-hoc.lang-tru">Hình học - Lăng trụ</option>
            <option value="giai-tich.dao-ham">Giải tích - Đạo hàm</option>
          </select>
        </div>
        <button onClick={handleStart} disabled={isLoading} className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50">
          {isLoading ? 'Đang tạo...' : 'Bắt đầu'}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Write active session page (Chat + ContextPanel)**

```tsx
// frontend/app/(student)/session/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import ChatPanel from '@/components/ChatPanel';
import ContextPanel from '@/components/ContextPanel';
import { useSessionStore } from '@/lib/sessionStore';
import { sendMessage, getSessionHistory } from '@/lib/api';
import type { Message } from '@/types';

export default function SessionPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const { messages, addMessage, setSession, setStreaming, isStreaming } = useSessionStore();
  const [streamingText, setStreamingText] = useState('');
  const [streamingToolUse, setStreamingToolUse] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    setSession(sessionId);
    getSessionHistory(sessionId).then((data) => {
      if (data.messages) {
        data.messages.forEach((msg: Message) => addMessage(msg));
      }
    });
  }, [sessionId, setSession, addMessage]);

  const handleSend = async (content: string, hintRequested?: boolean) => {
    setStreaming(true);
    setStreamingText('');
    setStreamingToolUse(null);

    const userMsg: Message = { role: 'user', content, timestamp: new Date().toISOString() };
    addMessage(userMsg);

    const stream = await sendMessage(sessionId, { content, hint_requested: hintRequested });

    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const parsed = JSON.parse(data);
            if (typeof parsed === 'string') setStreamingText((prev) => prev + parsed);
            else if (parsed.solid_type) setStreamingToolUse(parsed);
            else if (parsed.dialogue_state) setStreaming(false);
          } catch {
            setStreamingText((prev) => prev + data);
          }
        }
      }
    }

    const assistantMsg: Message = { role: 'assistant', content: streamingText, timestamp: new Date().toISOString() };
    if (streamingToolUse) (assistantMsg as Record<string, unknown>).tool_call = { name: 'render_geometry', input: streamingToolUse };
    addMessage(assistantMsg);
    setStreamingText('');
    setStreamingToolUse(null);
    setStreaming(false);
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatPanel messages={messages} isStreaming={isStreaming} streamingText={streamingText} onSend={handleSend} />
      </div>
      <div className="w-80">
        <ContextPanel dialogueState="review" hintLevel={0} messages={messages} />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit session pages**

```bash
git add app/\(student\)/session/
git commit -m "feat: add session new config page and active session chat page"
```

---

### Task 14: Create history page and admin routes

**Files:**
- Create: `frontend/app/(student)/history/page.tsx`
- Create: `frontend/app/(admin)/layout.tsx`
- Create: `frontend/app/(admin)/dashboard/page.tsx`
- Create: `frontend/app/page.tsx` (landing page)

- [ ] **Step 1: Write history page**

```tsx
// frontend/app/(student)/history/page.tsx
'use client';

export default function HistoryPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Lịch sử học tập</h1>
      <p className="mt-4 text-gray-500">Chức năng đang được phát triển...</p>
    </div>
  );
}
```

- [ ] **Step 2: Write admin layout with role guard**

```tsx
// frontend/app/(admin)/layout.tsx
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
    else if (session && (session.user as Record<string, unknown>).role !== 'admin') router.push('/dashboard');
  }, [session, status, router]);

  if (status === 'loading') return <div className="p-8 text-center">Đang tải...</div>;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r p-4">
        <h2 className="text-lg font-semibold">Admin Panel</h2>
        <nav className="mt-6 space-y-2">
          <a href="/admin/dashboard" className="block rounded px-3 py-2 hover:bg-gray-100">Dashboard</a>
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
```

- [ ] **Step 3: Write admin dashboard**

```tsx
// frontend/app/(admin)/dashboard/page.tsx
'use client';

export default function AdminDashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>
      <p className="mt-4 text-gray-500">Chức năng đang được phát triển...</p>
    </div>
  );
}
```

- [ ] **Step 4: Write landing page**

```tsx
// frontend/app/page.tsx
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'authenticated') router.push('/dashboard');
  }, [status, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Toán Socratic</h1>
        <p className="mt-4 text-lg text-gray-600">Gia sư Toán thông minh cho học sinh lớp 12</p>
        <button onClick={() => router.push('/login')} className="mt-6 rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700">
          Bắt đầu học
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Commit history, admin, and landing pages**

```bash
git add app/\(student\)/history/ app/\(admin\)/ app/page.tsx
git commit -m "feat: add history page, admin routes with role guard, and landing page"
```

---

### Task 15: Create topics/[id] page

**Files:**
- Create: `frontend/app/(student)/topics/[id]/page.tsx`

- [ ] **Step 1: Write topic detail page**

```tsx
// frontend/app/(student)/topics/[id]/page.tsx
'use client';

import { useParams } from 'next/navigation';

export default function TopicDetailPage() {
  const params = useParams();
  const topicId = params.id as string;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{topicId.split('.').pop()}</h1>
      <p className="mt-4 text-gray-500">Danh sách bài tập đang được cập nhật...</p>
      <button
        onClick={() => window.location.href = '/session/new'}
        className="mt-4 rounded bg-blue-600 px-4 py-2 text-white"
      >
        Bắt đầu học chủ đề này
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Commit topic detail page**

```bash
git add "app/(student)/topics/[id]/"
git commit -m "feat: add topic detail page with problem list placeholder"
```

---

### Task 16: Self-review and fix issues

- [ ] **Step 1: Check TypeScript types consistency**

```bash
cd /home/natus/Project/Tunas-Math/frontend
npx tsc --noEmit 2>&1 | head -50
# Fix any type errors found
```

- [ ] **Step 2: Check for placeholder patterns**

```bash
grep -rn "TODO\|TBD\|FIXME\|implement later" frontend/components/ frontend/lib/ frontend/app/
# Should return no results
```

- [ ] **Step 3: Verify all routes work (build test)**

```bash
cd /home/natus/Project/Tunas-Math/frontend
npm run build 2>&1 | tail -20
# Fix any build errors
```

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve TypeScript and build errors after rebuild"
```

---

### Task 17: Final test - end-to-end flow

- [ ] **Step 1: Start dev servers**

```bash
# Terminal 1: backend
cd /home/natus/Project/Tunas-Math/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

```bash
# Terminal 2: frontend
cd /home/natus/Project/Tunas-Math/frontend
npm run dev
```

- [ ] **Step 2: Test login flow**

Open http://localhost:3000, click "Bắt đầu học", complete Google OAuth, verify redirect to /dashboard.

- [ ] **Step 3: Test session flow**

From dashboard, navigate to /session/new, select topic, start session, verify chat loads with SSE streaming.

- [ ] **Step 4: Test 3D viewer**

Send a message about a geometry problem, verify GeometryViewer renders pyramid.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete frontend rebuild - all Sprint 2 features working"
```
