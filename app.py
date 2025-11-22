import streamlit as st
import time
from google import genai
import io

# 尝试导入 docx 库
try:
    import docx
except ImportError:
    docx = None

# --- 0. 页面配置 ---
st.set_page_config(page_title="Gemini AI小说创作台 V12.0 (全功能解锁)", layout="wide")

# --- 变量初始化 ---
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

# --- 辅助函数：读取文件内容 ---
def read_file_content(uploaded_file):
    if uploaded_file is None: return ""
    try:
        if uploaded_file.name.endswith('.docx'):
            if docx is None: return "错误：缺少 python-docx 库"
            doc = docx.Document(uploaded_file)
            return '\n'.join([para.text for para in doc.paragraphs])
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"读取失败: {e}"

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY:
        st.success("API Key 已就绪")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    uploaded_file = st.file_uploader("上传资料/风格参考 (TXT/MD/DOCX)", type=['txt', 'md', 'docx'], key='uploaded_style_file')
    if uploaded_file: st.info(f"已加载：{uploaded_file.name}")

# --- 1. 资料库问答 (V12.0 真实连接版) ---
st.header("1️⃣ 资料库问答 (真实AI)")
st.caption("基于您上传的【核心资料库】进行回答。")

col_q, col_btn = st.columns([5, 1])
with col_q:
    user_query = st.text_input("输入关于设定的问题...", key="query_input")
with col_btn:
    st.write("") # 占位
    st.write("") 
    ask_btn = st.button("提问 🤖")

if ask_btn and user_query:
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先输入 API Key")
    elif st.session_state.uploaded_style_file is None:
        st.warning("⚠️ 请先在侧边栏上传资料库文件，否则我无法回答关于设定的问题。")
    else:
        try:
            # 1. 读取文件
            doc_content = read_file_content(st.session_state.uploaded_style_file)
            
            # 2. 构建 RAG Prompt
            rag_prompt = f"""
            你是一个专业的助手。请根据以下【参考文档】的内容，准确回答用户的【问题】。
            如果文档中没有相关信息，请直接说“资料库中未找到相关设定”。
            
            --- 参考文档 ---
            {doc_content[:10000]}... (截取前1万字以防超长)
            --- 文档结束 ---
            
            用户问题：{user_query}
            """
            
            # 3. 调用 API
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            with st.spinner("🤖 正在查阅资料库..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=rag_prompt)
                st.success("✅ 回答如下：")
                st.info(response.text)
                
        except Exception as e:
            st.error(f"❌ 发生错误: {e}")

st.divider()

# --- 2 & 3. 提纲输入 ---
c2, c3 = st.columns(2)
with c2:
    st.header("2️⃣ 提纲规则设定")
    st.text_area("输入提纲生成的复杂要求", height=150, key='outline_rules')
with c3:
    st.header("3️⃣ 故事素材输入")
    st.text_area("输入您零散的故事脑洞/讲述", height=150, key='raw_story')
st.divider()

# --- 4. 提纲输出 ---
st.header("4️⃣ 生成的提纲")
if st.button("⚡ 结合 [板块2] + [板块3] 生成提纲"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先输入 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            prompt = f"规则：{st.session_state.outline_rules}\n素材：{st.session_state.raw_story}\n请生成详细小说大纲。"
            with st.spinner("生成中..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.session_state.outline = response.text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("提纲结果", st.session_state.outline, height=200)
st.divider()

# --- 5 & 6. 正文生成 ---
st.header("5️⃣ 正文写作要求")
st.text_area("输入本章的具体写作要求", height=100, key='writing_rules')

st.header("6️⃣ 生成的小说正文")
if st.button("✍️ 结合 [板块4] + [板块5] 撰写正文"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先输入 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            style_content = read_file_content(st.session_state.uploaded_style_file)
            prompt = f"模仿风格：\n{style_content[:3000]}\n\n大纲：{st.session_state.outline}\n要求：{st.session_state.writing_rules}\n请创作第一章："
            with st.spinner("写作中..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.session_state.story = response.text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("正文最终结果", st.session_state.story, height=400)
st.divider()

# --- 7. 自检 (V12.0 真实连接版) ---
st.header("7️⃣ 逻辑自检 (真实AI)")
if st.button("🔍 检查冲突"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先输入 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            doc_content = read_file_content(st.session_state.uploaded_style_file)
            prompt = f"请检查以下【正文】是否与【资料库】中的设定有冲突：\n\n资料库：{doc_content[:5000]}\n\n正文：{st.session_state.story}\n\n请列出具体的矛盾点："
            with st.spinner("自检中..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.warning("自检报告：")
                st.write(response.text)
        except Exception as e: st.error(f"错误: {e}")
