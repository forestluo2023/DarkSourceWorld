import streamlit as st
import time
from google import genai 

# --- 0. 页面配置与变量初始化 ---
st.set_page_config(page_title="Gemini AI小说创作台 V7.0", layout="wide")

# 初始化 Session State (确保所有变量都有初始值，避免 NameError)
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏：核心设置与 API 密钥 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY') 
    if st.session_state.GEMINI_API_KEY:
        st.success("API Key 已输入，可以使用 Gemini API 了。")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    st.file_uploader("上传设定集/旧稿", accept_multiple_files=True)
    st.info("💡 资料库问答和自检功能目前为模拟效果，需要更高级的配置。")

# --- 1. 资料库问答 (模拟功能) ---
st.header("1️⃣ 资料库问答 (模拟)")
st.caption("遇到设定遗忘？在这里随时向您的资料库提问。")
user_query = st.text_input("输入问题 (例如：主角第二次觉醒是什么时候？)")
if user_query:
    st.info("🤖 AI 回复：根据资料库，主角在第20章遭遇雷劫时觉醒... (模拟回复)")
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

# --- 4. 提纲输出 (连接 Gemini) ---
st.header("4️⃣ 生成的提纲")
if st.button("⚡ 结合 [板块2] + [板块3] 生成提纲"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先在侧边栏输入您的 Gemini API Key！")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            
            prompt = f"""
            请严格按照以下规则和故事素材，为我创作一部小说大纲：
            规则：{st.session_state.outline_rules}
            素材：{st.session_state.raw_story}
            要求输出一个详细的章节列表。
            """
            
            with st.spinner("🤖 正在连接 Gemini 生成提纲..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash', # 使用快速模型进行提纲生成
                    contents=prompt
                )
                st.session_state.outline = response.text
                st.success("提纲已通过 Gemini API 成功生成！")
        except Exception as e:
            st.error(f"❌ Gemini API 调用失败：请检查您的密钥是否正确或网络连接。错误信息: {e}")

st.text_area("提纲结果 (可手动微调)", st.session_state.outline, height=200)
st.divider()

# --- 5. 写作要求输入 ---
st.header("5️⃣ 正文写作要求")
st.text_area("输入本章的具体写作要求 (文风、字数、视角)", height=100, key='writing_rules')

# --- 6. 正文输出 (连接 Gemini) ---
st.header("6️⃣ 生成的小说正文")
if st.button("✍️ 结合 [板块4] + [板块5] 撰写正文"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先在侧边栏输入您的 Gemini API Key！")
    elif st.session_state.outline in ["点击下方按钮生成大纲。", ""]:
        st.warning("⚠️ 请先生成或输入大纲，否则 AI 不知道要写什么。")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            
            prompt = f"""
            请根据以下大纲和写作要求，创作小说的第一个章节：
            大纲：{st.session_state.outline[:500]}... (使用大纲作为上下文)
            写作要求：{st.session_state.writing_rules}
            """
            
            with st.spinner("🚀 正在连接 Gemini 创作正文..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                st.session_state.story = f"=== 第一章 ===\n\n" + response.text
                st.success("正文创作完成！")
        except Exception as e:
            st.error(f"❌ Gemini API 调用失败：请检查您的密钥或网络。错误信息: {e}")

st.text_area("正文最终结果", st.session_state.story, height=400)
st.divider()

# --- 7. 逻辑自检 (模拟功能) ---
st.header("7️⃣ 逻辑/冲突自检 (模拟)")
if st.button("🔍 检查正文是否与资料库冲突"):
    with st.status("正在进行深度一致性扫描..."):
        time.sleep(1)
        st.write("正在比对人物性格...")
        time.sleep(1)
        st.write("正在核查时间线...")
    st.error("⚠️ 发现 1 个潜在冲突！")
    st.markdown("""
    - **冲突点**：正文中的主角年龄与资料库不符。
    - **建议**：请检查并修改。
    """)
