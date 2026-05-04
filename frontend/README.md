# Toán Socratic - Frontend

Next.js 14 frontend for the AI-powered Vietnamese math tutoring application.

## 🛠️ Tech Stack

- **Next.js 14** - App Router with React Server Components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Three.js / React Three Fiber** - 3D geometry visualization
- **NextAuth** - Google OAuth authentication
- **React Query (TanStack)** - State management and caching
- **KaTeX** - Math formula rendering
- **Recharts** - Progress visualization

## 📁 Project Structure

```
frontend/
├── app/
│   ├── api/auth/[...nextauth]/  # NextAuth API route
│   ├── components/                # React components
│   ├── lib/                      # Utilities and API client
│   │   ├── api.ts               # Centralized API client
│   │   ├── types.ts             # TypeScript type definitions
│   │   └── useChat.ts          # React Query hooks
│   ├── login/                   # Login page
│   ├── session/                 # Chat session page
│   ├── topics/                  # Topics listing page
│   ├── dashboard/               # User dashboard
│   ├── layout.tsx               # Root layout with providers
│   ├── providers.tsx            # Session & Query providers
│   └── page.tsx                 # Home page
├── components/                   # Shared components
│   ├── ChatInterface.tsx        # Main chat interface
│   ├── Message.tsx              # Message bubble component
│   ├── LoadingDots.tsx          # Loading animation
│   └── GeometryViewer.tsx      # 3D geometry viewer
├── public/                       # Static assets
├── middleware.ts                 # Route protection
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## 🧪 Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Type checking
npm run type-check
```

## 📖 Key Features

### Authentication

- Google OAuth integration with NextAuth
- Session management with JWT tokens
- Route protection via middleware
- Automatic redirect to login for unauthenticated users

### Chat Interface

- Real-time streaming responses via Server-Sent Events (SSE)
- Progressive message display as AI responds
- Hint system with 4 levels (L0-L3)
- Dialogue state tracking (REVIEW, HEURISTIC, RECTIFY, SUMMARIZE)
- Auto-scroll to latest message

### 3D Geometry Viewer

- Interactive 3D visualization with Three.js
- Support for pyramids, prisms, and other geometric solids
- Rotate, zoom, and explore geometric shapes
- Integrated with problem geometry parameters

### State Management

- React Query for server state (sessions, problems)
- Custom hooks (`useChat`) for chat functionality
- Efficient caching and automatic refetching
- Optimistic updates for better UX

## 🔗 API Integration

The frontend communicates with the backend via a centralized API client (`lib/api.ts`):

- `createSession()` - Create new Socratic session
- `getProblems()` - Fetch problems with filters
- `sendMessageStream()` - Send message with streaming response
- `completeSession()` - Mark session as complete
- `getProgress()` - Fetch user progress

All API calls support optional JWT token for authentication.

## 📦 Deployment

### Vercel (Recommended)

```bash
vercel --prod
```

Set environment variables in Vercel dashboard:

- `NEXT_PUBLIC_API_URL` - Backend API URL
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `NEXTAUTH_SECRET` - NextAuth secret
- `NEXTAUTH_URL` - Production URL

## 🎨 Styling

- Tailwind CSS for utility-first styling
- Custom design system with CSS variables
- Responsive design for all screen sizes
- Dark mode support (planned)
