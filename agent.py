"""
Track 1: Book Demand Advisor Agent
===================================
An AI agent built with Google ADK and Gemini that accepts a book name
via HTTP and returns demand prediction + inventory advice.

Author: Ayesha Siddiqui
"""

import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# -----------------------------------------------------------
# Define the tools our agent can use
# -----------------------------------------------------------

def get_book_demand_info(book_name: str) -> dict:
    """
    Returns a simple demand profile for a given book.
    In a real system, this would query a database or ML model.
    For this demo, we return structured mock data.
    """
    # Simulated demand data (replace with real DB/model in production)
    sample_data = {
        "default": {
            "genre": "General Fiction",
            "avg_rating": 3.8,
            "units_sold_last_month": 42,
            "current_stock": 15,
            "sale_price": 12.99
        }
    }

    book_key = book_name.lower().strip()
    data = sample_data.get(book_key, sample_data["default"])
    data["book_name"] = book_name
    return data


def recommend_inventory_action(current_stock: int, predicted_demand: int) -> dict:
    """
    Given current stock and predicted demand, returns a simple recommendation.
    """
    ratio = current_stock / (predicted_demand + 1)

    if ratio < 0.8:
        action = "REORDER"
        message = f"Stock is low. Order at least {predicted_demand - current_stock} more units."
        priority = "HIGH"
    elif ratio > 1.5:
        action = "CLEARANCE"
        message = "You have excess stock. Consider a discount or promotion."
        priority = "LOW"
    else:
        action = "MAINTAIN"
        message = "Stock levels look healthy. No immediate action needed."
        priority = "MEDIUM"

    return {
        "action": action,
        "message": message,
        "priority": priority,
        "current_stock": current_stock,
        "predicted_demand": predicted_demand
    }


# -----------------------------------------------------------
# Create the ADK Agent
# -----------------------------------------------------------

book_demand_agent = Agent(
    name="book_demand_advisor",
    model="gemini-2.0-flash",
    description=(
        "An intelligent book inventory advisor. "
        "It takes a book name as input, looks up its demand profile, "
        "and recommends whether to reorder, maintain, or clear stock."
    ),
    instruction="""
        You are a helpful book inventory advisor for a bookstore.
        When a user gives you a book name:
        1. Use the get_book_demand_info tool to fetch the book's data.
        2. Use the recommend_inventory_action tool with the current stock and units sold.
        3. Respond in a friendly, clear, conversational tone.
        4. Always end with a one-line summary of what action to take.
        Keep your response concise — under 150 words.
    """,
    tools=[get_book_demand_info, recommend_inventory_action],
)


# -----------------------------------------------------------
# Runner setup (for local testing)
# -----------------------------------------------------------

def run_agent(book_name: str) -> str:
    """Run the agent for a given book name and return its response."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=book_demand_agent,
        app_name="book_demand_app",
        session_service=session_service
    )

    session = session_service.create_session(
        app_name="book_demand_app",
        user_id="user_001"
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=f"What should I do about inventory for the book: {book_name}?")]
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
# Entry point for quick local test
# -----------------------------------------------------------

if __name__ == "__main__":
    test_book = "The Alchemist"
    print(f"\nTesting agent with book: '{test_book}'\n")
    result = run_agent(test_book)
    print("Agent Response:")
    print(result)
