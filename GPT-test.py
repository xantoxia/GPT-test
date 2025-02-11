import streamlit as st
import openai
import fitz  # PyMuPDF 解析 PDF
import docx  # 解析 Word 文档
from PIL import Image
import io
import os


# 设置 OpenAI API Key
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "你是一个智能助手，能够处理文本、图片和文档分析。"}]

# Streamlit 界面
st.title("📢 ChatGPT Plus 模拟版 (Streamlit + OpenAI API)")

# **1️⃣ 上传图片**
uploaded_image = st.file_uploader("📸 上传图片 (GPT-4-vision 解析)", type=["jpg", "jpeg", "png"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="已上传图片", use_column_width=True)

    if st.button("分析图片"):
        st.write("⏳ GPT-4 正在分析图片...")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=st.session_state.messages + [{"role": "user", "content": "请分析这张图片"}],
            temperature=0.5,
            max_tokens=500,
            n=1,
            stream=False,
            logit_bias={},
            functions=[],
            function_call="auto",
            tool_choice="auto",
            image={"mime_type": "image/png", "data": img_bytes}
        )
        answer = response["choices"][0]["message"]["content"]
        st.write(answer)

# **2️⃣ 上传文档**
uploaded_file = st.file_uploader("📄 上传文档 (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])

def extract_text_from_file(file):
    """ 解析上传的文档内容 """
    if file.type == "application/pdf":
        pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in pdf_reader])
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        text = None
    return text

if uploaded_file:
    file_text = extract_text_from_file(uploaded_file)
    if file_text:
        st.text_area("📖 文件内容预览", file_text[:1000] + "..." if len(file_text) > 1000 else file_text)
        if st.button("分析文档"):
            st.write("⏳ GPT-4 正在分析文档...")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.messages + [{"role": "user", "content": f"请分析以下文档内容：\n{file_text}"}],
                temperature=0.5,
                max_tokens=1000
            )
            answer = response["choices"][0]["message"]["content"]
            st.write(answer)

# **3️⃣ 文字聊天**
st.subheader("💬 文字聊天")

# 显示聊天记录
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**👤 你:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 ChatGPT:** {msg['content']}")

# 用户输入
user_input = st.text_area("✍️ 请输入你的问题", "")

if st.button("发送"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 显示 GPT-4 响应
        with st.spinner("ChatGPT 正在思考..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.messages,
                temperature=0.7,
                stream=True
            )

            full_response = ""
            message_placeholder = st.empty()

            # **流式显示回答**
            for chunk in response:
                if "choices" in chunk:
                    full_response += chunk["choices"][0]["delta"].get("content", "")
                    message_placeholder.write(full_response)

            # 记录到对话历史
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.warning("请输入问题后再发送！")

# **4️⃣ 清空聊天记录**
if st.button("🗑️ 清空聊天记录"):
    st.session_state.messages = [{"role": "system", "content": "你是一个智能助手，能够处理文本、图片和文档分析。"}]
    st.success("聊天记录已清空！")

