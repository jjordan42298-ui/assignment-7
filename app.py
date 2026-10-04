import streamlit as st
from groq import Groq
import json
from tools import dispatch_tool
from agent import run_agent_loop

st.set_page_config(page_title="Room Manager", page_icon="🏫", layout="wide")
st.title("🏫 Campus Calendar Assistant")

# Validate secret key configurations
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing `.streamlit/secrets.toml`. Please specify your GROQ_API_KEY.")
    st.stop()

if "groq_client" not in st.session_state:
    st.session_state.groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialize layout variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly campus assistant. Assist users with scheduling parameters, room queries, or building hours."}
    ]
if "tool_logs" not in st.session_state:
    st.session_state.tool_logs = []
if "active_pending_call" not in st.session_state:
    st.session_state.active_pending_call = None

# Render Visible History Cards safely handling both dictionaries and objects
for msg in st.session_state.messages:
    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
    content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
    
    if role in ["user", "assistant"] and content:
        with st.chat_message(role):
            st.write(content)

user_input = st.chat_input("Ask about open rooms or place a reservation...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# SAFEGUARD: Keep looping automatically in the background until a text answer drops
while len(st.session_state.messages) > 1 and st.session_state.active_pending_call is None:
    last_msg = st.session_state.messages[-1]
    last_role = last_msg.get("role") if isinstance(last_msg, dict) else getattr(last_msg, "role", None)
    
    # Break out if the assistant already successfully answered with text
    if last_role == "assistant":
        break
        
    with st.spinner("Analyzing scheduling metadata..."):
        ans_msg, tool_calls = run_agent_loop(st.session_state.groq_client, st.session_state.messages)
        
        if tool_calls:
            # Trap state changes for safety confirmation step
            booking_actions = [c for c in tool_calls if c.function.name == "book_room"]
            if booking_actions:
                st.session_state.active_pending_call = booking_actions[0]
                st.rerun()
            else:
                # Automate read-only queries cleanly and continue the loop automatically
                for call in tool_calls:
                    res = dispatch_tool(call.function.name, call.function.arguments)
                    st.session_state.tool_logs.append({"tool": call.function.name, "args": call.function.arguments, "result": res})
                    st.session_state.messages.append({"role": "tool", "tool_call_id": call.id, "name": call.function.name, "content": res})
                continue
        elif ans_msg and ans_msg.content:
            st.session_state.messages.append({"role": "assistant", "content": ans_msg.content})
            st.rerun()
        else:
            break

# Render User Booking Authorization Interceptor Confirmation Block
if st.session_state.active_pending_call:
    pending = st.session_state.active_pending_call
    try:
        args = json.loads(pending.function.arguments)
        day_val, rm_val, name_val = args.get("day", "?"), args.get("room", "?"), args.get("name", "?")
    except:
        day_val, rm_val, name_val = "Error", "Error", "Error"
        
    st.warning(f"⚠️ **Authorization Form**: Confirm reservation request of Room **{rm_val}** on **{day_val}** under the profile **'{name_val}'**?")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirm and Book Room", type="primary"):
            exec_res = dispatch_tool(pending.function.name, pending.function.arguments)
            st.session_state.tool_logs.append({"tool": pending.function.name, "args": pending.function.arguments, "result": exec_res})
            st.session_state.messages.append({"role": "tool", "tool_call_id": pending.id, "name": pending.function.name, "content": exec_res})
            st.session_state.active_pending_call = None
            st.rerun()
    with c2:
        if st.button("Cancel Actions"):
            reject_str = "Error: Operation cancelled by user confirmation override."
            st.session_state.messages.append({"role": "tool", "tool_call_id": pending.id, "name": pending.function.name, "content": reject_str})
            st.session_state.active_pending_call = None
            st.rerun()

# Side Navigation Log Panel Drawer
with st.sidebar:
    st.subheader("🪵 Audit Tool Logs")
    if not st.session_state.tool_logs:
        st.write("No items tracked.")
    for idx, log in enumerate(reversed(st.session_state.tool_logs)):
        with st.expander(f"Call #{len(st.session_state.tool_logs)-idx}: {log['tool']}"):
            st.caption("Arguments:")
            st.code(log["args"], language="json")
            st.caption("Response Payload:")
            st.code(log["result"], language="text")
