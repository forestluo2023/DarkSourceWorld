import streamlit as st
import time
from google import genai
import io

# 尝试导入 docx
try:
    import docx
except ImportError:
    docx = None

st.set_page_config(page_title="Gemini AI小说创作台 V13.0 (多文件版)", layout="wide")

# --- 初始化 ---
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

# --- 辅助函数：批量读取文件 ---
def read_all_files(uploaded_files):
    if not uploaded_files: return ""
    
    # 如果是单文件（没开启多选时的兼容），转为列表
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
        
    all_content = []
    for file in uploaded_files:
        try:
            content = ""
            if file.name.endswith('.docx'):
                if docx:
                    doc = docx.Document(file)
                    content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                content = file.getvalue().decode("utf-8")
            
            if content:
                all_content.append(f"--- 文件名：{file.name} ---\n{content}\n")
        except Exception:
            continue
            
    return "\n".join(all_content)

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY: st.success("API Key 已就绪")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    # 开启 accept_multiple_files=True
    uploaded_files = st.file_uploader(
        "上传多份资料 (TXT/MD/DOCX)", 
        type=['txt', 'md', 'docx'], 
        key='uploaded_style_files',
        accept_multiple_files=True 
    )
    if uploaded_files: st.info(f"已加载 {len(uploaded_files)} 份文件")

# --- 1. 资料库问答 ---
st.header("1️⃣ 资料库问答 (真实AI)")
col_q, col_btn = st.columns([5, 1])
with col_q: user_query = st.text_input("输入问题...", key="query_input")
with col_btn: 
    st.write(""); st.write("")
    ask_btn = st.button("提问 🤖")

if ask_btn and user_query:
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先输入 API Key")
    elif not uploaded_files:
        st.warning("⚠️ 请先上传资料库文件")
    else:
        try:
            doc_content = read_all_files(uploaded_files)
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            with st.spinner("🤖 正在查阅所有资料..."):
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=f"参考文档：\n{doc_content[:20000]}\n用户问题：{user_query}"
                )
                st.info(response.text)
        except Exception as e: st.error(f"错误: {e}")

st.divider()

# --- 2-4 提纲部分 (保持不变) ---
# ... (为了节省篇幅，此处逻辑与 V12.0 相同，但需注意下方正文生成时要调用 read_all_files) ...
c2, c3 = st.columns(2)
with c2:
    st.header("2️⃣ 提纲规则设定")
    st.text_area("输入提纲生成的复杂要求", height=150, key='outline_rules')
with c3:
    st.header("3️⃣ 故事素材输入")
    st.text_area("输入您零散的故事脑洞/讲述", height=150, key='raw_story')
st.divider()

st.header("4️⃣ 生成的提纲")
if st.button("⚡ 生成提纲"):
    if not st.session_state.GEMINI_API_KEY: st.error("❌ 无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            prompt = f"规则：{st.session_state.outline_rules}\n素材：{st.session_state.raw_story}\n请生成大纲。"
            with st.spinner("生成中..."):
                st.session_state.outline = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("提纲结果", st.session_state.outline, height=200)
st.divider()

# --- 5 & 6. 正文生成 ---
st.header("5️⃣ 正文写作要求")
st.text_area("输入本章的具体写作要求", height=100, key='writing_rules')

st.header("6️⃣ 生成的小说正文")
if st.button("✍️ 撰写正文"):
    if not st.session_state.GEMINI_API_KEY: st.error("❌ 无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            # 读取所有文件内容作为风格参考
            style_content = read_all_files(uploaded_files)
            prompt = f"模仿风格：\n{style_content[:5000]}\n\n大纲：{st.session_state.outline}\n要求：{st.session_state.writing_rules}\n请创作第一章："
            with st.spinner("写作中..."):
                st.session_state.story = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("正文最终结果", st.session_state.story, height=400)
st.divider()

# --- 7. 自检 ---
st.header("7️⃣ 逻辑自检")
if st.button("🔍 检查冲突"):
    if not st.session_state.GEMINI_API_KEY: st.error("❌ 无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            doc_content = read_all_files(uploaded_files)
            prompt = f"检查冲突：\n资料库：{doc_content[:10000]}\n正文：{st.session_state.story}\n列出矛盾点："
            with st.spinner("自检中..."):
                st.write(client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text)
        except Exception as e: st.error(f"错误: {e}")
