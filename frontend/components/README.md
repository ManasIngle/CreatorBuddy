# Frontend Components Module

## Overview

The `frontend/components` directory contains all reusable React components for the CreatorIQ platform. Components are organized by functionality: layout components, UI primitives, chart components, and intelligence-specific display components.

## File Structure

```
frontend/components/
├── ErrorBoundary.tsx              # React class component error boundary
├── charts/                        # Data visualization components
│   ├── EngagementChart.tsx       # Engagement metrics line chart
│   ├── GrowthChart.tsx           # Subscriber/views growth area/line chart
│   ├── RetentionChart.tsx        # Audience retention curve chart
│   └── TrendChart.tsx            # Trend velocity visualization
├── intelligence/                  # Domain-specific intelligence display components
│   ├── AudienceInsightPanel.tsx   # Audience demographics and insights
│   ├── CompetitorCard.tsx        # Competitor summary with overlap score
│   ├── ContentGapCard.tsx        # Content gap opportunity display
│   ├── CreatorProfileCard.tsx    # YouTube creator profile display
│   ├── HookCard.tsx              # Viral hook card with type icons
│   ├── ScriptEditor.tsx          # Script display with copy functionality
│   ├── ThumbnailAnalysis.tsx      # Thumbnail AI analysis results
│   └── TrendRadar.tsx            # Trending topics radar visualization
├── layout/                       # App shell components
│   ├── Sidebar.tsx                # Desktop sidebar navigation
│   └── TopBar.tsx                # Header with channel selector and notifications
└── ui/                           # Primitive UI components
    ├── Avatar.tsx                # User/channel avatar with fallback
    ├── Badge.tsx                 # Status/category badge with variants
    ├── Button.tsx                # Button with CVA variants and loading state
    ├── Card.tsx                  # Card container with header/content parts
    ├── Input.tsx                 # Text input with dark theme styling
    ├── Modal.tsx                 # Dialog modal component
    ├── Progress.tsx             # Progress bar with percentage
    ├── Select.tsx                # Dropdown select component
    ├── Skeleton.tsx             # Loading skeleton placeholder
    ├── Tabs.tsx                 # Tab navigation component
    └── Tooltip.tsx              # Hover tooltip component
```

## Component Categories

### Layout Components

#### Sidebar ([`Sidebar.tsx`](frontend/components/layout/Sidebar.tsx:1))

Desktop navigation sidebar with:
- CreatorIQ branding header
- 8 navigation items with icons (Overview, My Channel, Competitors, Content Gaps, Scripts, Hooks, Thumbnails, Trends)
- Active route highlighting using `usePathname()`
- User profile section at bottom with avatar, name, plan type
- Settings and Sign out buttons
- Logout handler calling `useStore().logout()` and redirecting to `/login`

**State Dependencies:**
```typescript
const { user, logout } = useStore();
const pathname = usePathname();
```

**Navigation Items:**
```typescript
const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/channel", label: "My Channel", icon: Youtube },
  { href: "/competitors", label: "Competitors", icon: Users },
  { href: "/gaps", label: "Content Gaps", icon: Search },
  { href: "/scripts", label: "Scripts", icon: FileText },
  { href: "/hooks", label: "Hooks", icon: Zap },
  { href: "/thumbnails", label: "Thumbnails", icon: Image },
  { href: "/trends", label: "Trends", icon: TrendingUp },
];
```

#### TopBar ([`TopBar.tsx`](frontend/components/layout/TopBar.tsx:1))

Header bar with:
- Active channel display (thumbnail + title) on the left
- Search and notification buttons on the right
- Notification badge indicator (red dot)
- User avatar with initial fallback

**State Dependencies:**
```typescript
const { activeChannel, user } = useStore();
```

### UI Components

#### Button ([`Button.tsx`](frontend/components/ui/Button.tsx:1))

CVA (Class Variance Authority) based button with:
- 6 variants: `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`
- 4 sizes: `default`, `sm`, `lg`, `icon`
- Built-in loading spinner when `loading={true}`
- Focus visible ring with brand color

**Usage:**
```typescript
<Button variant="default" size="default" loading={isSubmitting}>
  Submit
</Button>
```

#### Card ([`Card.tsx`](frontend/components/ui/Card.tsx:1))

Card container with dark theme styling:
- Rounded corners (`rounded-xl`)
- Surface card background with border
- Sub-components: `CardHeader`, `CardTitle`, `CardContent`

**Usage:**
```typescript
<Card className="p-4">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>
```

#### Badge ([`Badge.tsx`](frontend/components/ui/Badge.tsx:1))

Status badge with color variants:
- `default` - brand purple (bg-brand-600/20)
- `success` / `green` - green (bg-accent-green/10)
- `warning` / `yellow` - yellow (bg-accent-yellow/10)
- `danger` / `red` - red (bg-accent-red/10)
- `purple` - purple (bg-accent-purple/10)
- `orange` - orange (bg-accent-orange/10)

**Usage:**
```typescript
<Badge variant="success">Completed</Badge>
<Badge variant="orange">{Math.round(score * 100)}%</Badge>
```

#### Avatar ([`Avatar.tsx`](frontend/components/ui/Avatar.tsx:1))

Image avatar with fallback to initial:
- 4 sizes: `sm` (32px), `md` (40px), `lg` (48px), `xl` (64px)
- Circular container with brand background
- Shows image if `src` provided, otherwise shows first letter of `fallback`

**Usage:**
```typescript
<Avatar src={channel.thumbnail_url} alt={channel.title} size="lg" />
<Avatar fallback={user.full_name} size="md" />
```

#### Input ([`Input.tsx`](frontend/components/ui/Input.tsx:1))

Text input with dark theme styling:
- Rounded corners with surface background
- Brand focus ring
- Placeholder text in gray-600
- Disabled state with reduced opacity

