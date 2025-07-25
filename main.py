'''
Stworzyć aplikację Python, korzystającą z biblioteki Streamlit, która jest czatem z LLM na Azure.

Do tego będą potrzebne dostępy do Azure AI Foundry.

Tam będzie dostęp do ChatGPT, który może pomóc w kodowaniu, ale w zasadzie to krytyczne nie jest to konieczne,
w przykładach Streamlit jest wręcz taki kod.

Celem jest uruchomienie chata lokalnie i poznanie jak w praktyce wygląda API LLM.

Rozszerzeniem zadania może być np. dodanie porównywania odpowiedzi dwóch modeli.


'''
import streamlit as st
from openai import OpenAI
import re



st.title("Streamlit ChatbotAI")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# base model gpt 4
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = 'gpt-4o-mini'

if "messages" not in st.session_state:
    st.session_state.messages = []



for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask something or use: [compare to 'gpt-3.5-turbo'], or use sidebar :)")
with st.sidebar:
        st.markdown("Model Selection")
        models = st.selectbox("Base model", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4.1"], index=0,label_visibility="collapsed")
        models_compare = st.selectbox("Compare with", ["none", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4.1"], index=0,label_visibility="collapsed")

if prompt:
        compare_model = None
        base_model = st.session_state["openai_model"]
        cleaned_prompt = prompt

        if prompt.startswith("[compare to '"):
            parts = prompt.split("'")
            if len(parts) > 1:
                compare_model = parts[1]
            cleaned_prompt = prompt.split("]", 1)[-1].strip()


        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        if models_compare != "none":
            compare_model = models_compare
        if compare_model:

            with st.chat_message("assistant"):
                st.markdown(f"Comparing models:")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"🤖 **Model 1** ({base_model}):")
                    stream1 = client.chat.completions.create(
                        model=base_model,
                        messages=[{"role": "user", "content": cleaned_prompt}],
                        stream=True,
                    )
                    response1 = st.write_stream(stream1)

                with col2:
                    st.markdown(f"🤖 **Model 2** ({compare_model}):")
                    stream2 = client.chat.completions.create(
                        model=compare_model,
                        messages=[{"role": "user", "content": cleaned_prompt}],
                        stream=True,
                    )
                    response2 = st.write_stream(stream2)

            st.session_state.messages.append(
                {"role": "assistant", "content": f"**{base_model}**: {response1}\n\n**{compare_model}**: {response2}"}
            )

        else:
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=base_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

st.session_state["openai_model"] = models


