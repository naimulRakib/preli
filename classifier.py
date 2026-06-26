import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def classify_ticket(ticket_id: str, message: str, channel: str, locale: str) -> dict:
    fallback = {
        "ticket_id": ticket_id,
        "case_type": "other",
        "severity": "low",
        "department": "customer_support",
        "agent_summary": "Unable to classify this ticket automatically. Please review manually.",
        "confidence": 0.0,
        "human_review_required": True
    }

    prompt = f"""You are a customer support ticket classifier for a digital mobile banking service (like bKash in Bangladesh). 

Classify the following customer support message and return ONLY a valid JSON object with no extra text, no markdown, no code blocks.

Customer message: "{message}"
Channel: "{channel}"
Locale: "{locale}"

Return this exact JSON structure:
{{
  "case_type": "<one of: wrong_transfer, payment_failed, refund_request, phishing_or_social_engineering, other>",
  "severity": "<one of: low, medium, high, critical>",
  "department": "<one of: customer_support, dispute_resolution, payments_ops, fraud_risk>",
  "agent_summary": "<1-2 neutral sentences describing the ticket for an agent. NEVER ask the customer to share PIN, OTP, password, or card number>",
  "confidence": <float between 0.0 and 1.0>
}}

Classification rules:
- wrong_transfer → severity: high → department: dispute_resolution
- payment_failed → severity: high → department: payments_ops  
- refund_request → severity: low (unless disputed) → department: customer_support or dispute_resolution
- phishing_or_social_engineering → severity: critical → department: fraud_risk
- other → severity: low → department: customer_support

human_review_required is true if severity is "critical" OR case_type is "phishing_or_social_engineering". Do NOT include this field in your JSON — it will be computed separately.

IMPORTANT SAFETY RULE: The agent_summary must NEVER contain phrases like "share your OTP", "provide your PIN", "give your password", or "send your card number". Violation of this rule causes automatic failure."""

    try:
        if not api_key:
            return fallback

        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        
        human_review_required = (result.get("severity") == "critical") or (result.get("case_type") in ["phishing_or_social_engineering", "wrong_transfer"])
        
        result["human_review_required"] = human_review_required
        result["ticket_id"] = ticket_id
        
        # Ensure all required fields exist
        required_fields = ["case_type", "severity", "department", "agent_summary", "confidence"]
        for field in required_fields:
            if field not in result:
                result[field] = fallback[field]
                
        # Additional safety check against leaking PIN/OTP
        bad_phrases = ["pin", "otp", "password", "card number"]
        summary_lower = result.get("agent_summary", "").lower()
        if any(phrase in summary_lower for phrase in bad_phrases):
            result["agent_summary"] = "Redacted agent summary due to safety rule violation. Please review manually."
            result["human_review_required"] = True
            
        return result
        
    except Exception as e:
        print(f"Error classifying ticket: {e}")
        return fallback
