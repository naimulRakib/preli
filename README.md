---
title: Ticket Sorter API
emoji: 🎫
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Ticket Sorter API

A FastAPI service that classifies bKash customer support tickets using Google Gemini AI.

## Endpoints

### GET /health
Returns service health status.

**Response:**
```json
{"status": "ok", "service": "ticket-sorter"}
```

### POST /sort-ticket
Classifies a customer support ticket.

**Request:**
```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number"
}
```

**Response:**
```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT to an incorrect number and requests a reversal.",
  "human_review_required": true,
  "confidence": 0.92
}
```

## Tech Stack
- FastAPI + Uvicorn
- Google Gemini 2.0 Flash
- Deployed on Hugging Face Spaces (Docker)

## Local Setup
1. Clone this repo
2. Create venv: `python -m venv venv && source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`
5. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Running Tests
```bash
pip install -r tests/requirements_test.txt

# Local
python tests/run_tests.py

# Live
python tests/run_tests.py https://YOUR_USERNAME-ticket-sorter.hf.space
```

## Deploying to Hugging Face Spaces

PREREQUISITES:
- Free Hugging Face account at huggingface.co
- Your GEMINI_API_KEY from aistudio.google.com
- Git installed locally

STEP 1 — Create a new Space on Hugging Face:
a) Go to huggingface.co and log in
b) Click your profile icon → New Space
c) Fill in:
   - Owner: your username
   - Space name: ticket-sorter
   - License: MIT
   - SDK: Docker   ← IMPORTANT: select Docker, not Gradio or Streamlit
   - Visibility: Public
d) Click "Create Space"
e) You will see an empty repo with a placeholder README

STEP 2 — Add your GEMINI_API_KEY as a Secret:
a) In your Space, click "Settings" tab
b) Scroll to "Variables and secrets" section
c) Click "New secret"
d) Name:  GEMINI_API_KEY
e) Value: your actual Gemini API key
f) Click Save
IMPORTANT: Use "secret" not "variable" — secrets are hidden from logs

STEP 3 — Push your code to the Space:
Run these commands from your project root:

# Add Hugging Face as a remote (keep your GitHub remote too)
git remote add hfspace https://huggingface.co/spaces/YOUR_USERNAME/ticket-sorter

# Push to Hugging Face
git push hfspace main

When prompted for credentials:
- Username: your Hugging Face username
- Password: your Hugging Face ACCESS TOKEN (not your login password)
  Get it from: huggingface.co/settings/tokens → New token → Role: Write

STEP 4 — Watch the build:
a) Go to your Space page on Hugging Face
b) Click the "Build" tab to watch live logs
c) Build takes 2-4 minutes (installing dependencies)
d) When you see "Uvicorn running on http://0.0.0.0:7860" in logs → it's live

STEP 5 — Get your live URL:
Your URL format is:
https://YOUR_USERNAME-ticket-sorter.hf.space

Example: if your username is "naimul123":
https://naimul123-ticket-sorter.hf.space

STEP 6 — Verify immediately with these curl commands:

Health check:
curl https://YOUR_USERNAME-ticket-sorter.hf.space/health

Sort ticket test:
curl -X POST https://YOUR_USERNAME-ticket-sorter.hf.space/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","channel":"app","locale":"en","message":"I sent 5000 taka to a wrong number"}'

Expected health: {"status":"ok","service":"ticket-sorter"}
Expected sort: case_type "wrong_transfer", severity "high"

STEP 7 — Run full test suite against live URL:
python tests/run_tests.py https://YOUR_USERNAME-ticket-sorter.hf.space

STEP 8 — What to submit in the hackathon form:
- Live API base URL: https://YOUR_USERNAME-ticket-sorter.hf.space
- GitHub repository URL: your GitHub repo URL
- Deployment platform: Hugging Face Spaces (Docker)
- LLM used: Yes — Google Gemini 2.0 Flash

## Known Limitations

HUGGING FACE SPACES FREE TIER NOTES:
- Spaces sleep after 30 minutes of inactivity
- First request after sleep takes 10-15 seconds (cold start)
- If grader hits a cold start, /health may be slow but will recover
- /sort-ticket has a 30 second timeout in the spec — cold start + Gemini = tight
- Solution: ping /health once first to wake the Space before running test suite
- Wake-up curl: curl https://YOUR_USERNAME-ticket-sorter.hf.space/health
