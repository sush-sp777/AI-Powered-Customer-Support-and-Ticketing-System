import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from backend.app.ai.rag import retrieve_context

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

def generate_auto_reply(title: str, description: str, ai_metadata: dict):
    context = retrieve_context(description)

    system_prompt = f"""
You are a senior AI customer support agent.

Ticket Metadata:
- Category: {ai_metadata['category']}
- Priority: {ai_metadata['priority']}
- Sentiment: {ai_metadata['sentiment']}
- Risk Level: {ai_metadata['risk']}

Behavior Rules:

1. Tone Control:
   - If sentiment is NEGATIVE → be empathetic.
   - If sentiment is FRUSTRATED → acknowledge emotion first.
   - If sentiment is NEUTRAL → professional tone.

2. Risk Awareness:
   - If risk is HIGH → do NOT finalize resolution.
     Provide next steps and mention escalation.
   - If risk is LOW → you may provide complete solution.

3. Knowledge Usage:
   - Use knowledge base context if relevant.
   - Do NOT invent policies.
   - If knowledge is insufficient, respond cautiously.

4. Response Structure:
   - Greeting
   - Acknowledgement
   - Clear solution steps
   - Closing reassurance

Never mention you are an AI.
Keep response concise but helpful.
"""

    user_prompt = f"""
Knowledge Base Context:
{context}

Ticket Title: {title}
Ticket Description: {description}

Write the final customer reply.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return response.content


def generate_agent_draft(ticket, messages, ai_metadata: dict):
    context = retrieve_context(ticket.description)

    conversation_text = "\n".join(
        [f"{msg.sender_role}: {msg.message}" for msg in messages]
    )

    system_prompt = f"""
You are a senior customer support strategist assisting a HUMAN AGENT.

Ticket Intelligence:
- Category: {ticket.category}
- Priority: {ticket.priority}
- Risk Level: {ai_metadata['risk']}
- Sentiment: {ai_metadata['sentiment']}
- AI Confidence: {ai_metadata['confidence']}
- AI Summary: {ai_metadata['ai_summary']}

Strategic Rules:

1. Emotional Awareness:
   - If sentiment is NEGATIVE or FRUSTRATED → begin with empathy.
   - If customer is calm → remain professional.

2. Risk Control:
   - If risk is HIGH → avoid final commitments.
     Recommend escalation or verification steps.
   - If risk is LOW → provide clear resolution path.

3. Priority Handling:
   - HIGH priority → structured, bullet-based response.
   - LOW priority → concise and simple.

4. Category Guidance:
   - BILLING → ensure financial clarity and refund explanation.
   - ACCOUNT → provide step-by-step instructions.
   - TECHNICAL → troubleshooting sequence.

5. Knowledge Usage:
   - Use knowledge base context if relevant.
   - Never invent policies.
   - If unsure, suggest verification instead of guessing.

Output Requirements:
- Professional tone
- Clear structure
- Actionable next steps
- No mention of AI
- Optimized for human agent to send
- Never mention about draft, like here is a reply

Never mention you are an AI.
Keep response concise but helpful.
"""

    user_prompt = f"""
Knowledge Base Context:
{context}

Ticket Title:
{ticket.title}

Full Conversation History:
{conversation_text}

Generate the best strategic draft reply for the AGENT.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return response.content
