import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)


def generate_auto_reply(title: str, description: str):
    system_prompt = """
You are a professional customer support agent.

Write a polite, clear, short resolution response.
Do not mention internal systems.
Keep it helpful and concise.
"""

    user_prompt = f"""
Title: {title}
Description: {description}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return response.content

def generate_agent_draft(ticket, messages):
    """
    Generates AI draft for agent using conversation history.
    """

    conversation_text = "\n".join(
        [f"{msg.sender_role}: {msg.message}" for msg in messages]
    )

    system_prompt = """
You are an expert customer support assistant helping a human agent.

Generate a professional reply draft.
Be clear, polite, and helpful.
Do NOT mention you are AI.
Keep it concise.
"""

    user_prompt = f"""
Ticket Title: {ticket.title}

Conversation:
{conversation_text}

Write a reply draft for the AGENT.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return response.content
