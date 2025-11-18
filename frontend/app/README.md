# Frontend App Module

## Overview

The `frontend/app` directory contains the Next.js 14 application using the App Router architecture. It handles all user interface rendering, authentication flows, and dashboard pages for the CreatorIQ platform.

## File Structure

```
frontend/app/
├── globals.css                    # Global styles and Tailwind imports
├── layout.tsx                     # Root layout with metadata and viewport
├── (auth)/                        # Auth route group (unauthenticated routes)
│   ├── layout.tsx                 # Auth layout with centered card design
│   ├── login/page.tsx             # Login page with email + Google OAuth
│   └── register/page.tsx          # Registration page
└── (dashboard)/                   # Dashboard route group (protected routes)
    ├── layout.tsx                 # Dashboard layout with auth guard
    ├── MobileNav.tsx              # Mobile bottom navigation component
    ├── dashboard/page.tsx         # Main dashboard with overview stats
    ├── channel/page.tsx            # YouTube channel connection/management
    ├── competitors/               # Competitor analysis pages
    │   ├── page.tsx               # Competitor list
    │   └── [id]/page.tsx          # Competitor detail view
    ├── gaps/page.tsx              # Content gap detection
    ├── hooks/page.tsx             # Viral hook generation
    ├── scripts/                   # Script management
    │   ├── page.tsx               # Script list
    │   ├── new/page.tsx           # Script generation form
    │   └── [id]/page.tsx          # Script detail view
    ├── research/page.tsx          # Topic/competitor research
    ├── settings/page.tsx          # User settings
    ├── thumbnails/page.tsx        # Thumbnail analysis
    └── trends/page.tsx            # Trend tracking
```

## Route Groups

### (auth) Route Group

Unauthenticated routes wrapped in a minimal layout with centered card design. These routes are accessible without authentication:
- `/login` - Email/password and Google OAuth login
- `/register` - User registration

**Auth Layout** ([`layout.tsx`](frontend/app/(auth)/layout.tsx:1)):
- Full-screen gradient background
- Centered card with CreatorIQ branding
- No sidebar or navigation (auth UI only)

### (dashboard) Route Group

Protected routes requiring authentication. All routes in this group:
- Automatically redirect to `/login` if no access token is found
- Share the dashboard layout with Sidebar, TopBar, and MobileNav

**Dashboard Layout** ([`layout.tsx`](frontend/app/(dashboard)/layout.tsx:1)):
- Auth check via `useStore().accessToken` or localStorage
- Flex layout with Sidebar (desktop) + MobileNav (mobile)
- TopBar for page title and user actions

## Key Components

### Root Layout ([`layout.tsx`](frontend/app/layout.tsx:1))

Next.js 14 root layout with comprehensive metadata:

```typescript
export const metadata: Metadata = {
  title: { default: "CreatorIQ - AI Growth Intelligence for Creators", template: "%s | CreatorIQ" },
  description: "AI-powered YouTube growth intelligence platform...",
  keywords: ["YouTube growth", "content creator tools", ...],
  openGraph: { type: "website", locale: "en_US", url: "https://creatoriq.io", ... },
  twitter: { card: "summary_large_image", ... },
  icons: { icon: [{ url: "/favicon.svg", type: "image/svg+xml" }], ... },
  manifest: "/manifest.json",
  robots: { index: true, follow: true, ... },
}
```

**Viewport Configuration:**
```typescript
export const viewport: Viewport = {
  themeColor: "#6366f1",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
}
```

### Auth Pages

#### Login Page ([`login/page.tsx`](frontend/app/(auth)/login/page.tsx:1))

Features:
- Google OAuth button with branded icon
- Email/password form with validation
- Error display for failed login attempts
- Link to registration page

**Authentication Flow:**
1. User enters credentials or clicks Google OAuth
2. On success, `setAccessToken(tokenResp.data.access_token)` stores JWT
3. Fetch user profile with `authApi.me()` and `setUser(userResp.data)`
4. Redirect to `/dashboard`

