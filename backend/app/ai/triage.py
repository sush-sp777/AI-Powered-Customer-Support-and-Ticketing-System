import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()
import re
import logging
logger = logging.getLogger(__name__)


# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # fast + good reasoning
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


def run_ai_triage(title: str, description: str):

    system_prompt = """
You are an enterprise AI support ticket triage engine.

Analyze the support ticket and return STRICT valid JSON only.

Return this exact structure:

{
  "category": "BILLING | TECHNICAL | ACCOUNT | GENERAL",
  "priority": "LOW | MEDIUM | HIGH | URGENT",
  "sentiment": "POSITIVE | NEUTRAL | NEGATIVE",
  "risk": "LOW | MEDIUM | HIGH",
  "confidence": float between 0 and 1,
  "ai_summary": "1 short sentence summary"
}

Classification Rules:

Category:
- Payment, refund, invoice → BILLING
- Login, password, account access → ACCOUNT
- Bug, crash, error, system failure → TECHNICAL
- General info or feature question → GENERAL

Risk:
- Security breach, fraud, data loss → HIGH
- Angry customer + billing issue → HIGH
- Normal bug without urgency → MEDIUM
- Simple query → LOW

Priority:
- Urgent words like "immediately", "ASAP", "critical" → URGENT
- Payment failure or system down → HIGH
- Normal bug → MEDIUM
- Question → LOW

Confidence:
- High clarity issue → 0.8 to 1.0
- Slight ambiguity → 0.6 to 0.8
- Unclear issue → below 0.6

Return ONLY JSON.
Do not explain.
"""

    user_prompt = f"""
Title: {title}
Description: {description}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    content = response.content.strip()

    # Safe JSON extraction
    match = re.search(r"\{.*\}", content, re.DOTALL)

    if not match:
        return fallback_response()

    json_text = match.group()

    try:
        parsed = json.loads(json_text)
        logger.info(f"AI TRIAGE RESULT → {parsed}")

        return parsed
    except json.JSONDecodeError:
        return fallback_response()


def fallback_response():
    return {
        "category": "GENERAL",
        "priority": "MEDIUM",
        "sentiment": "NEUTRAL",
        "risk": "LOW",
        "confidence": 0.5,
        "ai_summary": "AI parsing failed."
    }