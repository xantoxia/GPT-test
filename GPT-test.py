import streamlit as st
import openai
import os
from PIL import Image
import fitz  # PyMuPDF for PDF handling
import io
import docx

# 设置 OpenAI API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 推荐使用 Streamlit Secrets 存储 API Key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Streamlit 页面配置
st.set_page_config(page_title="ChatGPT Plus 模拟", page_icon="🤖", layout="wide")
st.title("💬 ChatGPT Plus 模拟 - Streamlit + OpenAI API")

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

    # 发送请求到 OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.messages
    )

    # 获取 GPT-4 回复
    reply = response.choices[0].message.content
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# 文件上传处理
uploaded_file = st.file_uploader("📎 上传文件（支持 PDF, Word, 图片）", type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file:
    file_type = uploaded_file.type
    content = ""

    if "pdf" in file_type:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            content += page.get_text("text") + "\n"
    
    elif "word" in file_type or "docx" in file_type:
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            content += para.text + "\n"

    elif "image" in file_type:
        image = Image.open(uploaded_file)
        st.image(image, caption="上传的图片", use_column_width=True)
        st.write("⚠️ 目前 OpenAI API 还不支持直接解析图片内容。")

    if content:
        st.subheader("📄 解析出的文本内容")
        st.text_area("文本内容", content, height=200)

        # 让 GPT-4 总结文件内容
        with st.spinner("AI 正在分析内容..."):
            summary_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "你是一个精通文本摘要的 AI，请总结以下内容。"},
                          {"role": "user", "content": content}]
            )
            summary = summary_response.choices[0].message.content
            st.subheader("📌 AI 总结")
            st.markdown(summary)
