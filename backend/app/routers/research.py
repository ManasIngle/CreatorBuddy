"""
Research Router for Deep Intelligence Gathering
Provides endpoints for comprehensive topic, competitor, and audience research
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.services.scraper_service import scraper_service
from app.services.openrouter_service import call_openai, safe_json_loads

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


class TopicResearchRequest(BaseModel):
    topic: str
    niche: str
    depth: Optional[str] = "standard"  # quick, standard, deep


class CompetitorResearchRequest(BaseModel):
    competitor_name: str
    competitor_url: Optional[str] = None
    include_social: Optional[bool] = True


class TrendResearchRequest(BaseModel):
    niche: str
    time_range: Optional[str] = "week"  # day, week, month
    sources: Optional[List[str]] = None


class AudienceResearchRequest(BaseModel):
    topic: str
    include_forums: Optional[bool] = True
    include_reddit: Optional[bool] = True
    include_quora: Optional[bool] = True


class DeepResearchRequest(BaseModel):
    topic: str
    niche: str
    sources_count: Optional[int] = 10


@router.post("/topic")
async def research_topic(request: TopicResearchRequest):
    """
    Deep research on a topic from multiple web sources.
    Aggregates data from various sources and synthesizes insights.
    """
    try:
        # Scrape multiple sources for the topic
        scraped_data = await scraper_service.multi_source_research(
            topic=request.topic,
            niche=request.niche
        )
        
        # Use AI to synthesize insights from scraped data
        synthesis_prompt = f"""
        Analyze the following scraped data about '{request.topic}' in the '{request.niche}' niche.
        
        Scraped Sources:
        {str(scraped_data.get('sources', []))[:5000]}
        
        Provide:
        1. Key insights about this topic
        2. Content opportunities
        3. Audience pain points
        4. Unique angles to explore
        
        Format your response as a structured analysis.
        """
        
        synthesis = call_openai(
            system_prompt="You are an expert content strategist analyzing research data.",
            user_prompt=synthesis_prompt,
            max_tokens=1000,
            complexity="medium"
        )
        
        return {
            "topic": request.topic,
            "niche": request.niche,
            "scraped_data": scraped_data,
            "ai_synthesis": synthesis,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Topic research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.post("/competitor")
async def research_competitor(request: CompetitorResearchRequest):
    """
    Research competitor across the web.
    Gathers data about competitor's content, strategy, and audience.
    """
    try:
        competitor_data = {
            "name": request.competitor_name,
            "url": request.competitor_url,
            "social_profiles": {},
            "content_strategy": {},
            "scraped_at": None,
            "success": False
        }
        
        # Scrape competitor website if URL provided
        if request.competitor_url:
            website_data = await scraper_service.scrape_channel_research(request.competitor_url)
            competitor_data["website_data"] = website_data
        
        # Scrape social proof and mentions
        social_proof = await scraper_service.scrape_social_proof(request.competitor_name)
        competitor_data["social_proof"] = social_proof
        
        # Scrape SEO data for competitor brand terms
        seo_data = await scraper_service.scrape_seo_data(request.competitor_name)
        competitor_data["seo_data"] = seo_data
        
        # Use AI to analyze competitor strategy
        analysis_prompt = f"""
        Analyze the following competitor data for '{request.competitor_name}':
        
        Website Data: {str(competitor_data.get('website_data', {}))[:2000]}
        Social Proof: {str(social_proof)[:2000]}
        SEO Data: {str(seo_data)[:2000]}
        
        Provide:
        1. Content strategy observations
        2. Audience engagement patterns
        3. Strengths to learn from
        4. Potential gaps to exploit
        """
        
        analysis = call_openai(
            system_prompt="You are a competitor analysis expert.",
            user_prompt=analysis_prompt,
            max_tokens=1000,
            complexity="medium"
        )
        
        competitor_data["ai_analysis"] = analysis
        competitor_data["success"] = True
        
        return competitor_data
    except Exception as e:
        logger.error(f"Competitor research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.post("/trends")
async def research_trends(request: TrendResearchRequest):
    """
    Aggregate trend data from multiple sources.
    """
    try:
        trends_data = {
            "niche": request.niche,
            "time_range": request.time_range,
            "trends": [],
            "scraped_at": None,
            "success": False
        }
        
        # Scrape trends from multiple sources
        trend_sources = []
        
        # Reddit trends
        reddit_trends = await scraper_service.scrape_reddit_trends(
            request.niche.replace(" ", ""),
            limit=25
        )
        trend_sources.extend(reddit_trends)
        
        # General trend aggregation
        general_trends = await scraper_service.scrape_trend_aggregator(request.niche)
        trend_sources.extend(general_trends)
        
        # Scrape forums for emerging discussions
        forum_discussions = await scraper_service.scrape_forum_discussions(request.niche)
        trend_sources.extend(forum_discussions)
        
        trends_data["trends"] = trend_sources
        trends_data["success"] = True
        
        # AI synthesis of trends
        synthesis_prompt = f"""
        Analyze these trends in the '{request.niche}' niche:
        
        {str(trend_sources)[:5000]}
        
        Identify:
        1. Top trending topics
        2. Emerging themes
        3. Content opportunities
        4. Timing recommendations
        """
        
        synthesis = call_openai(
            system_prompt="You are a trend analysis expert.",
            user_prompt=synthesis_prompt,
            max_tokens=1000,
            complexity="medium"
        )
        
        trends_data["ai_synthesis"] = synthesis
        
        return trends_data
    except Exception as e:
        logger.error(f"Trend research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.post("/audience")
async def research_audience(request: AudienceResearchRequest):
    """
    Research audience questions and pain points.
    Gathers data from forums, Reddit, Quora, and other discussion platforms.
    """
    try:
        audience_data = {
            "topic": request.topic,
            "questions": [],
            "pain_points": [],
            "discussions": [],
            "scraped_at": None,
            "success": False
        }
        
        # Scrape audience discourse from multiple sources
        discourse = await scraper_service.scrape_audience_discourse(request.topic)
        audience_data.update(discourse)
        
        # Scrape Reddit for audience insights
        if request.include_reddit:
            reddit_data = await scraper_service.scrape_reddit_trends(
                request.topic.replace(" ", ""),
                limit=25
            )
            audience_data["reddit_insights"] = reddit_data
        
        # Scrape forum discussions
        if request.include_forums:
            forum_data = await scraper_service.scrape_forum_discussions(request.topic)
            audience_data["forum_insights"] = forum_data
        
        # AI analysis of audience
        analysis_prompt = f"""
        Analyze this audience research for '{request.topic}':
        
        Questions: {str(discourse.get('questions', []))[:2000]}
        Discussions: {str(discourse.get('discussions', []))[:3000]}
        
        Provide:
        1. Most common questions
        2. Primary pain points
        3. Unmet needs
        4. Content angles that would resonate
        """
        
        analysis = call_openai(
            system_prompt="You are an audience research expert.",
            user_prompt=analysis_prompt,
            max_tokens=1000,
            complexity="medium"
        )
        
        audience_data["ai_analysis"] = analysis
        audience_data["success"] = True
        
        return audience_data
    except Exception as e:
        logger.error(f"Audience research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.post("/deep-research")
async def deep_research(request: DeepResearchRequest):
    """
    Comprehensive deep research on a topic.
    Scrapes 10+ sources and uses AI to synthesize insights.
    Returns a comprehensive briefing.
    """
    try:
        briefing = {
            "topic": request.topic,
            "niche": request.niche,
            "sources_count": request.sources_count,
            "findings": {
                "trends": [],
                "content_ideas": [],
                "audience_insights": [],
                "competitor_intel": [],
                "seo_data": []
            },
            "comprehensive_briefing": None,
            "scraped_at": None,
            "success": False
        }
        
        # Multi-source research
        research_data = await scraper_service.multi_source_research(
            topic=request.topic,
            niche=request.niche
        )
        briefing["findings"].update(research_data)
        
        # Scrape additional sources for depth
        content_ideas = await scraper_service.scrape_content_ideas(request.niche)
        briefing["findings"]["content_ideas"] = content_ideas
        
        audience_insights = await scraper_service.scrape_audience_discourse(request.topic)
        briefing["findings"]["audience_insights"] = audience_insights
        
        seo_data = await scraper_service.scrape_seo_data(request.topic)
        briefing["findings"]["seo_data"] = seo_data
        
        # Comprehensive AI briefing
        briefing_prompt = f"""
        Create a comprehensive research briefing for '{request.topic}' in the '{request.niche}' niche.
        
        Research Data:
        - Trends: {str(research_data.get('sources', []))[:2000]}
        - Content Ideas: {str(content_ideas)[:2000]}
        - Audience Insights: {str(audience_insights)[:2000]}
        - SEO Data: {str(seo_data)[:2000]}
        
        Format your response as a comprehensive briefing with:
        1. Executive Summary
        2. Key Trends
        3. Content Opportunities
        4. Audience Analysis
        5. SEO Opportunities
        6. Strategic Recommendations
        7. Content Ideas
        """
        
        briefing_text = call_openai(
            system_prompt="You are an expert content strategist and research analyst.",
            user_prompt=briefing_prompt,
            max_tokens=2000,
            complexity="complex"  # Deep research warrants premium model
        )
        
        briefing["comprehensive_briefing"] = briefing_text
        briefing["success"] = True
        
        return briefing
    except Exception as e:
        logger.error(f"Deep research failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.get("/sources")
async def list_sources():
    """
    List available scraping sources and their status.
    """
    return {
        "sources": [
            {"name": "Reddit", "status": "active", "types": ["trends", "discussions"]},
            {"name": "Quora", "status": "active", "types": ["questions", "topics"]},
            {"name": "Google", "status": "active", "types": ["search", "trends", "seo"]},
            {"name": "Wikipedia", "status": "active", "types": ["topics", "concepts"]},
            {"name": "YouTube", "status": "active", "types": ["channels", "content"]},
            {"name": "News", "status": "active", "types": ["trends", "breaking"]},
        ],
        "firecrawl_active": scraper_service.firecrawl is not None
    }