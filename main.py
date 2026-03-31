"""
Track 1: HTTP Endpoint for Book Demand Advisor Agent
=====================================================
This file exposes the ADK agent as an HTTP API using FastAPI.
Deploy this on Google Cloud Run to get a live endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import run_agent
import uvicorn

app = FastAPI(
    title="Book Demand Advisor API",
    description="AI-powered book inventory advisor using Google ADK + Gemini",
    version="1.0.0"
)


@app.get("/")
def home():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Book Demand Advisor Agent is live!",
        "usage": "POST /ask with JSON body: { 'book_name': 'The Alchemist' }"
    }


@app.post("/ask")
async def ask_agent(request: Request):
    """
    Main endpoint — accepts a book name and returns inventory advice.

    Request body:
        { "book_name": "The Alchemist" }

    Returns:
        { "book": "...", "advice": "..." }
    """
    try:
        body = await request.json()
        book_name = body.get("book_name", "").strip()

        if not book_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Please provide a 'book_name' in the request body."}
            )

        advice = run_agent(book_name)

        return {
            "book": book_name,
            "advice": advice
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Something went wrong: {str(e)}"}
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
