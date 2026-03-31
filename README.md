# 🗄️ Track 3 — Natural Language Book Query System with AlloyDB

**Google Cloud Gen AI Academy | Cohort 1 | Track 3**

---

## What This Project Does

This project lets anyone query a bookstore inventory database using plain English. Instead of writing SQL, you just ask a question like *"Which books have fewer than 20 copies in stock?"* — and the system figures out the rest.

It uses **AlloyDB for PostgreSQL** to store a custom bookstore dataset, and **Gemini** to translate natural language into SQL and turn raw results into friendly, readable answers.

**Use case:** Querying bookstore inventory and sales performance data

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Database | AlloyDB for PostgreSQL |
| AI Model | Gemini 2.0 Flash |
| API Layer | FastAPI |
| Deployment | Google Cloud Run |
| Language | Python 3.11 |

---

## Dataset

The dataset is a **custom bookstore inventory** I created — it is NOT the default lab dataset.

It contains 15 real books with these fields:

| Column | Description |
|--------|-------------|
| book_title | Name of the book |
| author | Author name |
| genre | Category (Fiction, Self-Help, etc.) |
| publishing_year | Year published |
| sale_price | Current price (USD) |
| units_sold | Historical sales |
| current_stock | Copies currently in stock |
| average_rating | Reader rating out of 5 |
| ratings_count | Number of ratings |
| publisher | Publishing company |

---

## Project Structure

```
track3/
├── main.py           # Core pipeline: NL → SQL → AlloyDB → response
├── api.py            # FastAPI HTTP endpoint
├── Dockerfile        # For Cloud Run
├── requirements.txt
└── README.md
```

---

## How It Works

```
User question (plain English)
        ↓
Gemini converts to SQL
        ↓
SQL runs on AlloyDB
        ↓
Results returned
        ↓
Gemini formats into friendly answer
```

---

## Sample Queries

```
"Which books have fewer than 20 copies in stock?"
→ SQL: SELECT book_title, current_stock FROM bookstore_inventory WHERE current_stock < 20
→ Answer: "Several books are running low — Think Again (8 copies), The Body Keeps the Score (14), and Educated (18) all need restocking soon."

"What are the top 5 best-selling books?"
→ SQL: SELECT book_title, units_sold FROM bookstore_inventory ORDER BY units_sold DESC LIMIT 5

"Show me all self-help books with rating above 4.5"
→ SQL: SELECT * FROM bookstore_inventory WHERE genre = 'Self-Help' AND average_rating > 4.5
```

---

## API Usage

```
POST /query
Content-Type: application/json

{
  "question": "Which books need reordering?"
}
```

Response:
```json
{
  "question": "Which books need reordering?",
  "sql": "SELECT book_title, current_stock FROM bookstore_inventory WHERE current_stock < 20 ORDER BY current_stock ASC",
  "results": [...],
  "answer": "Based on current stock, these books need reordering urgently: Think Again (8 copies), The Midnight Library (12), and The Body Keeps the Score (14). I'd recommend placing orders for these titles soon."
}
```

---

## Setup

```bash
# 1. Set environment variables
export ALLOYDB_HOST=your_alloydb_ip
export ALLOYDB_DATABASE=bookstore_db
export ALLOYDB_USER=postgres
export ALLOYDB_PASSWORD=your_password
export GOOGLE_API_KEY=your_gemini_key

# 2. Run setup (creates table + inserts data)
python -c "from main import setup_database; setup_database()"

# 3. Start the API
python api.py
```

---

## Explicit Constraint Compliance

✅ Dataset is custom (not the lab default)
✅ Table schema was created by me
✅ Natural language queries are my own, not copied from the lab
✅ Use case: "Querying bookstore inventory and sales performance data"

---

*Built for Google Cloud Gen AI Academy APAC — Cohort 1*
