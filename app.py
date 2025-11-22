import streamlit as st
from google import genai
import io

try: import docx
except ImportError: docx = None

st.set_page_config(page_title="Gemini AI小说创作台 V16.0 (三维资料库)", layout="wide")

# --- 初始化 ---
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

# --- 辅助函数 ---
def read_all_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    all_content = []
    for file in uploaded_files:
        try:
            content = ""
            if file.name.endswith('.docx') and docx:
                doc = docx.Document(file)
                content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                content = file.getvalue().decode("utf-8")
            if content: all_content.append(f"--- {file.name} ---\n{content}\n")
        except: continue
    return "\n".join(all_content)

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏：三维资料库 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY: st.success("API Key 已就绪")
    
    st.divider()
    st.header("📚 核心资料库")
    
    st.subheader("1. 写作风格参考")
    style_files = st.file_uploader("上传风格范文", type=['txt','md','docx'], key='style', accept_multiple_files=True)
    
    st.subheader("2. 人物设定卡")
    char_files = st.file_uploader("上传人物小传", type=['txt','md','docx'], key='char', accept_multiple_files=True)
    
    st.subheader("3. 世界观/环境设定") # 新增模块
    world_files = st.file_uploader("上传世界观/地图/物品设定", type=['txt','md','docx'], key='world', accept_multiple_files=True)

# --- 1. 全局资料库问答 ---
st.header("1️⃣ 资料库问答")
col_q, col_btn = st.columns([5, 1])
with col_q: user_query = st.text_input("输入问题 (如：这个世界的货币是什么？)", key="query")
with col_btn: 
    st.write(""); st.write("")
    if st.button("提问 🤖"):
        if not st.session_state.GEMINI_API_KEY: st.error("无 API Key")
        else:
            try:
                # 汇总所有资料
                context = f"世界观：\n{read_all_files(world_files)}\n人物：\n{read_all_files(char_files)}\n风格：\n{read_all_files(style_files)}"
                client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
                with st.spinner("查阅中..."):
                    resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"资料：\n{context[:30000]}\n问题：{user_query}")
                    st.info(resp.text)
            except Exception as e: st.error(f"错误: {e}")
st.divider()

# --- 2-4 提纲生成 ---
c2, c3 = st.columns(2)
with c2: st.header("2️⃣ 提纲规则"); st.text_area("输入规则", height=150, key='outline_rules')
with c3: st.header("3️⃣ 故事素材"); st.text_area("输入脑洞", height=150, key='raw_story')
st.divider()

st.header("4️⃣ 生成大纲")
if st.button("⚡ 生成提纲"):
    if not st.session_state.GEMINI_API_KEY: st.error("无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            world_doc = read_all_files(world_files)
            char_doc = read_all_files(char_files)
            prompt = f"世界观：{world_doc[:5000]}\n人物：{char_doc[:5000]}\n规则：{st.session_state.outline_rules}\n素材：{st.session_state.raw_story}\n生成大纲。"
            with st.spinner("生成中..."):
                st.session_state.outline = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("提纲结果", st.session_state.outline, height=200)
st.divider()

# --- 5-6 正文生成 ---
st.header("5️⃣ 写作要求"); st.text_area("本章要求", height=100, key='writing_rules')
st.header("6️⃣ 生成正文")
if st.button("✍️ 撰写正文"):
    if not st.session_state.GEMINI_API_KEY: st.error("无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            # 读取所有库
            style_doc = read_all_files(style_files)
            char_doc = read_all_files(char_files)
            world_doc = read_all_files(world_files)
            
            prompt = f"""
            你是一个专业小说家。请严格基于以下设定创作：
            1. 【世界观】：{world_doc[:5000]} (确保地名、物品、战力体系准确)
            2. 【人物】：{char_doc[:5000]} (确保性格、外貌、口癖一致)
            3. 【风格】：模仿此文笔 -> {style_doc[:5000]}
            
            大纲：{st.session_state.outline}
            要求：{st.session_state.writing_rules}
            创作第一章：
            """
            with st.spinner("写作中..."):
                st.session_state.story = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("正文结果", st.session_state.story, height=400)
st.divider()

# --- 7 自检 ---
st.header("7️⃣ 逻辑自检")
if st.button("🔍 全面检查"):
    if not st.session_state.GEMINI_API_KEY: st.error("无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            world_doc = read_all_files(world_files)
            char_doc = read_all_files(char_files)
            prompt = f"""
            请检查正文逻辑冲突：
            世界观：{world_doc[:5000]}
            人物：{char_doc[:5000]}
            大纲：{st.session_state.outline[:2000]}
            正文：{st.session_state.story}
            列出矛盾点：
            """
            with st.spinner("检查中..."):
                st.write(client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text)
        except Exception as e: st.error(f"错误: {e}")
