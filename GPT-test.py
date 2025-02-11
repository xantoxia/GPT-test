import streamlit as st
import openai
import os

# 读取 OpenRouter API Key
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# 设置 OpenRouter API 客户端
client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"  # OpenRouter API 端点
)

# Streamlit 页面配置
st.set_page_config(page_title="ChatGPT Plus 模拟", page_icon="🤖", layout="wide")
st.title("💬 ChatGPT Plus 模拟 - OpenRouter API")

# 聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
user_input = st.chat_input("请输入你的问题...")
if user_input:
    # 显示用户输入
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 发送请求到 OpenRouter
    response = client.chat.completions.create(
        model="openai/gpt-4-turbo",  # 使用 OpenRouter 支持的模型
        messages=st.session_state.messages
    )

    # 打印 API 响应以调试
    st.write(response)  # 查看返回的结构

    # 获取 AI 回复
    if 'choices' in response and len(response['choices']) > 0:
        reply = response['choices'][0]['text']  # 假设使用 'text' 字段
        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.error("未能获取有效的回复，检查 API 响应格式。")
