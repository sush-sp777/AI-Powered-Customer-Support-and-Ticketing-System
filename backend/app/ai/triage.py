import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # fast + good reasoning
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


def run_ai_triage(title: str, description: str):
    """
    Uses LLM to analyze ticket and return structured triage metadata.
    """

    system_prompt = """
You are an AI support triage engine.

Analyze the support ticket and respond ONLY in valid JSON.

Return:
{
  "category": "BILLING | TECHNICAL | ACCOUNT | GENERAL",
  "priority": "LOW | MEDIUM | HIGH | URGENT",
  "sentiment": "POSITIVE | NEUTRAL | NEGATIVE",
  "confidence": float between 0 and 1,
  "risk": "LOW | MEDIUM | HIGH",
  "ai_summary": "short 1-line summary"
}

Rules:
- Billing/payment/refund → BILLING
- Login/password/account access → ACCOUNT
- System bug/error/crash → TECHNICAL
- General query → GENERAL
- Angry/frustrated tone → HIGH risk
- Calm tone → LOW risk
Return ONLY JSON. No explanation.

Risk rules:
- Simple password reset issues → LOW risk
- Payment disputes with anger → HIGH risk
- Security breach or fraud → HIGH risk
- Technical bug without urgency → MEDIUM risk

"""

    user_prompt = f"""
Title: {title}
Description: {description}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    try:
        parsed = json.loads(response.content)
        return parsed
    except Exception:
        # fallback in case model outputs bad JSON
        return {
            "category": "GENERAL",
            "priority": "MEDIUM",
            "sentiment": "NEUTRAL",
            "confidence": 0.5,
            "risk": "LOW",
            "ai_summary": "AI parsing failed."
        }
