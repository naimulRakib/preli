# Ticket Sorter

A production-ready REST API service that classifies digital finance customer support tickets using AI. It processes customer messages and automatically categorizes them, determining severity and routing to the appropriate department.

## Tech Stack
- Python 3.11+
- FastAPI
- Google Gemini 2.0 Flash (via google-generativeai SDK)
- Uvicorn
- Koyeb for Deployment

## Local Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ticket-sorter
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`:
   ```bash
   cp .env.example .env
   ```

5. Run the application locally:
   ```bash
   python main.py
   ```

## API Endpoints

### GET /health
Check the health status of the service.
```bash
curl https://your-app.koyeb.app/health
```

### POST /sort-ticket
Classify a new customer support ticket.
```bash
curl -X POST https://your-app.koyeb.app/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","channel":"app","locale":"en","message":"I sent 5000 taka to a wrong number"}'
```

## Deployment on Koyeb

1. Push your code to a public GitHub repository.
2. Go to [Koyeb](https://www.koyeb.com/) and sign up for a free account.
3. Click **New App** -> Select **GitHub** -> Choose this repository.
4. Set the **Build command**: `pip install -r requirements.txt`
5. Set the **Run command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
6. Add the environment variable: `GEMINI_API_KEY` = `<your actual key>`
7. Click **Deploy**.
8. Your live HTTPS URL will be available in the dashboard (e.g., `https://your-app-name.koyeb.app`).

## Sample Test Cases

**1. Wrong Transfer**
* **Message:** "I sent 3000 to wrong number"
* **Expected:** `case_type`: "wrong_transfer", `severity`: "high"

**2. Phishing Attempt**
* **Message:** "Someone called asking my OTP, is that bKash?"
* **Expected:** `case_type`: "phishing_or_social_engineering", `severity`: "critical", `human_review_required`: true

**3. Payment Failed**
* **Message:** "Payment failed but balance deducted"
* **Expected:** `case_type`: "payment_failed", `department`: "payments_ops"

**4. Refund Request**
* **Message:** "Please refund my last transaction"
* **Expected:** `case_type`: "refund_request", `severity`: "low"

**5. Other Issue**
* **Message:** "App crashed when I opened it"
* **Expected:** `case_type`: "other", `severity`: "low"

## Running Tests

1. Install test dependencies:
   ```bash
   pip install -r tests/requirements_test.txt
   ```

2. Run against local server:
   ```bash
   python tests/run_tests.py
   ```

3. Run against live deployment:
   ```bash
   python tests/run_tests.py https://your-app.koyeb.app
   ```

4. What each result means:
   * **PASS** = all 8 checks passed for this case
   * **FAIL** = one or more checks failed (details printed below the case)
   * **WARN** = response received but confidence is 0 (fallback triggered)

## Known Limitations
None — this service is completely stateless and designed to run persistently on Koyeb's free tier without cold starts.
# preli
