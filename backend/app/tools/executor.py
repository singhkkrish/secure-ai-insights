"""
Tool executor — maps tool calls to safe backend implementations.
All data access flows through controlled, validated functions only.
"""
import logging
from typing import Any, Dict

from app.database import execute_safe_query
from app.services.pdf_service import search_documents as pdf_search

logger = logging.getLogger(__name__)


def execute_tool(tool_name: str, tool_input: Dict) -> Any:
    handlers = {
        "query_structured_data": handle_query_structured_data,
        "search_documents": handle_search_documents,
        "get_top_titles": handle_get_top_titles,
        "get_trending_analysis": handle_get_trending_analysis,
        "compare_titles": handle_compare_titles,
        "get_regional_engagement": handle_get_regional_engagement,
        "get_genre_performance": handle_get_genre_performance,
    }
    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handler(**tool_input)
    except Exception as e:
        logger.error(f"Tool '{tool_name}' failed: {e}")
        return {"error": str(e)}


def handle_query_structured_data(sql_query: str, **kwargs) -> Any:
    """Execute a safe SELECT query."""
    return execute_safe_query(sql_query)


def handle_search_documents(query: str, top_k: int = 5, **kwargs) -> Any:
    """Search PDF documents. top_k is optional."""
    try:
        top_k = min(int(top_k), 10)
    except (TypeError, ValueError):
        top_k = 5
    results = pdf_search(query, top_k=top_k)
    return {
        "query": query,
        "results_count": len(results),
        "results": [{"source": r["source"], "content": r["content"][:600], "relevance_score": r["relevance_score"]} for r in results],
    }


def handle_get_top_titles(year: int = None, genre: str = None, limit: int = 10, **kwargs) -> Any:
    limit = min(int(limit) if limit else 10, 50)
    where_clauses = []
    if year:
        where_clauses.append(f"m.release_year = {int(year)}")
    if genre:
        safe_genre = str(genre).replace("'", "")
        where_clauses.append(f"m.genre = '{safe_genre}'")
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = f"""
        SELECT m.title, m.genre, m.release_year, m.rating AS imdb_rating, m.status,
            COUNT(wa.activity_id) AS total_views,
            ROUND(AVG(wa.completion_pct), 1) AS avg_completion_pct,
            COUNT(DISTINCT wa.viewer_id) AS unique_viewers
        FROM movies m
        LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
        {where_sql}
        GROUP BY m.movie_id, m.title, m.genre, m.release_year, m.rating, m.status
        ORDER BY total_views DESC LIMIT {limit}
    """
    return execute_safe_query(query)


def handle_get_trending_analysis(title: str = None, recent_months: int = 2, **kwargs) -> Any:
    where_title = ""
    if title:
        safe_title = str(title).replace("'", "")
        where_title = f"AND m.title LIKE '%{safe_title}%'"
    query = f"""
        SELECT m.title, m.genre,
            COUNT(CASE WHEN wa.watch_month >= '2025-04' THEN 1 END) AS recent_views,
            COUNT(CASE WHEN wa.watch_month < '2025-04' THEN 1 END) AS historical_views,
            COUNT(wa.activity_id) AS total_views,
            ROUND(AVG(CASE WHEN wa.watch_month >= '2025-04' THEN wa.completion_pct END), 1) AS recent_completion_pct,
            ROUND(AVG(wa.completion_pct), 1) AS overall_completion_pct
        FROM movies m
        LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
        WHERE 1=1 {where_title}
        GROUP BY m.movie_id, m.title, m.genre
        HAVING total_views > 0
        ORDER BY recent_views DESC LIMIT 15
    """
    results = execute_safe_query(query)
    for r in results:
        hist = r.get("historical_views") or 1
        rec = r.get("recent_views") or 0
        r["trend_score"] = round(rec / hist, 2)
        r["trend_label"] = "Hot" if r["trend_score"] > 1.5 else ("Rising" if r["trend_score"] > 0.8 else "Declining")
    return sorted(results, key=lambda x: x["trend_score"], reverse=True)


