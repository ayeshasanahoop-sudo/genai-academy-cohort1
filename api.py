"""
Track 3: REST API for Natural Language Book Queries
====================================================
Wraps the AlloyDB + Gemini pipeline in a FastAPI endpoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from main import ask_question
import uvicorn

app = FastAPI(
    title="Bookstore Natural Language Query API",
    description="Ask questions about book inventory in plain English — powered by AlloyDB + Gemini",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "AlloyDB Natural Language Query System is live!",
        "usage": "POST /query with JSON: { 'question': 'Which books need reordering?' }"
    }


@app.post("/query")
async def query(request: Request):
    """
    Accepts a natural language question about the bookstore inventory,
    converts it to SQL using Gemini, runs it on AlloyDB, and returns
    a human-readable answer.
    """
    try:
        body = await request.json()
        question = body.get("question", "").strip()

        if not question:
            return JSONResponse(
                status_code=400,
                content={"error": "Please provide a 'question' in the request body."}
            )

        result = ask_question(question)
        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Query failed: {str(e)}"}
        )


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