**Google OAuth URL Construction:**
```typescript
const scope = encodeURIComponent("openid email profile https://www.googleapis.com/auth/youtube.readonly");
const redirect = encodeURIComponent(`${window.location.origin}/auth/callback`);
window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirect}&response_type=code&scope=${scope}&access_type=offline&prompt=consent`;
```

#### Register Page ([`register/page.tsx`](frontend/app/(auth)/register/page.tsx:1))

Features:
- Full name, email, and password fields
- Minimum 8 character password requirement
- Automatic login after successful registration

### Dashboard Pages

#### Main Dashboard ([`dashboard/page.tsx`](frontend/app/(dashboard)/dashboard/page.tsx:1))

Displays:
- Channel overview stats (subscribers, avg views, content gaps, niche)
- Top 3 content gaps with opportunity scores and competition levels
- Top 3 trending topics with velocity scores
- Quick action cards (Generate Script, Analyze Competitors, Generate Hooks)

**State Management:**
```typescript
const { activeChannel, setActiveChannel } = useStore();
const [channels, setChannels] = useState<Channel[]>([]);
const [gaps, setGaps] = useState<ContentGap[]>([]);
const [trends, setTrends] = useState<Trend[]>([]);
```

**Empty State:** Shows "Connect your channel" prompt when no channels exist.

#### Channel Page ([`channel/page.tsx`](frontend/app/(dashboard)/channel/page.tsx:1))

Features:
- List of connected YouTube channels
- Channel connection via ID or @handle input
- Analysis status indicator (done/running/pending)
- Re-analyze trigger button
- Niche tags display

**Channel Connection:**
```typescript
async function handleConnect() {
  const resp = await channelsApi.connect(channelIdInput);
  setChannels([...channels, resp.data]);
  setActiveChannel(resp.data);
}
```

#### Script Generation ([`scripts/new/page.tsx`](frontend/app/(dashboard)/scripts/new/page.tsx:1))

Form fields:
- Topic description (textarea)
- Format type selection (educational, story, list, review, commentary)
- Target duration (5, 8, 10, 15, 20 minutes)

On submit:
1. Calls `scriptsApi.generate({ topic, channel_id, target_duration_minutes, format_type })`
2. Navigates to `/scripts/{response.data.id}` on success

#### Mobile Navigation ([`MobileNav.tsx`](frontend/app/(dashboard)/MobileNav.tsx:1))

Bottom navigation bar for mobile devices:
- 7 navigation items: Home, Gaps, Competitors, Scripts, Hooks, Trends, Settings
- Active state highlighting using `usePathname()`
- Fixed position at bottom of screen

## Global Styles ([`globals.css`](frontend/app/globals.css:1))

Tailwind CSS configuration with custom theming:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --background: #0f172a;
  --foreground: #ffffff;
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: 'Inter', system-ui, sans-serif;
}

@layer utilities {
  .text-gradient-brand {
    @apply bg-gradient-brand bg-clip-text text-transparent;
  }
}
```

## State Management

Uses Zustand store from [`store/useStore.ts`](frontend/store/useStore.ts):

```typescript
const { accessToken, setAccessToken, setUser, activeChannel, setActiveChannel } = useStore();
```

Auth token stored in both:
- Zustand store (memory)
- localStorage (persistence across page reloads)

## API Integration

All API calls go through [`lib/api.ts`](frontend/lib/api.ts) which provides typed endpoints:
- `authApi.login()`, `authApi.register()`, `authApi.me()`
- `channelsApi.list()`, `channelsApi.connect()`, `channelsApi.reanalyze()`
- `gapsApi.list()`, `gapsApi.detect()`
- `trendsApi.list()`
- `scriptsApi.generate()`

## Dependencies

```json
{
  "next": "14.1.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "zustand": "^4.4.0",
  "@tanstack/react-query": "^5.0.0",
  "lucide-react": "^0.300.0",
  "clsx": "^2.0.0"
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID |

## Error Handling

- Auth pages display error messages from API responses
- Dashboard pages use try/catch with minimal error UI (empty states)
- Loading states use skeleton screens with `animate-pulse`

## Styling Conventions

- Uses Tailwind CSS utility classes
- Color tokens: `surface`, `surface-card`, `surface-border`, `brand-*`, `accent-*`
- Dark theme background: `#0f172a`
- Card backgrounds: `bg-surface-card` with `border-surface-border`
- Brand primary: `bg-brand-600`, text `text-brand-400`