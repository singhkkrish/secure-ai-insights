import json
import re
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from app.config import settings
from app.tools.executor import execute_tool

logger = logging.getLogger(__name__)
_client = None


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# ── Routing prompt — asks model to output plain JSON (no function calling) ──
ROUTING_PROMPT = """You are a tool router. Given a user question, decide which tool to call and output ONLY valid JSON.

Available tools:
- get_top_titles       → best/top performing movies (no args needed)
- get_trending_analysis → trending titles {"title": "movie name"} or {}
- compare_titles        → compare two movies {"title_a": "name1", "title_b": "name2"}
- get_regional_engagement → city/regional performance (no args needed)
- get_genre_performance  → genre trends {"genre": "name"} or {}
- search_documents      → strategy, recommendations, qualitative insights {"query": "search terms"}
- query_structured_data → specific data questions {"sql_query": "SELECT ..."}

Database columns ONLY (never use others):
movies: movie_id, title, genre, release_year, release_date, director, runtime_minutes, budget_usd, rating, status
viewers: viewer_id, age, gender, city, country, subscription_tier, segment, signup_date, is_active
watch_activity: activity_id, viewer_id, movie_id, watch_date, watch_month, completion_pct, device, platform
reviews: review_id, viewer_id, movie_id, rating, sentiment, review_date, helpful_votes
marketing_spend: movie_id, title, month, channel, spend_usd, impressions, clicks, conversions
regional_performance: city, month, genre, total_views, unique_viewers, avg_completion_pct, avg_rating, revenue_usd

Examples:
"Which titles performed best?" → {"tool": "get_top_titles", "args": {}}
"Why is Stellar Run trending?" → {"tool": "get_trending_analysis", "args": {"title": "Stellar Run"}}
"Compare Dark Orbit vs Last Kingdom" → {"tool": "compare_titles", "args": {"title_a": "Dark Orbit", "title_b": "Last Kingdom"}}
"Which city had most engagement?" → {"tool": "get_regional_engagement", "args": {}}
"What explains comedy weakness?" → {"tool": "search_documents", "args": {"query": "comedy performance analysis"}}
"Recommendations for leadership?" → {"tool": "search_documents", "args": {"query": "leadership recommendations strategy"}}
"Genre trends this year?" → {"tool": "get_genre_performance", "args": {}}
"How many premium subscribers?" → {"tool": "query_structured_data", "args": {"sql_query": "SELECT COUNT(*) as count FROM viewers WHERE subscription_tier = 'Premium'"}}

Respond with ONLY the JSON object, no explanation, no markdown, no extra text."""


# ── Answer prompt — given data, write the final response ──
ANSWER_PROMPT = """You are StreamVault Entertainment's internal analytics assistant.
You have retrieved real data to answer the user's question.
Write a clear, helpful, well-structured answer.
Include key numbers, cite the data source, and give useful business insight.
Be concise but thorough."""


def _call_llm_plain(messages: List[Dict], temperature: float = 0.0) -> str:
    """Call LLM without any tools — returns raw text content."""
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2048,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def _route_to_tool(user_question: str, conversation_history: List[Dict]) -> Optional[Dict]:
    """
    Ask the LLM which tool to call — returns {"tool": "...", "args": {...}}
    Uses plain JSON output instead of function calling to avoid Groq 400 errors.
    """
    # Build context from recent history
    context = ""
    if conversation_history:
        recent = conversation_history[-4:]
        context = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent])
        context = f"\nRecent conversation:\n{context}\n"

    messages = [
        {"role": "system", "content": ROUTING_PROMPT},
        {"role": "user", "content": f"{context}User question: {user_question}"}
    ]

    try:
        raw = _call_llm_plain(messages, temperature=0.0)
        logger.info(f"Router raw output: {raw}")

        # Clean up response — extract JSON even if model adds extra text
        raw = raw.strip()

        # Try direct parse first
        try:
            parsed = json.loads(raw)
            return parsed
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from response
        match = re.search(r'\{[^{}]*"tool"[^{}]*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            return parsed

        logger.error(f"Could not parse router output: {raw}")
        return None

    except Exception as e:
        logger.error(f"Router call failed: {e}")
        return None


def _sanitize_args(args: Any) -> Dict:
    """Ensure args is always a clean dict with correct types."""
    if args is None or not isinstance(args, dict):
        return {}

    clean = {}
    for k, v in args.items():
        if v is None:
            continue
        # Coerce numeric fields
        if k in ["limit", "top_k", "recent_months"]:
            try:
                clean[k] = int(v)
            except (ValueError, TypeError):
                pass  # Skip invalid numeric fields
        else:
            clean[k] = v

    return clean


def run_chat(messages: List[Dict], conversation_history: List[Dict] = None) -> Dict:
    tool_trace = []
    history = list(conversation_history or [])

    # Get the latest user message
    user_message = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_message = m.get("content", "")
            break

    if not user_message:
        return {"answer": "No message received.", "tool_trace": [], "model": "llama-3.3-70b"}

    # ── Step 1: Route to the right tool ───────────────────────────────
    logger.info(f"Routing question: {user_message}")
    route = _route_to_tool(user_message, history)

    tool_result = None
    tool_name = None

    if route and "tool" in route:
        tool_name = route.get("tool", "")
        raw_args = route.get("args", {})
        args = _sanitize_args(raw_args)

        logger.info(f"Routing to tool: {tool_name}({args})")

        # ── Step 2: Execute the tool ───────────────────────────────────
        try:
            tool_result = execute_tool(tool_name, args)
            tool_trace.append({
                "tool": tool_name,
                "input": args,
                "result_preview": _summarize_result(tool_result),
            })
            logger.info(f"Tool result: {_summarize_result(tool_result)}")
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            tool_result = {"error": str(e)}
            tool_trace.append({
                "tool": tool_name,
                "input": args,
                "result_preview": f"Error: {str(e)}",
            })
    else:
        logger.warning("Router returned no tool — answering directly")

    # ── Step 3: Generate final answer ─────────────────────────────────
    answer_messages = [{"role": "system", "content": ANSWER_PROMPT}]

    # Add conversation history for context
    if history:
        answer_messages += history[-4:]

    # Add the user question
    if tool_result is not None:
        result_str = json.dumps(tool_result, default=str)[:4000]
        answer_messages.append({
            "role": "user",
            "content": (
                f"Question: {user_message}\n\n"
                f"Data retrieved from '{tool_name}':\n{result_str}\n\n"
                f"Please write a clear, insightful answer based on this data."
            )
        })
    else:
        # No tool needed — answer from general knowledge about the system
        answer_messages.append({
            "role": "user",
            "content": user_message
        })

    try:
        answer = _call_llm_plain(answer_messages, temperature=0.1)
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        answer = f"I retrieved the data successfully but encountered an error generating the summary: {str(e)}"

    return {
        "answer": answer,
        "tool_trace": tool_trace,
        "model": "llama-3.3-70b"
    }


def _summarize_result(result: Any) -> str:
    if isinstance(result, list):
        return f"{len(result)} rows returned"
    if isinstance(result, dict):
        if "error" in result:
            return f"Error: {result['error']}"
        if "results" in result:
            return f"{result.get('results_count', 0)} document chunks found"
        return f"Keys: {list(result.keys())}"
    return str(result)[:100]