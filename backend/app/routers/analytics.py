"""
Analytics router — serves pre-built chart data and aggregations.
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from app.database import execute_safe_query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/top-titles")
async def get_top_titles(limit: int = Query(default=10, le=50), year: int = Query(default=None)):
    """Top titles by total views."""
    where = f"WHERE m.release_year = {year}" if year else ""
    query = f"""
        SELECT m.title, m.genre, m.release_year, m.rating,
            COUNT(wa.activity_id) AS total_views,
            ROUND(AVG(wa.completion_pct), 1) AS avg_completion_pct,
            COUNT(DISTINCT wa.viewer_id) AS unique_viewers
        FROM movies m LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
        {where}
        GROUP BY m.movie_id ORDER BY total_views DESC LIMIT {limit}
    """
    try:
        return {"data": execute_safe_query(query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genre-trends")
async def get_genre_trends():
    """Views by genre per month for trend charts."""
    query = """
        SELECT rp.genre, rp.month,
            SUM(rp.total_views) AS total_views,
            ROUND(AVG(rp.avg_completion_pct), 1) AS avg_completion_pct,
            ROUND(AVG(rp.avg_rating), 1) AS avg_rating,
            SUM(rp.revenue_usd) AS revenue_usd
        FROM regional_performance rp
        GROUP BY rp.genre, rp.month ORDER BY rp.month, rp.genre
    """
    try:
        return {"data": execute_safe_query(query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-heatmap")
async def get_regional_heatmap(month: str = Query(default=None)):
    """Engagement by city for map/heatmap visualization."""
    where = f"WHERE month = '{month}'" if month else ""
    query = f"""
        SELECT city,
            SUM(total_views) AS total_views,
            SUM(unique_viewers) AS unique_viewers,
            ROUND(AVG(avg_completion_pct), 1) AS avg_completion_pct,
            SUM(revenue_usd) AS revenue_usd
        FROM regional_performance {where}
        GROUP BY city ORDER BY total_views DESC
    """
    try:
        return {"data": execute_safe_query(query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketing-efficiency")
async def get_marketing_efficiency():
    """Marketing spend vs views efficiency."""
    query = """
        SELECT ms.title, ms.month,
            SUM(ms.spend_usd) AS total_spend,
            SUM(ms.impressions) AS total_impressions,
            SUM(ms.conversions) AS total_conversions,
            ROUND(CAST(SUM(ms.conversions) AS FLOAT) / NULLIF(SUM(ms.spend_usd), 0) * 1000, 2) AS conversions_per_1k_spend
        FROM marketing_spend ms
        GROUP BY ms.title, ms.month
        ORDER BY ms.month, total_spend DESC
    """
    try:
        return {"data": execute_safe_query(query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audience-segments")
async def get_audience_segments():
    """Viewer distribution by segment."""
    query = """
        SELECT v.segment,
            COUNT(v.viewer_id) AS viewer_count,
            ROUND(AVG(v.age), 1) AS avg_age,
            COUNT(wa.activity_id) AS total_watches,
            ROUND(AVG(wa.completion_pct), 1) AS avg_completion_pct
        FROM viewers v
        LEFT JOIN watch_activity wa ON v.viewer_id = wa.viewer_id
        GROUP BY v.segment ORDER BY viewer_count DESC
    """
    try:
        return {"data": execute_safe_query(query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview-stats")
async def get_overview_stats():
    """High-level KPI stats for the dashboard."""
    try:
        movies = execute_safe_query("SELECT COUNT(*) as count FROM movies")[0]["count"]
        viewers = execute_safe_query("SELECT COUNT(*) as count FROM viewers WHERE is_active = 1")[0]["count"]
        views = execute_safe_query("SELECT COUNT(*) as count FROM watch_activity")[0]["count"]
        avg_rating = execute_safe_query("SELECT ROUND(AVG(rating), 1) as avg FROM movies")[0]["avg"]
        top_genre = execute_safe_query("""
            SELECT m.genre, COUNT(wa.activity_id) as views
            FROM movies m JOIN watch_activity wa ON m.movie_id = wa.movie_id
            GROUP BY m.genre ORDER BY views DESC LIMIT 1
        """)[0]["genre"]
        return {
            "total_titles": movies,
            "active_viewers": viewers,
            "total_views": views,
            "avg_content_rating": avg_rating,
            "top_genre": top_genre,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
