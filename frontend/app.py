import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Support System", layout="centered")

# -----------------------
# Session State
# -----------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None

if "agent_draft" not in st.session_state:
    st.session_state.agent_draft = ""


# -----------------------
# Helper Functions
# -----------------------
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


def status_badge(status):
    colors = {
        "OPEN": "blue",
        "PENDING_AGENT": "red",
        "WAITING_FOR_USER": "orange",
        "AUTO_RESOLVED": "green",
        "CLOSED": "gray"
    }
    color = colors.get(status, "black")
    return f"<span style='color:{color}; font-weight:bold'>{status}</span>"


# -----------------------
# UI Start
# -----------------------
st.title("🤖 AI Customer Support System")

# =========================
# NOT LOGGED IN
# =========================
if st.session_state.token is None:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            response = login_request(email, password)
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Create Account")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register"):
            response = register_request(email, password)
            if response.status_code in [200, 201]:
                st.success("Account created. Please login.")
            else:
                st.error("Registration failed.")

# =========================
# LOGGED IN
# =========================
else:

    col1, col2 = st.columns([8, 2])

    with col1:
        st.success(f"Logged in as {st.session_state.role}")

    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.selected_ticket = None
            st.session_state.agent_draft = ""
            st.rerun()

    st.divider()

    # =====================================
    # USER DASHBOARD
    # =====================================
    if st.session_state.role == "USER":

        st.header("User Dashboard")

        # Create Ticket
        st.subheader("Create New Ticket")
        title = st.text_input("Ticket Title")
        description = st.text_area("Describe your issue")

        if st.button("Submit Ticket"):
            response = requests.post(
                f"{BASE_URL}/tickets/",
                headers=auth_headers(),
                json={"title": title, "description": description}
            )
            if response.status_code == 200:
                st.success("Ticket created!")
                st.rerun()
            else:
                st.error("Failed to create ticket")

        st.divider()

        # My Tickets
        st.subheader("My Tickets")

        response = requests.get(
            f"{BASE_URL}/tickets/my",
            headers=auth_headers()
        )

        if response.status_code == 200:
            tickets = response.json()

            for ticket in tickets:
                st.write(f"### {ticket['title']}")
                st.markdown(
                    f"Status: {status_badge(ticket['status'])}",
                    unsafe_allow_html=True
                )

                if st.button(f"Open Ticket {ticket['id']}"):
                    st.session_state.selected_ticket = ticket["id"]
                    st.rerun()

                st.write("---")

        # Ticket Conversation
        if st.session_state.selected_ticket:

            ticket_id = st.session_state.selected_ticket
            st.subheader(f"Conversation (Ticket {ticket_id})")

            msg_response = requests.get(
                f"{BASE_URL}/tickets/{ticket_id}/messages",
                headers=auth_headers()
            )

            if msg_response.status_code == 200:
                messages = msg_response.json()

                for msg in messages:
                    st.write(f"**{msg['sender_role']}**: {msg['message']}")

                st.divider()

                reply = st.text_area("Reply")

                if st.button("Send Reply"):
                    requests.post(
                        f"{BASE_URL}/tickets/{ticket_id}/reply",
                        headers=auth_headers(),
                        json={"message": reply}
                    )
                    st.success("Reply sent")
                    st.rerun()

                if st.button("Close Ticket"):
                    requests.post(
                        f"{BASE_URL}/tickets/{ticket_id}/close",
                        headers=auth_headers()
                    )
                    st.success("Ticket closed")
                    st.session_state.selected_ticket = None
                    st.rerun()

    # =====================================
    # AGENT DASHBOARD
    # =====================================
    elif st.session_state.role == "AGENT":

        st.header("Agent Dashboard")

        response = requests.get(
            f"{BASE_URL}/tickets/agent/pending",
            headers=auth_headers()
        )

        if response.status_code == 200:
            tickets = response.json()

            # Metrics
            total_pending = len(tickets)
            high_priority = len(
                [t for t in tickets if t["priority"] == "HIGH"]
            )

            col1, col2 = st.columns(2)
            col1.metric("Pending Tickets", total_pending)
            col2.metric("High Priority", high_priority)

            st.divider()

            for ticket in tickets:
                st.write(f"### {ticket['title']}")
                st.markdown(
                    f"Status: {status_badge(ticket['status'])}",
                    unsafe_allow_html=True
                )
                st.write(f"Priority: {ticket['priority']}")
                st.write(f"Category: {ticket['category']}")

                # AI Metadata
                if ticket.get("ai_metadata"):
                    meta = ticket["ai_metadata"]
                    st.write(f"Sentiment: {meta.get('sentiment')}")
                    st.write(f"Risk: {meta.get('risk')}")
                    st.write(
                        f"Confidence: {round(meta.get('confidence', 0), 2)}"
                    )

                if st.button(f"Open Ticket {ticket['id']}"):
                    st.session_state.selected_ticket = ticket["id"]
                    st.rerun()

                st.write("---")

        # Ticket Conversation (Agent)
        if st.session_state.selected_ticket:

            ticket_id = st.session_state.selected_ticket
            st.subheader(f"Conversation (Ticket {ticket_id})")

            msg_response = requests.get(
                f"{BASE_URL}/tickets/{ticket_id}/messages",
                headers=auth_headers()
            )

            if msg_response.status_code == 200:
                messages = msg_response.json()

                for msg in messages:
                    st.write(f"**{msg['sender_role']}**: {msg['message']}")

                st.divider()

                # Generate AI Draft
                if st.button("Generate AI Draft"):
                    draft_response = requests.post(
                        f"{BASE_URL}/tickets/{ticket_id}/generate-draft",
                        headers=auth_headers()
                    )
                    if draft_response.status_code == 200:
                        st.session_state.agent_draft = draft_response.json()["draft"]

                draft_text = st.text_area(
                    "Agent Reply",
                    value=st.session_state.agent_draft
                )

                if st.button("Send Reply"):
                    requests.post(
                        f"{BASE_URL}/tickets/{ticket_id}/reply",
                        headers=auth_headers(),
                        json={"message": draft_text}
                    )
                    st.session_state.agent_draft = ""
                    st.success("Reply sent")
                    st.rerun()