#### Select ([`Select.tsx`](frontend/components/ui/Select.tsx:1))

Dropdown select with same styling as Input:
- Accepts `options` array of `{ value, label }` objects
- White text on dark background

#### Skeleton ([`Skeleton.tsx`](frontend/components/ui/Skeleton.tsx:1))

Loading placeholder with pulse animation:
- `animate-pulse` class for shimmer effect
- Used for loading states in page components

### Intelligence Components

#### ScriptEditor ([`ScriptEditor.tsx`](frontend/components/intelligence/ScriptEditor.tsx:1))

Display component for generated scripts with:
- Title suggestions (copyable)
- Opening hook display (copyable)
- Full script with formatting (parses `[PAUSE]`, `[EMPHASIS]`, `[B-ROLL:]`)
- Call-to-action text
- Short form adaptation (60s version)
- Thumbnail concept
- Target duration and format type metadata

**Script Formatting:**
```typescript
const formatScript = (text: string) => {
  return text
    .replace(/\[PAUSE\]/g, '\n\n⏸️ [PAUSE]\n')
    .replace(/\[EMPHASIS\]/g, '**')
    .replace(/\[B-ROLL:([^\]]+)\]/g, '\n\n🎬 B-ROLL: $1\n')
    .split('\n\n')
    .map((para, i) => <p key={i}>{para}</p>);
};
```

**Export variants:**
- `ScriptEditor` - main display component
- `ScriptEditorSkeleton` - loading state
- `ScriptEditorEmpty` - empty state

#### CompetitorCard ([`CompetitorCard.tsx`](frontend/components/intelligence/CompetitorCard.tsx:1))

Competitor summary card showing:
- Avatar with thumbnail
- Title and niche overlap badge (color-coded by overlap %)
- Subscriber count and average views
- "Why they succeed" description (2 line clamp)
- Best formats as subtle badges
- Link to detailed analysis page

**Overlap Score Colors:**
- >= 70%: `accent-green` (high relevance)
- >= 40%: `accent-yellow` (medium relevance)
- < 40%: `accent-orange` (low relevance)

**Export variants:**
- `CompetitorCard` - main card
- `CompetitorCardSkeleton` - loading state
- `CompetitorCardEmpty` - empty state

#### ContentGapCard ([`ContentGapCard.tsx`](frontend/components/intelligence/ContentGapCard.tsx:1))

Content gap opportunity card showing:
- Topic with target icon
- Trend direction icon (rising/declining/minus) with color
- Competition level badge
- Reason description
- Suggested angle (if available)
- Opportunity score with color coding (green >= 7, yellow >= 5, orange < 5)
- "Title ready" badge if suggested_title exists

**Export variants:**
- `ContentGapCard` - main card
- `ContentGapCardSkeleton` - loading state
- `ContentGapCardEmpty` - empty state

#### HookCard ([`HookCard.tsx`](frontend/components/intelligence/HookCard.tsx:1))

Viral hook display card showing:
- Hook type icon with color (curiosity, shock, story, question, contrarian)
- Hook type badge and emotional trigger badge
- Hook text (3 line clamp)
- Predicted retention boost percentage (if available)

**Hook Type Icons/Colors:**
```typescript
const hookTypeIcons: Record<string, Icon> = {
  curiosity: Sparkles,    // text-accent-yellow
  shock: AlertTriangle,   // text-accent-red
  story: MessageCircle,   // text-accent-purple
  question: HelpCircle,   // text-accent-blue
  contrarian: Crossroads, // text-accent-orange
};
```

**Export variants:**
- `HookCard` - main card (clickable, passes onClick)
- `HookCardSkeleton` - loading state
- `HookCardEmpty` - empty state

### Chart Components

#### GrowthChart ([`GrowthChart.tsx`](frontend/components/charts/GrowthChart.tsx:1))

Line/area chart for subscriber and view growth:
- Uses `recharts` library (AreaChart, LineChart)
- Three modes: `subscribers`, `views`, or `all`
- Subscribers shown as area chart with gradient fill
- Views shown as line chart
- Combined shows both as lines
- Dark theme styling with custom tooltip
- Y-axis formatted with K/M suffixes

**Usage:**
```typescript
<GrowthChart data={growthData} metric="all" />
<GrowthChart data={subData} metric="subscribers" />
```

**Data format:**
```typescript
interface GrowthData {
  date: string;
  subscribers: number;
  views: number;
  videos: number;
}
```

### Error Handling

#### ErrorBoundary ([`ErrorBoundary.tsx`](frontend/components/ErrorBoundary.tsx:1))

React class component error boundary:
- Catches render errors and displays fallback UI
- `getDerivedStateFromError` sets `hasError: true`
- `componentDidCatch` logs to console (would send to Sentry in production)
- Shows error card with "Something went wrong" message
- Two action buttons: "Reload Page" and "Go to Dashboard"
- Development mode shows full error stack in expandable details
- Accepts optional `fallback` prop for custom error UI

**Props:**
```typescript
interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}
```

## Dependencies

```json
{
  "react": "^18.2.0",
  "recharts": "^2.10.0",
  "lucide-react": "^0.300.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.0.0"
}
```

## Styling Conventions

- Uses Tailwind CSS utility classes
- All components use dark theme colors (surface, surface-card, surface-border)
- Brand colors for primary actions (bg-brand-600, text-brand-400)
- Accent colors for status indicators (green, yellow, red, orange, purple)
- `transition` class for hover state animations
- `group` class for hover states on child elements

## Composition Pattern

Intelligence components follow a consistent pattern:
1. Main component with props interface
2. Skeleton component for loading states
3. Empty component for empty data states

This allows pages to show appropriate state based on data availability.