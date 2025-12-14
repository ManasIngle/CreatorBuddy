# Frontend Hooks Module

## Overview

The `frontend/hooks` directory contains custom React hooks that wrap TanStack Query (React Query) for data fetching, state management, and API interactions. These hooks provide a clean interface for components to access backend data with built-in caching, loading states, and error handling.

## File Structure

```
frontend/hooks/
├── useCompetitors.ts      # Competitor list and single competitor queries/mutations
├── useContentGaps.ts      # Content gap list and detection mutation
├── useCreatorProfile.ts   # Channel list and single channel queries
└── useScript.ts           # Script list, single script, generate, and delete operations
```

## TanStack Query Configuration

All hooks use consistent QueryClient configuration:
- `staleTime`: Time in ms before data is considered stale (varies by entity type)
- `gcTime`: Garbage collection time - how long unused data stays in cache (default: 5 min)
- `retry`: Number of times to retry failed requests (default: 2)
- `enabled`: Boolean to prevent query from running until condition is met
- `refetchOnWindowFocus`: Refetch when user returns to the tab (competitors only)

## Hooks API

### useCompetitors ([`useCompetitors.ts`](frontend/hooks/useCompetitors.ts:6))

**Purpose:** Fetch and manage competitor list for a channel.

```typescript
export function useCompetitors(channelId: string | undefined)
```

**Parameters:**
- `channelId: string | undefined` - The channel ID to fetch competitors for

**Returns:**
```typescript
{
  competitors: Competitor[];      // List of competitors (empty array if loading/error)
  isLoading: boolean;              // Initial loading state
  isFetching: boolean;             // Background refetching state
  error: Error | null;             // Error object if failed
  addCompetitor: UseMutationResult; // Mutation to add new competitor
}
```

**Query Configuration:**
```typescript
{
  staleTime: 10 * 60 * 1000,      // 10 minutes
  gcTime: 30 * 60 * 1000,         // 30 minutes
  refetchOnWindowFocus: true,
  retry: 2,
  enabled: !!channelId
}
```

**Usage Example:**
```typescript
const { competitors, isLoading, addCompetitor } = useCompetitors(channelId);

async function handleAddCompetitor(youtubeChannelId: string) {
  await addCompetitor.mutateAsync(youtubeChannelId);
}
```

### useCompetitor ([`useCompetitors.ts`](frontend/hooks/useCompetitors.ts:54))

**Purpose:** Fetch a single competitor's details.

```typescript
export function useCompetitor(channelId: string | undefined, competitorId: string | undefined)
```

**Parameters:**
- `channelId: string | undefined`
- `competitorId: string | undefined`

**Returns:** Standard useQuery result with `data` as `Competitor` object.

**Query Configuration:**
```typescript
{
  staleTime: 5 * 60 * 1000,       // 5 minutes - competitor data changes less
  gcTime: 15 * 60 * 1000,
  enabled: !!channelId && !!competitorId
}
```

### useRefreshCompetitors ([`useCompetitors.ts`](frontend/hooks/useCompetitors.ts:70))

**Purpose:** Manual refresh control for competitor data.

```typescript
export function useRefreshCompetitors(channelId: string | undefined)
```

**Returns:**
```typescript
{
  refresh: () => void;      // Invalidate specific channel's competitors
  refreshAll: () => void;    // Invalidate all competitor queries
}
```

**Usage:**
```typescript
const { refresh } = useRefreshCompetitors(channelId);

// After user action that changes competitor data
refresh();
```

---

### useContentGaps ([`useContentGaps.ts`](frontend/hooks/useContentGaps.ts:6))

**Purpose:** Fetch and detect content gaps for a channel.

```typescript
export function useContentGaps(channelId: string | undefined)
```

**Parameters:**
- `channelId: string | undefined`

**Returns:**
```typescript
{
  gaps: ContentGap[];               // List of detected gaps
  isLoading: boolean;
  error: Error | null;
  detectGaps: UseMutationResult;    // Mutation to trigger gap detection
}
```

**Query Configuration:**
```typescript
{
  staleTime: 15 * 60 * 1000,       // 15 minutes - gap analysis is expensive
  enabled: !!channelId
}
```

**Mutation onSuccess:**
- Invalidates `["gaps", channelId]` to refetch after detection completes

**Usage Example:**
```typescript
const { gaps, detectGaps } = useContentGaps(channelId);

// Trigger detection
await detectGaps.mutateAsync();
```

---

### useScripts ([`useScripts.ts`](frontend/hooks/useScripts.ts:6))

**Purpose:** Fetch all scripts for the current user.

```typescript
export function useScripts()
```

**Returns:**
```typescript
{
  scripts: Script[];
  isLoading: boolean;
  error: Error | null;
}
```

**Query Configuration:**
```typescript
{
  staleTime: 5 * 60 * 1000,  // 5 minutes
}
```

### useScript ([`useScripts.ts`](frontend/hooks/useScript.ts:25))

**Purpose:** Fetch a single script by ID.

```typescript
export function useScript(scriptId: string | undefined)
```

**Parameters:**
- `scriptId: string | undefined`

**Returns:** Standard useQuery result with `data` as `Script` object.

