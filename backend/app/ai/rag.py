from backend.app.knowledge_base.faqs import KNOWLEDGE_BASE

def generate_draft_reply(ai_metadata: dict):
    category = ai_metadata.get("category")

    for item in KNOWLEDGE_BASE:
        if item["category"] == category:
            return item["answer"]

    return "Thank you for contacting support. An agent will assist you shortly."
