"""
Track 3: Natural Language Book Query System with AlloyDB
=========================================================
A system where book sales data is stored in AlloyDB for PostgreSQL,
and users can query it using plain English. The system converts
natural language to SQL using Gemini and runs it against AlloyDB.

Dataset: Bookstore sales data (custom — not the lab default dataset)
Use case: "Querying bookstore inventory and sales performance data"

Author: Ayesha Siddiqui
"""

import os
import json
import psycopg2
import google.generativeai as genai

# -----------------------------------------------------------
# Configuration — fill these in before running
# -----------------------------------------------------------

ALLOYDB_HOST = os.environ.get("ALLOYDB_HOST", "YOUR_ALLOYDB_IP")
ALLOYDB_PORT = os.environ.get("ALLOYDB_PORT", "5432")
ALLOYDB_DATABASE = os.environ.get("ALLOYDB_DATABASE", "bookstore_db")
ALLOYDB_USER = os.environ.get("ALLOYDB_USER", "postgres")
ALLOYDB_PASSWORD = os.environ.get("ALLOYDB_PASSWORD", "YOUR_PASSWORD")
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


# -----------------------------------------------------------
# Step 1: Database setup — create table and insert data
# -----------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS bookstore_inventory (
    id SERIAL PRIMARY KEY,
    book_title VARCHAR(300) NOT NULL,
    author VARCHAR(200),
    genre VARCHAR(100),
    publishing_year INT,
    sale_price DECIMAL(8, 2),
    units_sold INT,
    current_stock INT,
    average_rating DECIMAL(3, 2),
    ratings_count INT,
    publisher VARCHAR(200),
    language VARCHAR(50) DEFAULT 'English'
);
"""

SAMPLE_DATA_SQL = """
INSERT INTO bookstore_inventory
    (book_title, author, genre, publishing_year, sale_price, units_sold, current_stock, average_rating, ratings_count, publisher, language)
