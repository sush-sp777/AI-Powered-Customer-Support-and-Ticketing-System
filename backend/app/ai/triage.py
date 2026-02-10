def run_ai_triage(title: str, description: str):
    text = f"{title} {description}".lower()

    # CATEGORY
    if "password" in text or "login" in text:
        category = "AUTH"
    elif "payment" in text or "refund" in text:
        category = "BILLING"
    else:
        category = "GENERAL"

    # PRIORITY
    if "urgent" in text or "immediately" in text:
        priority = "HIGH"
    else:
        priority = "MEDIUM"

    # SENTIMENT
    if "angry" in text or "frustrated" in text:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"

    # RISK
    risk = "HIGH" if category == "BILLING" else "LOW"

    confidence = 0.85 if category != "GENERAL" else 0.6

    ai_summary = f"Detected {category} issue with {priority} priority."

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "confidence": confidence,
        "risk": risk,
        "ai_summary": ai_summary
    }
