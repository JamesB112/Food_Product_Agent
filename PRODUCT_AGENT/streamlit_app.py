import streamlit as st
from agent import root_agent  # Assuming your agent code is in agent_module.py

# --- Streamlit page configuration ---
st.set_page_config(page_title="Food Health Assistant", layout="wide")
st.title("🍎 Interactive Food Health Assistant")

# --- Initialize session state ---
if "history" not in st.session_state:
    st.session_state.history = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {}

# --- User input ---
st.sidebar.header("Input Options")
user_input = st.sidebar.text_input("Enter product(s) or ask a question:")

# --- Submit button ---
if st.sidebar.button("Analyze / Ask") and user_input.strip():
    # Call the agent
    try:
        # Pass existing state so agent can reuse previous results
        response = root_agent.run(user_input, state=st.session_state.agent_state)
        
        # Store conversation history
        st.session_state.history.append({"user": user_input, "agent": response})
    except Exception as e:
        st.error(f"Error running agent: {e}")

# --- Display conversation ---
st.header("Conversation")
for chat in st.session_state.history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Assistant:** {chat['agent']}")

# --- Optionally clear history ---
if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.session_state.agent_state = {}
    st.experimental_rerun()
