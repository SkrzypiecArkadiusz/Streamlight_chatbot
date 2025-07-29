'''
Stworzyć aplikację Python, korzystającą z biblioteki Streamlit, która jest czatem z LLM na Azure.

Do tego będą potrzebne dostępy do Azure AI Foundry.

Tam będzie dostęp do ChatGPT, który może pomóc w kodowaniu, ale w zasadzie to krytyczne nie jest to konieczne,
w przykładach Streamlit jest wręcz taki kod.

Celem jest uruchomienie chata lokalnie i poznanie jak w praktyce wygląda API LLM.

Rozszerzeniem zadania może być np. dodanie porównywania odpowiedzi dwóch modeli.

git config --global user.name "Arkadiusz Skrzypiec"
git config --global user.email "arkadiusz.skrzypiec@bluesoft.com"

'''



import streamlit as st
from openai import OpenAI
from openai import AzureOpenAI
import re

AZURE_OPENAI_API_KEY= st.secrets["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT= st.secrets["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT= st.secrets["AZURE_OPENAI_DEPLOYMENT"]
AZURE_OPENAI_API_VERSION=st.secrets["AZURE_OPENAI_API_VERSION"]


st.title("Streamlit ChatbotAI")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client2 = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

def Add_Message_Log(content, role="assistant"):
    st.session_state.messages.append({
        "role": role,
        "content": content
    })


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
        models = st.selectbox("Base model", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4.1","none"], index=0,label_visibility="collapsed")
        models_compare = st.selectbox("Compare with", ["none", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4.1"], index=0,label_visibility="collapsed")
        azure_models = st.selectbox("Azure models", ["none", "gpt-4o","gpt-4o-mini"])

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
                    if azure_models == "gpt-4o":
                        print ("right step----------------------------------------------------------------------------------------------------------------------------------------------")
                        st.markdown(f"🤖 **Model 1** Azure ({base_model}):")
                        response1 = client2.chat.completions.create(
                            model=AZURE_OPENAI_DEPLOYMENT,
                            messages=[{"role": "user", "content": cleaned_prompt+"remember you are azure model"}],
                            max_tokens=500,
                            temperature=1.0,
                            top_p=1.0,
                        )
                        content1 = response1.choices[0].message.content
                        st.write(content1)
                    else:
                        st.markdown(f"🤖 **Model 1** ({base_model}):")
                        stream1 = client.chat.completions.create(
                            model=base_model,
                            messages=[{"role": "user", "content": cleaned_prompt+"you are openai model"}],
                            stream=True,
                        )

                        response1 = st.write_stream(stream1)

                with col2:
                    st.markdown(f"🤖 **Model 2** ({compare_model}):")
                    stream2 = client.chat.completions.create(
                        model=compare_model,
                        messages=[{"role": "user", "content": cleaned_prompt+"you are openai model"}],
                        stream=True,
                    )
                    response2 = st.write_stream(stream2)

            st.session_state.messages.append(
                {"role": "assistant", "content": f"**{base_model}**: {response1}\n\n**{compare_model}**: {response2}"}
            )
        elif models != "none":
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=base_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
        elif azure_models != "none":
            AZURE_OPENAI_DEPLOYMENT = azure_models
            st.markdown(f"🤖 **Model 1** Azure ({base_model}):")
            response1 = client2.chat.completions.create(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=[
                        {"role": "system",
                         "content": "Do not mention you are deployed on Azure unless explicitly asked about your deployment location."},
                        {"role": "user", "content": cleaned_prompt+"dont use letter e in eny way in your response"}
                    ],
                    max_tokens=450,
                    temperature=1.0,
                    top_p=1.0,
            )
            content1 = response1.choices[0].message.content
            st.write(content1)
            Add_Message_Log(f"**{base_model}**: {content1}")


if models != "none":
     st.session_state["openai_model"] = models
elif azure_models != "none":
     st.session_state["openai_model"] = azure_models



