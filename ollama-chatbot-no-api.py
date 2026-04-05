# importing the necessary libraries and modules
import streamlit as st
import ollama

# setting up the page configuration
st.set_page_config(page_title="Local AI Chatbot (No API KEY)", layout='centered')

# setup the title
st.title("Local AI chatbot (No API Key)")
st.caption("Runs on your laptop using Ollama Models")

# Sidebar controls to keep the model simple for the beginner level
with st.sidebar:
    st.header("Application Setting:")

    # Dropdown or model options - Sirf ye do models
    model_name = st.selectbox(
        "Choose a model:",
        options=["llama3.1:8b", "llama3.2:1b"],
        index=0
    )

    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens (response length)", 64, 1024, 256, 64)

    st.markdown("---")

    st.subheader("Important: Pull the model first in your terminal if you have not")
    st.code(f"ollama pull {model_name}", language="bash")

    st.write('If you want to pull all the models:')
    st.code(
        "ollama pull llama3.1:8b\n"
        "ollama pull llama3.2:1b",
        language="bash"
    )

    st.markdown("---")
    st.write("Quick test in terminal:")
    st.code("ollama list", language="bash")

# storing the chat history in streamlit session (persists across reruns)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI Assistant to answer many different questions accurately and precisely."}
    ]

for msg in st.session_state.messages:
    if msg['role'] == 'system':
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# chat input
user_text = st.chat_input("Please type your question here...")

# define the function to get the response from llm
def generate_response_stream(messages, model, temp, max_tokens):
    """
    Stream tokens from ollama model so the UI feels like ChatGPT / Copilot
    """
    stream = ollama.chat(
        model=model, messages=messages, stream=True,
        options={
            "temperature": temp,
            "num_predict": max_tokens
        }
    )
    for chunk in stream:
        yield chunk['message']['content']

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message('user'):
        st.markdown(user_text)

    # generate + stream assistant response
    with st.chat_message('assistant'):
        try:
            response_text = st.write_stream(
                generate_response_stream(
                    messages=st.session_state.messages,
                    model=model_name,
                    temp=temperature,
                    max_tokens=max_tokens
                )
            )
        except Exception as e:
            st.error('Could not connect to Ollama or run the selected model.')
            st.info(
                "Fix checklist:\n"
                "1) Make sure that Ollama is installed and running\n"
                "2) Run the pull command shown in the sidebar\n"
                "3) Verify available models with: `ollama list`\n"
                "4) try: `ollama run llama3.1:8b` or `ollama run llama3.2:1b`"
            )
            st.exception(e)
            response_text = ""

    # saving assistants response to conversation history
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# Clear chat button
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful AI Assistant to answer many different questions accurately and precisely."}
        ]
        st.rerun()
