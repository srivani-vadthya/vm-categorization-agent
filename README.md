# Categorization Agent

A rule-based IT incident categorization REST API built with FastAPI. It receives a support ticket, classifies it into a support level (L1 / L2 / L3) or rejects it, detects the technology domain, and returns a routing decision — all in one API call.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [File Descriptions](#file-descriptions)
- [Request & Response Format](#request--response-format)
- [Setup & Run](#setup--run)
- [Example Usage](#example-usage)
- [Support Level Reference](#support-level-reference)

---

## How It Works

```
Incoming Ticket (title + description)
        │
        ▼
  reject_rules.py  ──► REJECT  (non-operational: vacation, help, how-to, etc.)
        │
        ▼
   l1_rules.py     ──► L1      (vpn, login, browser, cache, password, etc.)
        │
        ▼
   l3_rules.py     ──► L3      (exception, stacktrace, code defect, regression, etc.)
        │
        ▼
   default         ──► L2      (cpu, memory, database, kubernetes, api, latency, etc.)
        │
        ▼
technology_rules.py ──► detects technology (Guidewire, Kubernetes, Database, etc.)
        │
        ▼
routing_service.py  ──► determines which downstream agent to route to
        │
        ▼
  JSON Response returned
```

The categorization logic runs in priority order: **REJECT → L1 → L3 → L2 (default)**.

---

## Project Structure

```
categorization-agent/
├── agents/
│   └── categorization_agent.py     # Core categorization logic
├── api/
│   └── categorization_api.py       # FastAPI route definition
├── models/
│   └── categorization_result.py    # Pydantic response model
├── prompts/
│   └── categorization_prompt.txt   # LLM prompt reference (documentation)
├── rules/
│   ├── reject_rules.py             # Keywords that trigger rejection
│   ├── l1_rules.py                 # Keywords for L1 support
│   ├── l2_rules.py                 # Keywords for L2 support
│   ├── l3_rules.py                 # Keywords for L3 support
│   └── technology_rules.py         # Technology domain detection
├── services/
│   └── routing_service.py          # Routing decision logic
├── utils/
│   └── logger_config.py            # Centralized logging setup
├── main.py                         # FastAPI app entry point
└── requirements.txt                # Python dependencies
```

---

## File Descriptions

### `main.py`
Entry point of the application. Creates the FastAPI app, registers the `/categorize` router, and exposes a health-check endpoint at `GET /`.

### `api/categorization_api.py`
Defines the `POST /categorize` endpoint. Accepts a free-form JSON dictionary (ticket payload) and delegates to the categorization agent.

### `agents/categorization_agent.py`
The brain of the system. The `categorize(payload)` function:
1. Combines `title` and `description` into a single text string.
2. Detects the technology using `technology_rules.py`.
3. Runs the text through reject → L1 → L3 checks in order.
4. Falls back to L2 if no other rule matches.
5. Returns a structured result dict with classification, support level, team, technology, routing target, confidence, and reason.

### `models/categorization_result.py`
Pydantic model (`CategorizationResult`) that defines the shape of the API response. Used for documentation and validation.

### `rules/reject_rules.py`
Contains `REJECT_KEYWORDS` (e.g., `"vacation"`, `"how to"`, `"help"`) and the `is_rejected(text)` function. If any keyword is found in the ticket text, the ticket is rejected immediately.

### `rules/l1_rules.py`
Contains `L1_KEYWORDS` (e.g., `"vpn"`, `"login"`, `"browser"`, `"cache"`) and `is_l1(text)`. Matches basic end-user support issues.

### `rules/l2_rules.py`
Contains `L2_KEYWORDS` (e.g., `"cpu"`, `"database"`, `"kubernetes"`, `"latency"`) and `is_l2(text)`. Matches operational/infrastructure issues. Note: L2 is also the default fallback — `is_l2()` is not called directly in the agent; L2 is returned when no other rule matches.

### `rules/l3_rules.py`
Contains `L3_KEYWORDS` (e.g., `"exception"`, `"stacktrace"`, `"regression"`, `"traceback"`) and `is_l3(text)`. Matches code-level and development issues.

### `rules/technology_rules.py`
The `detect_technology(text)` function scans the ticket text for technology-specific keywords and returns a label: `Guidewire`, `ServiceNow`, `Kubernetes`, `Database`, `Application`, `Infrastructure`, or `General`.

### `services/routing_service.py`
The `determine_route(support_level, technology)` function maps the support level + technology combination to a downstream agent name (e.g., `l2_guidewire_agent`, `l3_development_agent`, `l1_support_agent`).

### `prompts/categorization_prompt.txt`
A reference prompt describing the full categorization logic in natural language. This serves as documentation for the rules and can be used as a system prompt if an LLM-based version of the agent is built in the future.

### `utils/logger_config.py`
Sets up a shared `logger` instance with a timestamped format. Import and use this logger across any module for consistent logging.

### `requirements.txt`
Lists the three dependencies:
- `fastapi` — web framework
- `uvicorn` — ASGI server to run FastAPI
- `pydantic` — data validation for the response model

---

## Request & Response Format

### Request — `POST /categorize`

```json
{
  "ticket_id": "INC001",
  "title": "Kubernetes pod crash loop",
  "description": "Multiple pods in the production cluster are in CrashLoopBackOff state."
}
```

### Response

```json
{
  "ticket_id": "INC001",
  "classification": "INCIDENT",
  "support_level": "L2",
  "team": "Operations",
  "technology": "Kubernetes",
  "route_to": "l2_application_agent",
  "confidence": 0.85,
  "reject": false,
  "reason": "Operational issue"
}
```

### Rejected Ticket Response

```json
{
  "ticket_id": "INC002",
  "classification": "REJECT",
  "support_level": "NONE",
  "reject": true,
  "confidence": 0.95,
  "reason": "Non-operational request",
  "route_to": "reject"
}
```

---

## Setup & Run

### Prerequisites
- Python 3.9 or higher
- pip

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd categorization-agent
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### 5. Open the interactive API docs

Navigate to `http://127.0.0.1:8000/docs` in your browser to explore and test all endpoints using the built-in Swagger UI.

---

## Example Usage

Using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/categorize" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "INC003",
    "title": "VPN not connecting",
    "description": "User cannot connect to VPN after password change."
  }'
```

Using Python `requests`:

```python
import requests

payload = {
    "ticket_id": "INC003",
    "title": "VPN not connecting",
    "description": "User cannot connect to VPN after password change."
}

response = requests.post("http://127.0.0.1:8000/categorize", json=payload)
print(response.json())
```

---

## Support Level Reference

| Level | Team        | Trigger Examples                                      | Route                        |
|-------|-------------|-------------------------------------------------------|------------------------------|
| REJECT | —          | vacation, help, how to, general query                 | `reject`                     |
| L1    | Support     | vpn, login, browser, cache, access denied             | `l1_support_agent`           |
| L2    | Operations  | cpu, memory, database, kubernetes, api, latency       | `l2_*_agent` (by technology) |
| L3    | Development | exception, stacktrace, regression, traceback, compile | `l3_development_agent`       |

### L2 Routing by Technology

| Technology     | Route                      |
|----------------|----------------------------|
| Guidewire      | `l2_guidewire_agent`       |
| Infrastructure | `l2_infrastructure_agent`  |
| Database       | `l2_database_agent`        |
| All others     | `l2_application_agent`     |