VALUES
    ('Atomic Habits', 'James Clear', 'Self-Help', 2018, 14.99, 320, 45, 4.8, 95000, 'Avery', 'English'),
    ('The Alchemist', 'Paulo Coelho', 'Fiction', 1988, 12.99, 275, 30, 4.6, 120000, 'HarperOne', 'English'),
    ('Deep Work', 'Cal Newport', 'Self-Help', 2016, 13.99, 180, 22, 4.5, 45000, 'Grand Central', 'English'),
    ('Dune', 'Frank Herbert', 'Science Fiction', 1965, 15.99, 210, 60, 4.7, 200000, 'Ace Books', 'English'),
    ('Educated', 'Tara Westover', 'Memoir', 2018, 13.49, 155, 18, 4.7, 80000, 'Random House', 'English'),
    ('The Midnight Library', 'Matt Haig', 'Fiction', 2020, 14.99, 290, 12, 4.2, 55000, 'Canongate', 'English'),
    ('Ikigai', 'Hector Garcia', 'Self-Help', 2016, 11.99, 195, 35, 4.3, 30000, 'Penguin', 'English'),
    ('Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 2011, 16.99, 240, 28, 4.4, 150000, 'Harper', 'English'),
    ('The Psychology of Money', 'Morgan Housel', 'Finance', 2020, 14.49, 310, 40, 4.6, 65000, 'Harriman House', 'English'),
    ('Think Again', 'Adam Grant', 'Self-Help', 2021, 15.49, 145, 8, 4.1, 25000, 'Viking', 'English'),
    ('Project Hail Mary', 'Andy Weir', 'Science Fiction', 2021, 16.99, 170, 55, 4.9, 70000, 'Ballantine', 'English'),
    ('The Body Keeps the Score', 'Bessel van der Kolk', 'Psychology', 2014, 15.99, 130, 14, 4.7, 42000, 'Viking', 'English'),
    ('Normal People', 'Sally Rooney', 'Fiction', 2018, 12.99, 185, 20, 4.0, 60000, 'Faber & Faber', 'English'),
    ('1984', 'George Orwell', 'Dystopian Fiction', 1949, 10.99, 260, 75, 4.7, 180000, 'Secker & Warburg', 'English'),
    ('The Lean Startup', 'Eric Ries', 'Business', 2011, 14.99, 120, 16, 4.3, 35000, 'Crown Business', 'English')
ON CONFLICT DO NOTHING;
"""

TABLE_SCHEMA_DESCRIPTION = """
Table: bookstore_inventory
Columns:
  - id: unique row number
  - book_title: name of the book
  - author: author name
  - genre: book category (Fiction, Self-Help, Science Fiction, etc.)
  - publishing_year: year the book was published
  - sale_price: current selling price in USD
  - units_sold: total units sold historically
  - current_stock: how many copies are in stock right now
  - average_rating: average reader rating out of 5
  - ratings_count: total number of ratings
  - publisher: publishing company
  - language: language of the book
"""


# -----------------------------------------------------------
# Step 2: Connect to AlloyDB
# -----------------------------------------------------------

def get_db_connection():
    """Create and return a connection to AlloyDB."""
    conn = psycopg2.connect(
        host=ALLOYDB_HOST,
        port=ALLOYDB_PORT,
        database=ALLOYDB_DATABASE,
        user=ALLOYDB_USER,
        password=ALLOYDB_PASSWORD
    )
    return conn


def setup_database():
    """Create table and insert sample data if not already done."""
    print("Setting up AlloyDB database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(SCHEMA_SQL)
    cursor.execute(SAMPLE_DATA_SQL)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database ready with bookstore data.")


# -----------------------------------------------------------
# Step 3: Natural language → SQL using Gemini
# -----------------------------------------------------------

def convert_question_to_sql(natural_language_question: str) -> str:
    """
    Uses Gemini to convert a plain English question into a
    valid PostgreSQL query for the bookstore_inventory table.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are an expert SQL assistant for a PostgreSQL database.

Here is the database table schema:
{TABLE_SCHEMA_DESCRIPTION}

Convert the following question into a valid PostgreSQL SELECT query.
Return ONLY the SQL query — no explanation, no markdown, no backticks.

Question: {natural_language_question}

SQL:
"""

    response = model.generate_content(prompt)
    sql = response.text.strip()

    # Clean up if Gemini accidentally added backticks
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


# -----------------------------------------------------------
# Step 4: Run the SQL query against AlloyDB
# -----------------------------------------------------------

def run_query(sql: str) -> list:
    """Execute the SQL query on AlloyDB and return results."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(zip(columns, row)) for row in rows]


# -----------------------------------------------------------
# Step 5: Format results into a human-readable response
# -----------------------------------------------------------

def format_results(question: str, results: list) -> str:
    """Use Gemini to turn raw query results into a friendly answer."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
The user asked: "{question}"

The database returned these results:
{json.dumps(results, indent=2, default=str)}

Write a short, friendly, human-readable summary of these results.
Be specific — mention book titles, numbers, and any useful insight.
Keep it under 150 words.
"""

    response = model.generate_content(prompt)
    return response.text.strip()


# -----------------------------------------------------------
# Main pipeline: question → SQL → results → response
# -----------------------------------------------------------

def ask_question(question: str) -> dict:
    """
    Full pipeline:
    1. Convert natural language to SQL
    2. Run SQL on AlloyDB
    3. Format results with Gemini
    """
    print(f"\n🔍 Question: {question}")

    sql = convert_question_to_sql(question)
    print(f"📝 Generated SQL: {sql}")

    results = run_query(sql)
    print(f"📊 Rows returned: {len(results)}")

    answer = format_results(question, results)
    print(f"💬 Answer: {answer}")

    return {
        "question": question,
        "sql": sql,
        "results": results,
        "answer": answer
    }


# -----------------------------------------------------------
# Demo: Run sample natural language queries
# -----------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📚 Natural Language Book Query System — AlloyDB + Gemini")
    print("=" * 60)

    # Setup the database first (run once)
    # setup_database()

    # Sample queries that demonstrate the system
    sample_questions = [
        "Which books have fewer than 20 copies in stock?",
        "What are the top 5 best-selling books?",
        "Show me all self-help books with a rating above 4.5",
        "Which books were published after 2019?",
        "What is the average sale price of science fiction books?"
    ]

    for question in sample_questions[:2]:  # Run 2 for demo
        result = ask_question(question)
        print("\n" + "-" * 40)
