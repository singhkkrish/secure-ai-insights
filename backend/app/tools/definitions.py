"""
Tool definitions for Claude function/tool calling.
Each tool maps to a safe backend service — no raw data access.
"""

TOOLS = [
    {
        "name": "query_structured_data",
        "description": (
            "Execute a safe SELECT query against the StreamVault SQLite database. "
            "Available tables: movies (movie_id, title, genre, release_year, release_date, director, "
            "runtime_minutes, budget_usd, rating, status), "
            "viewers (viewer_id, age, gender, city, country, subscription_tier, segment, signup_date, is_active), "
            "watch_activity (activity_id, viewer_id, movie_id, watch_date, watch_month, completion_pct, device, platform), "
            "reviews (review_id, viewer_id, movie_id, rating, sentiment, review_date, helpful_votes), "
            "marketing_spend (movie_id, title, month, channel, spend_usd, impressions, clicks, conversions), "
            "regional_performance (city, month, genre, total_views, unique_viewers, avg_completion_pct, avg_rating, revenue_usd). "
            "Only SELECT queries allowed. Limit results to 50 rows unless aggregating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "A valid SELECT SQL query. Must start with SELECT.",
                }
            },
            "required": ["sql_query"],
        },
    },
    {
        "name": "search_documents",
        "description": (
            "Search internal PDF documents for relevant information. "
            "Documents include: Quarterly Executive Report, Campaign Performance Summary, "
            "Audience Behavior Report, Content Roadmap, Policy Guidelines. "
            "Use this to find qualitative insights, strategy details, explanations of trends, "
            "and leadership recommendations that are not in the structured data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query to find relevant document passages.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of document chunks to return (default 5, max 10).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_top_titles",
        "description": (
            "Get the top performing movie titles by total views, filtered by year and/or genre. "
            "Returns title name, genre, total views, avg rating, and completion rate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Filter by release year (e.g. 2025). Optional.",
                },
                "genre": {
                    "type": "string",
                    "description": "Filter by genre (e.g. Action, Sci-Fi, Drama). Optional.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of titles to return (default 10).",
                    "default": 10,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_trending_analysis",
        "description": (
            "Analyze trending titles by comparing recent view counts against historical baseline. "
            "Returns titles with their trend score, momentum, and recent activity data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Specific movie title to analyze. If omitted, returns top trending titles.",
                },
                "recent_months": {
                    "type": "integer",
                    "description": "Number of recent months to consider as 'recent' (default 2).",
                    "default": 2,
                },
            },
            "required": [],
        },
    },
    {
        "name": "compare_titles",
        "description": (
            "Compare two movie titles across key metrics: views, completion rate, ratings, "
            "marketing spend, audience demographics, and regional performance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title_a": {
                    "type": "string",
                    "description": "First movie title to compare.",
                },
                "title_b": {
                    "type": "string",
                    "description": "Second movie title to compare.",
                },
            },
            "required": ["title_a", "title_b"],
        },
    },
    {
        "name": "get_regional_engagement",
        "description": (
            "Get engagement metrics by city/region. Returns top cities by views, "
            "completion rates, revenue, and genre preferences per region."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "Month in YYYY-MM format (e.g. 2025-04). Optional — returns all months if omitted.",
                },
                "genre": {
                    "type": "string",
                    "description": "Filter by genre. Optional.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of cities to return (default 10).",
                    "default": 10,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_genre_performance",
        "description": (
            "Analyze performance metrics by genre over time. "
            "Returns views, completion rates, ratings, and month-over-month growth per genre."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "genre": {
                    "type": "string",
                    "description": "Specific genre to analyze. If omitted, returns all genres.",
                },
            },
            "required": [],
        },
    },
]
