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

## Deploying to Vercel

PREREQUISITES:
- Free Vercel account at vercel.com (sign up with GitHub)
- Your GEMINI_API_KEY from aistudio.google.com
- Code pushed to a public GitHub repository

STEP 1 — Push all changes to GitHub:
git add .
git commit -m "Add Vercel deployment config"
git push origin main

STEP 2 — Deploy via Vercel Dashboard:
a) Go to vercel.com and log in
b) Click "Add New Project"
c) Click "Import Git Repository"
d) Find and select your ticket-sorter repository
e) Vercel auto-detects Python — do NOT change the framework preset, leave it as "Other"
f) BEFORE clicking Deploy, expand "Environment Variables"
g) Add this variable:
   Name:  GEMINI_API_KEY
   Value: your actual key from aistudio.google.com
h) Click "Add"
i) Click "Deploy"
j) Wait 1-2 minutes for the build

STEP 3 — Get your live URL:
After deployment Vercel shows you a URL like:
https://ticket-sorter-abc123.vercel.app
This is your base URL. Copy it.

STEP 4 — Verify immediately with these curl commands:

Health check (must respond in under 10 seconds):
curl https://your-app.vercel.app/health

Sort ticket test (must respond in under 30 seconds):
curl -X POST https://your-app.vercel.app/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","channel":"app","locale":"en","message":"I sent 5000 taka to a wrong number"}'

Expected /health response:
{"status":"ok","service":"ticket-sorter"}

Expected /sort-ticket response:
case_type should be "wrong_transfer", severity "high", human_review_required true

STEP 5 — Run full test suite against live URL:
python tests/run_tests.py https://your-app.vercel.app

STEP 6 — What to submit in the hackathon form:
- Live API base URL: https://your-app.vercel.app
- GitHub repository URL: your public GitHub repo URL
- Deployment platform: Vercel
- LLM used: Yes — Google Gemini 2.0 Flash

## Known Limitations

VERCEL FREE TIER (HOBBY) NOTES:
- Default timeout is 10 seconds — we override this to 30 seconds via vercel.json
- Cold start on first request after inactivity may take 5-10 seconds
- /health is lightweight (no Gemini call) and will always respond fast
- /sort-ticket calls Gemini which takes 2-4 seconds — well within 30 second limit
- If a test case fails with a timeout, re-run once — it may have been a cold start
- Wake up the deployment before grading by hitting /health once:
  curl https://your-app.vercel.app/health
