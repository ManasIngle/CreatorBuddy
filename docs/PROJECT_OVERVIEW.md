# CreatorIQ - Project Overview

> AI-Powered YouTube Growth Intelligence Platform

---

## 1. Executive Summary

**CreatorIQ** is an intelligent platform that helps YouTube creators grow their channels by providing AI-powered competitor analysis, content opportunity detection, and script generation. Instead of guessing what content to create, creators use data-driven insights to produce videos that resonate with their target audience.

The platform connects to a creator's YouTube channel and analyzes hundreds of competitor channels to identify what content gaps exist and what topics will likely perform well. CreatorIQ then generates complete video scripts with hooks, editing notes, and calls-to-action—all tailored to the creator's specific niche and audience.

**Who is it for?** YouTube creators with 1,000 to 100,000 subscribers who want to accelerate their growth without spending hours on research. Content agencies and MCNs also use CreatorIQ to manage multiple channels with data-backed strategies.

**Core value proposition:** Stop guessing what to create. Know exactly what your audience wants, what competitors are missing, and get AI-generated scripts ready to film.

---

## 2. The Problem We Solve

Creating successful YouTube content is harder than it looks. Here's what creators struggle with every day:

### Content Creators Struggle to Grow on YouTube

Most creators produce content based on gut feeling or viral trends they stumbled upon. Without a systematic approach, growth is slow and inconsistent. They spend hours filming and editing videos that barely get traction, not because the content is bad, but because no one was looking for it.

### No Clear Data on What's Working for Competitors

Even when creators want to learn from competitors, they can only see surface-level metrics: view counts, like ratios, comment numbers. There's no way to understand *why* a competitor's video succeeded. What was the hook? What angle did they take? What emotional triggers did they use? This data simply isn't visible through YouTube's interface.

### Time-Consuming to Research Content Opportunities

Finding content gaps takes hours of manual work. Creators must watch dozens of competitor videos, read comments to understand what audiences want, track trending topics across multiple sources, and piece together a content strategy from fragments. By the time the research is done, the opportunity may have already passed.

### Script Writing is Tedious and Results Unpredictable

Writing a script from scratch is time-consuming, and even experienced writers struggle to create hooks that engage viewers in the first 30 seconds. The difference between a video that gets recommended and one that flops often comes down to execution details that most creators don't have time to perfect.

---

## 3. Solution Overview

CreatorIQ helps creators grow through intelligent automation and AI-powered insights:

| Capability | What It Does |
|------------|--------------|
| **AI Competitor Intelligence** | Analyzes why specific channels succeed and what content they haven't covered yet |
| **Data-Driven Content Gap Detection** | Identifies topics your audience wants but no one is creating |
| **AI Script Generation** | Creates complete, production-ready scripts with hooks, segments, and CTAs |
| **Viral Hook Identification** | Analyzes patterns from top-performing videos and generates hooks for your topic |
| **Real-Time Trend Monitoring** | Tracks emerging trends before they saturate the market |

The platform works in the background—connecting to YouTube, analyzing data, and surfacing actionable insights in a dashboard. Creators spend less time researching and more time creating.

---

## 4. Core Features

### Feature 1: Channel Connection & Analysis

**What it does:** Connects to a creator's YouTube channel and performs a comprehensive analysis of their content, audience, and competitive position.

**How it works:**
1. User authenticates via YouTube OAuth (secure, read-only access)
2. Background job fetches all channel videos, statistics, and available transcripts
3. AI analyzes the creator's content patterns to build a profile
4. Profile is displayed in the dashboard with actionable insights

**What data it uses:**
- Channel metadata (subscriber count, total views, upload frequency)
- Video list with performance metrics (views, likes, comments, watch time)
- Video transcripts and titles
- Content categories and upload schedule

**What output it produces:**
- Creator personality profile (tone, style, expertise areas)
- Audience demographics estimation
- Content strength and weakness analysis
- Speaking style and presentation patterns
- Optimal posting schedule recommendations

---

### Feature 2: Competitor Intelligence

**What it does:** Adds competitor channels and uses AI to analyze why they succeed, what gaps exist in their content, and what patterns drive their engagement.

**How it works:**
1. User adds competitors by entering their YouTube channel ID
2. System fetches competitor's video catalog, metrics, and thumbnails
3. AI analyzes the content to understand success factors
4. Insights are displayed in comparison cards showing strengths and opportunities

