import streamlit as st
from google import genai
import io

# 尝试导入 docx
try:
    import docx
except ImportError:
    docx = None

st.set_page_config(page_title="Gemini AI小说创作台 V15.0 (逻辑自检版)", layout="wide")

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
            if file.name.endswith('.docx'):
                if docx:
                    doc = docx.Document(file)
                    content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                content = file.getvalue().decode("utf-8")
            if content: all_content.append(f"--- 文件名：{file.name} ---\n{content}\n")
        except Exception: continue
    return "\n".join(all_content)

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY: st.success("API Key 已就绪")
    
    st.divider()
    st.header("📚 核心资料库")
    
    # 1. 风格库
    st.subheader("1. 写作风格参考")
    style_files = st.file_uploader("上传风格范文 (TXT/MD/DOCX)", type=['txt', 'md', 'docx'], key='uploaded_style_files', accept_multiple_files=True)
    
    st.divider()
    
    # 2. 人物库
    st.subheader("2. 人物设定卡")
    char_files = st.file_uploader("上传人物设定 (TXT/MD/DOCX)", type=['txt', 'md', 'docx'], key='uploaded_char_files', accept_multiple_files=True)

# --- 1. 资料库问答 ---
st.header("1️⃣ 资料库问答 (真实AI)")
col_q, col_btn = st.columns([5, 1])
with col_q: user_query = st.text_input("输入问题...", key="query_input")
with col_btn: 
    st.write(""); st.write("")
    ask_btn = st.button("提问 🤖")

if ask_btn and user_query:
    if not st.session_state.GEMINI_API_KEY: st.error("❌ 无 API Key")
    else:
        try:
            style_content = read_all_files(style_files)
            char_content = read_all_files(char_files)
            full_context = f"【人物设定】：\n{char_content}\n\n【风格参考】：\n{style_content}"
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            with st.spinner("🤖 查阅中..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=f"参考资料：\n{full_context[:20000]}\n用户问题：{user_query}")
                st.info(response.text)
        except Exception as e: st.error(f"错误: {e}")
st.divider()

# --- 2-4 提纲部分 ---
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
            char_content = read_all_files(char_files)
            prompt = f"人物设定：\n{char_content[:5000]}\n\n规则：{st.session_state.outline_rules}\n素材：{st.session_state.raw_story}\n请生成大纲。"
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
            style_doc = read_all_files(style_files)
            char_doc = read_all_files(char_files)
            prompt = f"""
            人物设定：{char_doc[:5000]}
            风格参考：{style_doc[:5000]}
            大纲：{st.session_state.outline}
            要求：{st.session_state.writing_rules}
            请创作第一章：
            """
            with st.spinner("写作中..."):
                st.session_state.story = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
                st.success("完成！")
        except Exception as e: st.error(f"错误: {e}")
st.text_area("正文最终结果", st.session_state.story, height=400)
st.divider()

# --- 7. 自检 (核心升级) ---
st.header("7️⃣ 逻辑自检 (深度扫描)")
if st.button("🔍 检查逻辑与人设冲突"):
    if not st.session_state.GEMINI_API_KEY: st.error("❌ 无 API Key")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            # 读取人物设定
            char_doc = read_all_files(char_files)
            # 获取当前大纲
            current_outline = st.session_state.outline
            # 获取当前正文
            current_story = st.session_state.story
            
            # 构建自检 Prompt
            prompt = f"""
            你是一个严厉的小说逻辑编辑。请检查以下【正文】是否存在逻辑错误。
            
            1. 【人设一致性检查】：
            对比【人物设定】：{char_doc[:5000]}
            检查正文中的人物对话、行为是否符合性格特征。
            
            2. 【剧情逻辑检查】：
            对比【故事大纲】：{current_outline[:5000]}
            检查正文是否偏离了既定的大纲走向。
            
            --- 正文内容 ---
            {current_story}
            --- 正文结束 ---
            
            请列出具体的矛盾点（如果没有冲突，请回复“逻辑通顺”）：
            """
            with st.spinner("正在进行深度逻辑扫描..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.warning("自检报告如下：")
                st.write(response.text)
        except Exception as e: st.error(f"错误: {e}")
