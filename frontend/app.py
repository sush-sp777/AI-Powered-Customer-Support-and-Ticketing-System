import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SupportIQ",
    page_icon="🤖",
    layout="centered"
)

# =====================================================
# SESSION STATE
# =====================================================
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None

if "agent_draft" not in st.session_state:
    st.session_state.agent_draft = ""

# =====================================================
# API FUNCTIONS
# =====================================================
def register_request(email, password):
    return requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password}
    )

def login_request(email, password):
    return requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# =====================================================
# UI HELPERS
# =====================================================
def status_badge(status):
    colors = {
        "OPEN": "#1f77b4",
        "PENDING_AGENT": "#d62728",
        "WAITING_FOR_USER": "#ff7f0e",
        "AUTO_RESOLVED": "#2ca02c",
        "CLOSED": "#7f7f7f"
    }
    return f"<span style='color:{colors.get(status,'black')};font-weight:600'>{status}</span>"

def render_message(role, message):
    if role == "USER":
        label = "User"
    elif role == "AGENT":
        label = "Agent"
    else:
        label = "AI"

    st.markdown(f"**{label}:** {message}")

def urgency_score(ticket):
    score = 0

    if ticket.get("priority") == "HIGH":
        score += 5

    meta = ticket.get("ai_metadata") or {}
    sentiment = str(meta.get("sentiment","")).lower()
    confidence = meta.get("confidence",0)

    if sentiment == "negative":
        score += 3 * confidence

    return score

def escalation_reason(ticket):
    meta = ticket.get("ai_metadata") or {}
    sentiment = meta.get("sentiment")
    risk = meta.get("risk")
    priority = ticket.get("priority")

    reasons = []
    if priority == "HIGH":
        reasons.append("high priority")
    if sentiment == "negative":
        reasons.append("negative sentiment")
    if risk == "HIGH":
        reasons.append("risk detected")

    if reasons:
        return "Escalation: " + ", ".join(reasons)
    return None

# =====================================================
# HEADER
# =====================================================
st.markdown("<h2 style='text-align:center;'>SupportIQ — AI Assisted Helpdesk</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Internal Support Dashboard</p>", unsafe_allow_html=True)
st.divider()

# =====================================================
# NOT LOGGED IN
# =====================================================
if st.session_state.token is None:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            r = login_request(email, password)
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Create Account", use_container_width=True):
            r = register_request(email, password)
            if r.status_code in [200,201]:
                st.success("Account created. Please login.")
            else:
                st.error("Registration failed")

# =====================================================
# LOGGED IN
# =====================================================
else:

    col1, col2 = st.columns([8,2])

    with col1:
        st.success(f"Logged in as {st.session_state.role}")

    with col2:
        if st.button("Logout"):
            st.session_state.token=None
            st.session_state.role=None
            st.session_state.selected_ticket=None
            st.session_state.agent_draft=""
            st.rerun()

    st.divider()

    # =====================================================
    # USER DASHBOARD
    # =====================================================
    if st.session_state.role == "USER":

        st.subheader("Create Ticket")
        title = st.text_input("Title")
        desc = st.text_area("Describe issue")

        if st.button("Submit"):
            r = requests.post(f"{BASE_URL}/tickets/",headers=auth_headers(),
                              json={"title":title,"description":desc})
            if r.status_code==200:
                st.success("Ticket created")
                st.rerun()

        st.divider()
        st.subheader("My Tickets")

        r = requests.get(f"{BASE_URL}/tickets/my",headers=auth_headers())
        if r.status_code==200:
            tickets=r.json()

            for t in tickets:
                st.markdown(f"**{t['title']}** — {status_badge(t['status'])}",unsafe_allow_html=True)

                if st.button(f"Open #{t['id']}"):
                    st.session_state.selected_ticket=t["id"]
                    st.rerun()

                st.markdown("---")

        if st.session_state.selected_ticket:
            tid=st.session_state.selected_ticket
            st.subheader(f"Conversation #{tid}")

            msgs=requests.get(f"{BASE_URL}/tickets/{tid}/messages",headers=auth_headers()).json()
            for m in msgs:
                render_message(m["sender_role"],m["message"])

            reply=st.text_area("Reply")

            if st.button("Send"):
                requests.post(f"{BASE_URL}/tickets/{tid}/reply",headers=auth_headers(),json={"message":reply})
                st.rerun()

            if st.button("Close Ticket"):
                requests.post(f"{BASE_URL}/tickets/{tid}/close",headers=auth_headers())
                st.session_state.selected_ticket=None
                st.rerun()

    # =====================================================
    # AGENT DASHBOARD
    # =====================================================
    else:

        st.subheader("Pending Tickets")

        r=requests.get(f"{BASE_URL}/tickets/agent/pending",headers=auth_headers())
        if r.status_code==200:
            tickets=r.json()

            tickets.sort(key=urgency_score,reverse=True)

            for t in tickets:

                meta=t.get("ai_metadata") or {}
                sentiment=meta.get("sentiment","-")
                confidence=round(meta.get("confidence",0),2)

                st.markdown(f"**{t['title']}** — {status_badge(t['status'])}",unsafe_allow_html=True)
                st.write(f"Priority: {t['priority']} | Category: {t['category']} | Sentiment: {sentiment} ({confidence})")

                reason=escalation_reason(t)
                if reason:
                    st.warning(reason)

                if st.button(f"Open #{t['id']}"):
                    st.session_state.selected_ticket=t["id"]
                    st.rerun()

                st.markdown("---")

        if st.session_state.selected_ticket:
            tid=st.session_state.selected_ticket
            st.subheader(f"Conversation #{tid}")

            msgs=requests.get(f"{BASE_URL}/tickets/{tid}/messages",headers=auth_headers()).json()
            for m in msgs:
                render_message(m["sender_role"],m["message"])

            if st.button("Generate AI Draft"):
                d=requests.post(f"{BASE_URL}/tickets/{tid}/generate-draft",headers=auth_headers())
                if d.status_code==200:
                    st.session_state.agent_draft=d.json()["draft"]

            draft=st.text_area("Agent Reply",value=st.session_state.agent_draft,height=150)

            if st.button("Send Reply"):
                requests.post(f"{BASE_URL}/tickets/{tid}/reply",headers=auth_headers(),json={"message":draft})
                st.session_state.agent_draft=""
                st.rerun()
