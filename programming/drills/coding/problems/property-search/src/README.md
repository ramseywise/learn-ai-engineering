# AI Property Search

A semantic search system for real estate properties using FastAPI, FAISS, and sentence transformers.

## Files

- `main.py` - FastAPI application with search logic
- `properties.json` - Property catalog (50 real estate listings)
- `index.html` - Web interface

## Usage

Search for properties using natural language queries like:

- "condo"
- "waterfront home"
- "family home with yard"
- "downtown apartment"

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
uvicorn main:app --reload
```

4. Open your browser and navigate to:

```text
http://localhost:8000
```

## Code Test Instructions

Review the codebase and identify any issues with the search functionality.

After debugging, be prepared to discuss how you would implement additional filtering features.