**What data it uses:**
- Competitor video catalog (titles, descriptions, view counts)
- Thumbnail designs and text overlays
- Content themes and topic coverage
- Upload frequency and consistency
- Engagement patterns (likes, comments, shares)

**What output it produces:**
- Competitor strength analysis (what they do well)
- Content gap identification (topics they've missed)
- Hook pattern recognition (what opening styles work)
- Thumbnail style analysis (design patterns that perform)
- Comparison dashboard showing your content vs. theirs

---

### Feature 3: Content Gap Detection

**What it does:** Identifies topics that your target audience is searching for but that competitors haven't adequately covered—these are high-opportunity content ideas with less competition.

**How it works:**
1. System analyzes your niche's top performers and their content coverage
2. Cross-references with audience demand signals from comments and searches
3. Identifies topics with high interest but low supply
4. Scores each gap by opportunity, competition level, and trend velocity
5. Presents ranked content ideas with suggested angles

**What data it uses:**
- Your channel's content themes and audience interests
- Competitor content coverage map (what they've done)
- Audience comments indicating unmet needs
- Search trend data and topic demand signals
- Niche saturation levels

**What output it produces:**
- Ranked list of content gaps with opportunity scores
- Suggested video titles and angles for each topic
- Competition difficulty rating (1-10)
- Trend trajectory indicator (rising, stable, declining)
- Estimated audience size for each topic

---

### Feature 4: AI Script Generator

**What it does:** Creates complete, production-ready video scripts based on a topic, target duration, format preference, and tone. Includes hook, main content segments, CTAs, and editing notes.

**How it works:**
1. User inputs topic, desired duration (5-30 minutes), format (tutorial, vlog, review), and tone (professional, casual, humorous)
2. System retrieves relevant context from your creator profile and competitor analysis
3. AI generates multiple title options with predicted CTR
4. Script is generated with timing markers, emotional triggers, and delivery notes
5. Short-form adaptation is provided for YouTube Shorts or TikTok

**What data it uses:**
- Target topic and keywords
- User's creator profile (speaking style, niche, audience)
- Competitor script patterns that performed well
- Viral hook database and retention optimization data
- Platform best practices (YouTube algorithm preferences)

**What output it produces:**
- 3 title options with CTR predictions
- Opening hook (first 30 seconds designed to retain viewers)
- Full script with speaker notes and timing
- Segment breakdown with key points per section
- B-roll suggestions and visual notes
- Mid-roll CTAs and end-screen recommendations
- Short-form version for vertical platforms
- Estimated production complexity (low/medium/high)

---

### Feature 5: Hook Intelligence

**What it does:** Analyzes the opening hooks from top-performing videos in your niche to identify patterns, then generates new hooks tailored to your topic that are designed to maximize viewer retention.

**How it works:**
1. System analyzes hooks from high-performing videos (high view-to-impression ratio)
2. Classifies hooks into patterns: curiosity gap, shock value, personal story, question, contrarian take, pattern interrupt
3. Identifies which hook types perform best in your specific niche
4. Generates multiple hook options for the user's topic
5. Scores each hook on predicted retention boost and click-through potential

**What data it uses:**
- Top 20% performing video hooks (by retention rate)
- Hook structure analysis (length, sentence patterns, word choices)
- Niche-specific hook performance data
- Viewer psychology triggers (fear of missing out, curiosity, validation)
- Platform algorithm preferences (retention signals)

**What output it produces:**
- Hook pattern classification and analysis
- Top performing hook templates for your niche
- 5+ generated hook options for your topic
- Predicted retention boost score per hook
- Click-through rate estimate
- Voice and tone recommendations for delivery

---

### Feature 6: Thumbnail Intelligence

**What it does:** Uses GPT-4o vision analysis to evaluate and recommend YouTube thumbnails based on predicted click-through rate, emotional impact, and clarity.

**How it works:**
1. User uploads a thumbnail image or provides a competitor thumbnail URL
2. Vision model analyzes the composition, text placement, facial expressions, color contrast, and emotional appeal
3. System cross-references with top-performing thumbnails in your niche
4. Provides specific improvement recommendations and generates alternative concepts

**What data it uses:**
- Thumbnail image (uploaded or from competitor)
- Top-performing thumbnails in the same niche
- CTR data from similar thumbnail styles
- Color psychology and contrast patterns
- Text overlay effectiveness data

**What output it produces:**
- CTR prediction score (1-10 scale)
- Emotional impact assessment
- Text clarity and readability score
- Composition analysis (face placement, focal point, visual hierarchy)
- Specific improvement recommendations
- Alternative thumbnail concepts based on competitor analysis
- A/B testing suggestions

---

### Feature 7: Trend Radar

**What it does:** Monitors web sources in real-time to detect emerging trends in your niche before they saturate, giving you an early-mover advantage on content opportunities.

**How it works:**
1. System continuously scrapes relevant sources (news, social media, forums, industry publications)
2. Identifies topics gaining momentum based on mention velocity
3. Scores trends by growth rate and saturation level
4. Alerts you when high-opportunity trends emerge
5. Predicts optimal timing for content creation

**What data it uses:**
- Web content from niche-relevant sources
- Social media mention velocity
- Search trend data
- News cycle monitoring
- Competitor content release timing

**What output it produces:**
- Real-time trend dashboard with trending topics
- Velocity score (how fast the trend is growing)
- Saturation indicator (how many creators are covering it)
- Opportunity window (time remaining before oversaturation)
- Related content ideas for each trend
- Optimal publish timing recommendations

---

### Feature 8: Audience Psychology

**What it does:** Extracts deep insights about your audience from comments and video data—understanding not just demographics, but the psychological drivers that make them engage and share content.

**How it works:**
1. System analyzes comments across your videos and competitor videos
2. Identifies recurring pain points, desires, frustrations, and aspirations
3. Builds audience persona profiles with psychological triggers
4. Maps behavioral patterns (when they watch, how they consume content, what triggers engagement)
5. Generates insights for content strategy and script personalization

**What data it uses:**
- Comment text from your videos and competitors' videos
- Comment sentiment and engagement patterns
- Viewer questions and feedback patterns
- Content that generates discussion vs. passive watching
- Audience demographic signals

**What output it produces:**
- Audience pain point summary (top frustrations and desires)
- Demographics profile (age range, interests, knowledge level)
- Psychological trigger map (what motivates engagement)
- Behavioral patterns (peak viewing times, content consumption style)
- Content personalization recommendations
- Messaging tone guidelines for maximum resonance

---

## 5. Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with App Router for fast, SEO-friendly pages |
| **TypeScript** | Type-safe code for better maintainability |
| **TailwindCSS** | Utility-first styling for consistent design system |
| **React Query** | Data fetching and caching for API calls |
| **Zustand** | Lightweight state management for UI state |
| **Recharts** | Data visualization for analytics dashboards |

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python API framework |
| **PostgreSQL + pgvector** | Database with vector embeddings for similarity search |
| **Redis** | Caching layer for fast data access |
| **Celery** | Background task processing for long-running jobs |

### AI & External Services

| Technology | Purpose |
|------------|---------|
| **OpenRouter** | Multi-model LLM gateway (access to GPT-4, Claude, Llama, etc.) |
| **Firecrawl** | Web scraping for trend monitoring and competitor research |
| **YouTube Data API v3** | Channel data, video metrics, and transcripts |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Vercel** | Frontend hosting and edge deployment |
| **Railway** | Backend hosting with easy scaling |
| **Docker** | Containerization for consistent environments |

---

## 6. Data Flow

The following diagram shows how data moves through the CreatorIQ system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER ACTIONS                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. AUTHENTICATION                                                           │
│     User connects YouTube channel via OAuth                                  │
│     System stores secure access token                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. DATA INGESTION (Background Jobs)                                         │
│     • Fetch all channel videos, stats, and transcripts                      │
│     • Store raw data in PostgreSQL                                          │
│     • Generate embeddings for semantic search                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. AI ANALYSIS                                                             │
│     • Creator profile analyzer extracts niche, audience, personality       │
│     • Competitor engine analyzes success patterns                            │
│     • Gap detector identifies unmet audience needs                          │
│     • Retention engine evaluates hook effectiveness                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. DASHBOARD PRESENTATION                                                   │
│     User views insights organized by feature:                                │
│     • Dashboard: Overview with key metrics                                   │
│     • Competitors: Comparison cards and gap analysis                         │
│     • Gaps: Ranked content opportunities                                    │
│     • Scripts: Generated scripts with editing notes                          │
│     • Trends: Real-time trend radar                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. ON-DEMAND ACTIONS                                                       │
│     User can trigger:                                                        │
│     • Add competitor channel → fetch and analyze                            │
│     • Generate script → input topic → AI script output                      │
│     • Analyze thumbnail → upload → vision analysis                          │
│     • Refresh trends → scrape sources → update dashboard                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. User Journey

Here's how a typical creator experiences CreatorIQ from signup to publishing a successful video:

### Step 1: Sign Up and Connect

A creator visits CreatorIQ and signs up with email or Google account. They click "Connect Your Channel" and grant YouTube read-only access via OAuth. The system immediately starts analyzing their channel in the background.

**Time: 2 minutes**

### Step 2: Wait for Initial Analysis

While the creator explores the interface, the system fetches all their videos, statistics, and available transcripts. AI analyzes their content style, audience, and competitive position. When complete, a notification alerts them that their creator profile is ready.

**Time: 5-15 minutes (depending on channel size)**

### Step 3: Review Creator Profile

The creator opens their dashboard and sees their profile card showing:
- Their content niche and focus areas
- Audience demographics and interests
- Content strengths and areas for improvement
- Recommended content directions

**Time: 5 minutes**

### Step 4: Add Competitors

The creator goes to the Competitors section and adds 3-5 channels they admire or compete with. The system fetches their content catalogs, analyzes success patterns, and displays comparison cards. The creator learns what these competitors do well and where they have gaps.

**Time: 10 minutes**

### Step 5: Discover Content Gaps

The creator navigates to Content Gaps and sees a ranked list of opportunities:
- "AI Video Editing in 2024: Complete Beginner's Guide" (Opportunity: 9/10)
- "Why Your Thumbnails Are Failing (And How to Fix)" (Opportunity: 8/10)
- "Behind the Scenes: How I Hit 100K Subscribers" (Opportunity: 7/10)

They pick one that fits their style and click "Generate Script."

**Time: 5 minutes**

### Step 6: Generate Script

The creator fills out a form:
- **Topic:** "AI Video Editing in 2024: Complete Beginner's Guide"
- **Duration:** 15 minutes
- **Format:** Tutorial
- **Tone:** Friendly and encouraging

The system generates a complete script including:
- 3 title options with CTR predictions
- A viral hook for the first 30 seconds
- Full script with timing markers
- B-roll suggestions and editing notes
- Short-form adaptation for YouTube Shorts

**Time: 2 minutes**

### Step 7: Polish and Film

The creator reviews the script, makes minor adjustments to match their voice, and films their video using the provided structure and notes. The hook and editing suggestions help them create content that retains viewers.

**Time: Variable (filming and editing)**

### Step 8: Analyze Results

After publishing, the creator returns to CreatorIQ to see how their video performed compared to predicted metrics. They can analyze engagement data, compare to competitor benchmarks, and use insights to improve their next video.

**Time: Ongoing**

---

## 8. Target Users

### Primary: YouTube Creators (1K-100K Subscribers)

**Profile:** Individual creators building their channel, often working part-time or as a side hustle. They have limited time for research and need high-impact guidance.

**Needs:**
- Clear content direction without hours of research
- Confidence that their next video will perform well
- Script help to speed up production
- Understanding of what their audience really wants

**Use cases:**
- "I don't know what to make next—give me data-backed ideas"
- "I want to beat my competitor on this topic—what angle should I take?"
- "I need a complete script fast so I can film this week"

### Secondary: Content Agencies

**Profile:** Small teams managing 5-20 YouTube channels for clients. They need efficient workflows and consistent results across multiple accounts.

**Needs:**
- Multi-channel dashboard for quick overview
- Scalable content strategy framework
- Client reporting with clear insights
- Template-based script generation

**Use cases:**
- "Manage all our clients' channels in one place"
- "Generate consistent content strategies for each niche"
- "Provide clients with weekly insight reports"

### Tertiary: MCNs (Multi-Channel Networks)

**Profile:** Larger organizations with hundreds of channels under management. They need platform-level intelligence and bulk operations.

**Needs:**
- Aggregated analytics across large channel portfolios
- Trend monitoring at scale
- Competitive intelligence across entire niches
- API access for custom integrations

**Use cases:**
- "Find emerging trends before they hit mainstream"
- "Benchmark all channels in our network against competitors"
- "Build custom dashboards for executive reporting"

---

## Getting Started

Ready to grow your YouTube channel with AI-powered intelligence?

1. **Sign up** at the CreatorIQ registration page
2. **Connect your YouTube channel** via the channel connection flow
3. **Add competitors** to build your analysis baseline
4. **Explore content gaps** and pick your next video topic
5. **Generate a script** and start filming

For technical documentation, see [docs/README.md](README.md).
For implementation details, see [IMPLEMENTATION.md](../IMPLEMENTATION.md).