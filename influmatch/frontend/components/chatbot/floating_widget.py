"""Floating ARIA Chatbot Widget"""
import uuid
import streamlit as st
from ...utils.api_client import api_post
from ...utils.i18n import t

def render_chatbot():
    if not st.session_state.get("chat_open", False):
        return

    # Persist session_id across reruns — one UUID per browser session
    if "chat_session_id" not in st.session_state:
        st.session_state["chat_session_id"] = str(uuid.uuid4())

    lang       = st.session_state.get("lang", "ar")
    session_id = st.session_state["chat_session_id"]
    user_id    = st.session_state.get("user_id")   # may be None for unauthenticated
    msgs       = st.session_state.get("chat_messages", [])

    with st.expander("🤖 ARIA AI Assistant", expanded=True):
        # Message history
        chat_container = st.container()
        with chat_container:
            for msg in msgs[-20:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin:0.4rem 0">
                        <div style="background:rgba(124,58,237,0.25);padding:0.5rem 0.9rem;
                                    border-radius:12px 12px 0 12px;max-width:80%;font-size:0.88rem">
                            {content}
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-start;margin:0.4rem 0">
                        <div style="background:rgba(30,41,59,0.9);border:1px solid rgba(148,163,184,0.15);
                                    padding:0.5rem 0.9rem;border-radius:12px 12px 12px 0;
                                    max-width:80%;font-size:0.88rem">
                            🤖 {content}
                        </div>
                    </div>""", unsafe_allow_html=True)

        # Input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                t("type_message"), key="chatbot_input",
                label_visibility="collapsed",
                placeholder="اسألني أي شيء... / Ask me anything..."
            )
        with col2:
            send = st.button(t("send"), key="chatbot_send")

        if send and user_input.strip():
            msgs.append({"role": "user", "content": user_input})
            st.session_state["chat_messages"] = msgs
            with st.spinner("🤖 ARIA تفكر... / Thinking..."):
                status_code, resp = api_post(
                    "/api/chatbot/chat",
                    json={
                        "message"   : user_input,
                        "session_id": session_id,
                        "user_id"   : user_id,
                        "language"  : lang,
                    },
                    timeout=60
                )
            if status_code == 200:
                reply = resp.get("response", "...")
            else:
                detail = resp.get("detail", "") if isinstance(resp, dict) else ""
                reply = f"عذراً، حدث خطأ ({status_code}). / Error ({status_code}): {detail}" if lang == "ar" else f"Error ({status_code}): {detail}"
            msgs.append({"role": "assistant", "content": reply})
            st.session_state["chat_messages"] = msgs
            st.rerun()

        if st.button("🗑️ Clear / مسح", key="chatbot_clear"):
            st.session_state["chat_messages"] = []
            # New session after clearing so history doesn't bleed back from DB
            st.session_state["chat_session_id"] = str(uuid.uuid4())
            st.rerun()
