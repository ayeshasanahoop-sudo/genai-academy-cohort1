"""
Track 2: Book Info Agent with MCP Integration
==============================================
An ADK agent that uses MCP to connect to the Google Books API,
retrieves real book information, and generates a smart summary
with reading & inventory insights using Gemini.

Author: Ayesha Siddiqui
"""

import os
import json
import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# -----------------------------------------------------------
# MCP Tool: Fetch data from Google Books API (external source)
# -----------------------------------------------------------

def fetch_book_from_google_books(book_title: str) -> dict:
    """
    MCP Tool: Connects to the Google Books API to retrieve
    real metadata about a book — title, author, description,
    page count, categories, and average rating.

    This is the 'external data source' connected via MCP pattern.
    """
    try:
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": book_title, "maxResults": 1}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if not data.get("items"):
            return {
                "found": False,
                "message": f"No results found for '{book_title}' in Google Books."
            }

        item = data["items"][0]["volumeInfo"]

        return {
            "found": True,
            "title": item.get("title", "Unknown"),
            "authors": ", ".join(item.get("authors", ["Unknown"])),
            "description": item.get("description", "No description available.")[:400],
            "page_count": item.get("pageCount", "N/A"),
            "categories": ", ".join(item.get("categories", ["General"])),
            "average_rating": item.get("averageRating", "Not rated"),
            "ratings_count": item.get("ratingsCount", 0),
            "published_date": item.get("publishedDate", "Unknown"),
            "language": item.get("language", "Unknown")
        }

    except Exception as e:
        return {
            "found": False,
            "message": f"Failed to fetch data: {str(e)}"
        }


def analyze_book_for_bookstore(
    title: str,
    average_rating: float,
    ratings_count: int,
    categories: str
) -> dict:
    """
    Analyzes a book's commercial potential for a bookstore
    based on rating and popularity signals.
    """
    # Score based on rating and number of reviews
    popularity_score = (average_rating or 0) * (min(ratings_count, 1000) / 100)

    if popularity_score > 30:
        demand_level = "HIGH"
        stock_advice = "Stock 50+ units. This is a popular title."
    elif popularity_score > 10:
        demand_level = "MEDIUM"
        stock_advice = "Stock 20-30 units. Steady demand expected."
    else:
        demand_level = "LOW"
        stock_advice = "Stock 5-10 units. Niche audience."

    genre_premium = "Yes" if any(g in categories.lower() for g in ["fiction", "self-help", "business"]) else "No"

    return {
        "demand_level": demand_level,
        "stock_advice": stock_advice,
        "popularity_score": round(popularity_score, 2),
        "genre_premium_category": genre_premium
    }


# -----------------------------------------------------------
# ADK Agent Definition
# -----------------------------------------------------------

book_mcp_agent = Agent(
    name="book_mcp_agent",
    model="gemini-2.0-flash",
    description=(
        "An AI agent that connects to Google Books (via MCP pattern) "
        "to retrieve real book information and provide smart bookstore insights."
    ),
    instruction="""
        You are a knowledgeable book advisor for an independent bookstore.

        When a user asks about a book:
        1. Use fetch_book_from_google_books to get real data about the book.
        2. Use analyze_book_for_bookstore with the rating and category data.
        3. Combine both to write a warm, helpful response that includes:
           - A brief summary of what the book is about
           - Who would enjoy reading it
           - Your honest stocking recommendation for a bookstore

        Write like a human who loves books — not like a robot.
        Keep the response under 200 words and end with a clear recommendation.
    """,
    tools=[fetch_book_from_google_books, analyze_book_for_bookstore],
)


# -----------------------------------------------------------
# Runner
# -----------------------------------------------------------

def run_agent(book_title: str) -> str:
    """Run the MCP agent for a given book title."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=book_mcp_agent,
        app_name="book_mcp_app",
        session_service=session_service
    )

    session = session_service.create_session(
        app_name="book_mcp_app",
        user_id="user_001"
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=f"Tell me about the book '{book_title}' and whether I should stock it.")]
    )

    response_text = ""
    for event in runner.run(
        user_id="user_001",
        session_id=session.id,
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    response_text += part.text

    return response_text


# -----------------------------------------------------------
# Local test
# -----------------------------------------------------------

if __name__ == "__main__":
    test_book = "Atomic Habits"
    print(f"\nFetching insights for: '{test_book}'\n")
    print(run_agent(test_book))