**Query Configuration:**
```typescript
{
  enabled: !!scriptId,
  staleTime: 5 * 60 * 1000,
}
```

### useGenerateScript ([`useScripts.ts`](frontend/hooks/useScript.ts:45))

**Purpose:** Generate a new script via mutation.

```typescript
interface GenerateScriptParams {
  topic: string;
  channel_id?: string;
  target_duration_minutes?: number;
  format_type?: string;
}

export function useGenerateScript()
```

**Returns:** Mutation result that resolves to generated `Script` object.

**Mutation onSuccess:**
- Invalidates `["scripts"]` query to refresh list

**Usage:**
```typescript
const generateScript = useGenerateScript();

const newScript = await generateScript.mutateAsync({
  topic: "How to grow your channel",
  channel_id: activeChannel?.id,
  target_duration_minutes: 10,
  format_type: "educational"
});
```

### useDeleteScript ([`useScripts.ts`](frontend/hooks/useScript.ts:59))

**Purpose:** Delete a script by ID.

```typescript
export function useDeleteScript()
```

**Returns:** Mutation result.

**Mutation onSuccess:**
- Invalidates `["scripts"]` query to refresh list

---

### useCreatorProfile ([`useCreatorProfile.ts`](frontend/hooks/useCreatorProfile.ts:14))

**Purpose:** Fetch all connected YouTube channels and manage active channel state.

```typescript
interface UseCreatorProfileResult {
  channels: Channel[];
  activeChannel: Channel | null;    // First channel or null if none
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;               // Manual refetch function
}

export function useCreatorProfile(): UseCreatorProfileResult
```

**Query Configuration:**
```typescript
{
  staleTime: 5 * 60 * 1000,  // 5 minutes
  retry: 2
}
```

**Returns Note:** `activeChannel` is derived from `data?.[0]`, not from the Zustand store. For store-based active channel, use `useStore().activeChannel` instead.

### useChannel ([`useCreatorProfile.ts`](frontend/hooks/useCreatorProfile.ts:34))

**Purpose:** Fetch a single channel by ID.

```typescript
export function useChannel(channelId: string | undefined)
```

**Parameters:**
- `channelId: string | undefined`

**Returns:** Standard useQuery result with `data` as `Channel` object.

**Query Configuration:**
```typescript
{
  enabled: !!channelId,
  staleTime: 5 * 60 * 1000,
}
```

## Data Types

All hooks import types from [`@/types`](frontend/types/index.ts):

```typescript
interface Competitor {
  id: string;
  youtube_channel_id: string;
  title: string;
  thumbnail_url?: string;
  subscriber_count: number;
  avg_views: number;
  niche_overlap_score: number;
  why_they_succeed?: string;
  best_formats?: string[];
}

interface ContentGap {
  id: string;
  topic: string;
  competition_level: "low" | "medium" | "high";
  opportunity_score: number;
  trend_direction: "rising" | "declining" | "stable";
  reason: string;
  suggested_angle?: string;
  suggested_title?: string;
}

interface Script {
  id: string;
  topic: string;
  channel_id: string;
  hook?: string;
  full_script?: string;
  title_suggestions?: string[];
  cta_text?: string;
  short_form_adaptation?: string;
  thumbnail_concept?: string;
  target_duration_minutes: number;
  format_type: string;
}

interface Channel {
  id: string;
  youtube_channel_id: string;
  title: string;
  thumbnail_url?: string;
  subscriber_count: number;
  video_count: number;
  avg_views: number;
  avg_engagement_rate: number;
  niche?: string;
  audience_type?: string;
  niche_tags?: string[];
  analysis_status: "pending" | "running" | "done";
}
```

## Dependencies

```json
{
  "react": "^18.2.0",
  "@tanstack/react-query": "^5.0.0"
}
```

## Usage Pattern

Components typically use hooks like this:

```typescript
import { useContentGaps } from "@/hooks/useContentGaps";
import { useStore } from "@/store/useStore";

export function GapsPage() {
  const { activeChannel } = useStore();
  const { gaps, isLoading, detectGaps } = useContentGaps(activeChannel?.id);

  if (isLoading) return <ContentGapCardSkeleton />;
  
  return (
    <div>
      {gaps.map(gap => <ContentGapCard key={gap.id} gap={gap} />)}
      <Button onClick={() => detectGaps.mutate()}>
        Detect New Gaps
      </Button>
    </div>
  );
}
```

## Query Key Conventions

Query keys follow a hierarchical pattern:
- `["channels"]` - All channels
- `["channel", channelId]` - Single channel
- `["competitors", channelId]` - Competitors for channel
- `["competitor", channelId, competitorId]` - Single competitor
- `["gaps", channelId]` - Gaps for channel
- `["scripts"]` - All scripts
- `["script", scriptId]` - Single script

## Cache Invalidation Strategy

Mutations use `queryClient.invalidateQueries` with specific query keys to ensure fresh data after mutations:
- `addCompetitor` → invalidates `["competitors", channelId]`
- `detectGaps` → invalidates `["gaps", channelId]`
- `useGenerateScript` → invalidates `["scripts"]`
- `useDeleteScript` → invalidates `["scripts"]`