import streamlit as st
from google import genai
import io
import re

# 尝试导入 docx
try:
    import docx
except ImportError:
    docx = None

st.set_page_config(page_title="Gemini AI小说创作工作流 V17.0 (终极参谋版)", layout="wide")

# --- 初始化 Session State ---
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "在此输入您的故事梗概..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 必须保留我的文风特点。\n2. 单章字数控制在2500字左右。"
if 'chapter_target_words' not in st.session_state: st.session_state.chapter_target_words = 2500
if 'target_chapter_count' not in st.session_state: st.session_state.target_chapter_count = 5 # 用户期望的章数
if 'refinement_stage' not in st.session_state: st.session_state.refinement_stage = "A" 
if 'refinement_chat' not in st.session_state: st.session_state.refinement_chat = []
if 'initial_outlines' not in st.session_state: st.session_state.initial_outlines = ""
if 'final_outlines' not in st.session_state: st.session_state.final_outlines = "请先完成提纲精炼。"
if 'current_chapter_index' not in st.session_state: st.session_state.current_chapter_index = 0
if 'story_content' not in st.session_state: st.session_state.story_content = "请选择章节并开始写作。"
if 'extracted_style_prompt' not in st.session_state: st.session_state.extracted_style_prompt = ""

# --- 辅助函数 ---
def read_all_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    all_content = []
    for file in uploaded_files:
        content = ""
        if file.name.endswith('.docx') and docx:
            try:
                doc = docx.Document(file)
                content = '\n'.join([para.text for para in doc.paragraphs])
            except Exception: pass
        else:
            try:
                content = file.getvalue().decode("utf-8")
            except Exception: pass
        if content: all_content.append(f"--- 文件名：{file.name} ---\n{content}\n")
    return "\n".join(all_content)

def get_gemini_client():
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请在侧边栏输入 Gemini API Key。")
        return None
    try:
        return genai.Client(api_key=st.session_state.GEMINI_API_KEY)
    except Exception as e:
        st.error(f"API Key 初始化失败: {e}")
        return None

# --- 侧边栏：资料库与全能分析 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    
    st.divider()
    st.header("📚 核心资料库 & 风格分析")
    
    # 1. 风格库上传与分析
    st.info("💡 步骤1: 上传 5-8 章您的代表作，让 AI 学习您的‘章节密度’。")
    style_files = st.file_uploader("上传您的旧作 (TXT/DOCX)", type=['txt', 'md', 'docx'], key='uploaded_style_files', accept_multiple_files=True)
    
    if style_files:
        if st.button("🪄 全能分析 (提取文风+结构密度)"):
            client = get_gemini_client()
            if client:
                raw_text = read_all_files(style_files)
                # 升级后的 Prompt：逆向工程分析
                prompt_analyze = f"""
                你是一位资深的小说主编。请深度阅读以下作者的 5 个样章，进行两方面的逆向分析。
                
                --- 样章内容 ---
                {raw_text[:40000]} 
                
                --- 分析任务 ---
                请输出一份【作者创作习惯指南】：
                1. 【文风 DNA】(用于正文扩写)：叙事视角、用词偏好、对话风格。
                2. 【结构与密度密码】(核心 - 用于提纲规划)：
                   - **单章信息量**：平均每一章(2500字)包含几个核心事件？(例如：3个小转折+1个大高潮)
                   - **节奏感**：作者是喜欢快速推进剧情，还是喜欢大量心理/环境描写来填充字数？
                   - **场景切换**：一章内通常切换几次场景？
                """
                with st.spinner("正在解析您的文风 DNA 和 章节密度..."):
                    try:
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_analyze)
                        st.session_state.extracted_style_prompt = response.text
                        st.success("分析完成！AI 已掌握您的‘叙事节奏’。")
                    except Exception as e: st.error(f"分析失败: {e}")
    
    st.text_area("生成的风格与密度指南", value=st.session_state.extracted_style_prompt, height=150, key='style_guide_final', help="AI 将根据这个标准来判断您的素材够写几章")

    st.divider()
    st.subheader("2. 人物设定卡")
    char_files = st.file_uploader("上传人物设定", type=['txt', 'md', 'docx'], key='uploaded_char_files', accept_multiple_files=True)
    st.divider()
    st.number_input("单章字数目标", value=2500, step=100, key='chapter_target_
