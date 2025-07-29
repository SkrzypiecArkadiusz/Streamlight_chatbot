import os
from openai import AzureOpenAI
import streamlit as st
endpoint = "https://bluesoft-ai-4gpt.openai.azure.com/"
model_name = "gpt-4o"
deployment = "gpt-4"

subscription_key = st.secrets["AZURE_OPENAI_API_KEY"]
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see? 2 sentences",
        }
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=deployment
)

print(response.choices[0].message.content)