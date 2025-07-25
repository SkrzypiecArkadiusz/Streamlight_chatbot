
import streamlit as st
from openai import OpenAI
class Chatbot:
    def __init__(self, api_key):
        self.client = OpenAI(api_key= st.secrets['openai_api_key'])
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = 'gpt-4'

        if "messages" not in st.session_state:
            st.session_state.messages = []

    def model_comparison(selfself, prompt):
        compare_model = None
        base_model = st.session_state["openai_model"]
        cleaned_prompt = prompt

        if prompt.startswith("[compare to '"):
            parts = prompt.split("'")
            if len(parts) > 1:
                compare_model = parts[1]
            cleaned_prompt = prompt.split("]", 1)[-1].strip()
        return compare_model, cleaned_prompt

    def add_message(self, role,content):
        st.session_state.messages.append({"role": role, "content": content})

    def run(self):
        st.title("Streamlit ChatbotAI")

        with st.sidebar:
            base_model = st.selectbox("Base model", ["gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
                                      index=["gpt-4", "gpt-3.5-turbo", "gpt-3.5"].index(st.session_state.openai_model))
            compare_model = st.selectbox("Compare with", ["none", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"])

        st.session_state.openai_model = base_model

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask something or use: [compare to 'gpt-3.5-turbo'], or select models in sidebar")

        if prompt:
            cleaned_prompt, parsed_compare = self.parse_compare_model(prompt)
            effective_compare = compare_model if compare_model != "none" else parsed_compare

            self.add_message("user", prompt)

            if effective_compare:
                with st.chat_message("assistant"):
                    st.markdown(f"Comparing models: **{base_model}** vs **{effective_compare}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"🤖 **{base_model}**:")
                        stream1 = self.client.chat.completions.create(
                            model=base_model,
                            messages=[{"role": "user", "content": cleaned_prompt}],
                            stream=True,
                        )
                        response1 = st.write_stream(stream1)
                    with col2:
                        st.markdown(f"🤖 **{effective_compare}**:")
                        stream2 = self.client.chat.completions.create(
                            model=compare_model,
                            messages=[{"role": "user", "content": cleaned_prompt}],
                            stream=True,
                        )
                        response2 = st.write_stream(stream2)

                combined = f"**{base_model}**: {response1}\n\n**{effective_compare}**: {response2}"
                self.add_message("assistant", combined)
            else:
                messages = st.session_state.messages.copy()
                response = self.get_completion(base_model, messages)
                with st.chat_message("assistant"):
                    st.markdown(response)
                self.add_message("assistant", response)