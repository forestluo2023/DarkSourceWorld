import streamlit as st
import time
from google import genai
import io # 导入io库用于处理文件内容

# --- 0. 页面配置与变量初始化 ---
st.set_page_config(page_title="Gemini AI小说创作台 V8.0 (风格修复版)", layout="wide")

# 初始化 Session State (确保所有变量都有初始值，避免 NameError)
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""
if 'uploaded_style_file' not in st.session_state: st.session_state.uploaded_style_file = None # 新增文件变量

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏：核心设置与 API 密钥 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY') 
    if st.session_state.GEMINI_API_KEY:
        st.success("API Key 已输入，可以使用 Gemini API 了。")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    # 绑定到 session_state
    uploaded_file = st.file_uploader("上传风格参考文稿 (TXT格式最佳)", type=['txt', 'md'], key='uploaded_style_file') 
    if uploaded_file is not None:
        st.info(f"文件 '{uploaded_file.name}' 已上传。")
    st.info("💡 资料库问答和自检功能仍为模拟效果。")

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
                    model='gemini-2.5-flash', 
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
            
            # --- V8.0 核心修复：读取上传的风格文件内容 ---
            style_content = ""
            if st.session_state.uploaded_style_file is not None:
                # 读取文件内容 (假设为文本文件)
                file_data = st.session_state.uploaded_style_file.getvalue()
                # 尝试解码为字符串
                try:
                    style_content = file_data.decode("utf-8")
                    st.success(f"已读取风格文件 '{st.session_state.uploaded_style_file.name}'，内容将作为风格参考注入。")
                except UnicodeDecodeError:
                    st.warning("⚠️ 无法以 UTF-8 编码读取文件，请确保您上传的是纯文本文件。")
                    style_content = ""
            
            # 构建包含风格的 Prompt
            prompt = f"""
            你现在是一个专业的小说家。
            请严格模仿以下提供的【风格参考】的文笔和语言习惯进行创作。
            请根据以下【大纲】和【写作要求】，创作小说的第一个章节：
            
            --- 风格参考 ---
            {style_content[:3000]}... (仅发送前3000字作为风格参考)
            --- 风格参考结束 ---
            
            大纲：{st.session_state.outline}
            写作要求：{st.session_state.writing_rules}
            """
            
            with st.spinner("🚀 正在连接 Gemini 创作正文..."):
                response = client.models.generate_content(
                    model='gemini-2.5-pro', # 切换到 Pro 模型以获得更好的风格模仿能力
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