def handle_compare_titles(title_a: str, title_b: str, **kwargs) -> Any:
    safe_a = str(title_a).replace("'", "")
    safe_b = str(title_b).replace("'", "")
    query = f"""
        SELECT m.title, m.genre, m.release_year, m.budget_usd, m.rating AS imdb_rating, m.status,
            COUNT(wa.activity_id) AS total_views,
            COUNT(DISTINCT wa.viewer_id) AS unique_viewers,
            ROUND(AVG(wa.completion_pct), 1) AS avg_completion_pct,
            ROUND(AVG(r.rating), 1) AS avg_user_rating,
            COUNT(r.review_id) AS review_count,
            SUM(ms.spend_usd) AS total_marketing_spend
        FROM movies m
        LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
        LEFT JOIN reviews r ON m.movie_id = r.movie_id
        LEFT JOIN marketing_spend ms ON m.movie_id = ms.movie_id
        WHERE m.title LIKE '%{safe_a}%' OR m.title LIKE '%{safe_b}%'
        GROUP BY m.movie_id, m.title, m.genre, m.release_year, m.budget_usd, m.rating, m.status
    """
    results = execute_safe_query(query)
    demo_query = f"""
        SELECT m.title, ROUND(AVG(v.age), 1) AS avg_viewer_age,
            COUNT(CASE WHEN v.gender = 'M' THEN 1 END) AS male_viewers,
            COUNT(CASE WHEN v.gender = 'F' THEN 1 END) AS female_viewers,
            COUNT(CASE WHEN v.subscription_tier = 'Premium' THEN 1 END) AS premium_viewers
        FROM movies m
        JOIN watch_activity wa ON m.movie_id = wa.movie_id
        JOIN viewers v ON wa.viewer_id = v.viewer_id
        WHERE m.title LIKE '%{safe_a}%' OR m.title LIKE '%{safe_b}%'
        GROUP BY m.movie_id, m.title
    """
    demo = execute_safe_query(demo_query)
    return {"comparison": results, "demographics": demo}


def handle_get_regional_engagement(month: str = None, genre: str = None, limit: int = 10, **kwargs) -> Any:
    limit = min(int(limit) if limit else 10, 50)
    where_clauses = []
    if month:
        safe_month = str(month).replace("'", "")
        where_clauses.append(f"month = '{safe_month}'")
    if genre:
        safe_genre = str(genre).replace("'", "")
        where_clauses.append(f"genre = '{safe_genre}'")
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = f"""
        SELECT city,
            SUM(total_views) AS total_views,
            SUM(unique_viewers) AS unique_viewers,
            ROUND(AVG(avg_completion_pct), 1) AS avg_completion_pct,
            ROUND(AVG(avg_rating), 1) AS avg_rating,
            SUM(revenue_usd) AS total_revenue
        FROM regional_performance {where_sql}
        GROUP BY city ORDER BY total_views DESC LIMIT {limit}
    """
    return execute_safe_query(query)


def handle_get_genre_performance(genre: str = None, **kwargs) -> Any:
    where_sql = f"WHERE rp.genre = '{str(genre).replace(chr(39), '')}'" if genre else ""
    query = f"""
        SELECT rp.genre, rp.month,
            SUM(rp.total_views) AS total_views,
            SUM(rp.unique_viewers) AS unique_viewers,
            ROUND(AVG(rp.avg_completion_pct), 1) AS avg_completion_pct,
            ROUND(AVG(rp.avg_rating), 1) AS avg_rating,
            SUM(rp.revenue_usd) AS revenue_usd
        FROM regional_performance rp {where_sql}
        GROUP BY rp.genre, rp.month ORDER BY rp.genre, rp.month
    """
    return execute_safe_query(query)
