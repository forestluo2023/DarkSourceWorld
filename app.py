import streamlit as st
from google import genai
import time
import io
import random # 用于模拟多张图片
# 导入 docx
try: import docx
except ImportError: docx = None

st.set_page_config(page_title="Gemini AI小说创作台 V17.0 (图像生成)", layout="wide")

# --- 初始化 ---
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

# --- 辅助函数：读取文件内容 ---
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

# --- 侧边栏 ---
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
    st.subheader("3. 世界观/环境设定")
    world_files = st.file_uploader("上传世界观/地图/物品设定", type=['txt','md','docx'], key='world', accept_multiple_files=True)

# --- 1-7 (省略中间部分，与 V16.0 相同) ---
# ... (Sections 1-7 code here, assumes content is generated into st.session_state.story)

# -------------------------------------------------------------
# --- 新增板块 8: 封面生成 (需配合 Image API) ---
# -------------------------------------------------------------
st.divider()
st.header("8️⃣ 章节封面生成 (AIGC)")

# 样式选择
style = st.selectbox(
    "选择艺术风格 (将用于生成提示词)：",
    ['国风水墨 (Wuxia Ink)', '日式漫画 (Manga)', '吉卜力 (Ghibli)', '美系写实 (US Realistic)', '连环画 (Comic Book)']
)

# 来源选择与输入
col_input, col_btn = st.columns([4, 1])
with col_input:
    # 允许手动输入或使用已生成的正文
    img_source = st.text_area(
        "输入图片生成灵感或粘贴高光内容：", 
        value=st.session_state.story[:500] if st.session_state.story else "", # 默认使用正文前500字
        height=150
    )
with col_btn:
    st.write(""); st.write("")
    generate_cover_button = st.button("一键生成 5 张封面 (竖版)")

if generate_cover_button:
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先在侧边栏输入 Gemini API Key！")
    elif not img_source:
        st.warning("⚠️ 请输入生成图片的灵感或先生成小说正文。")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)

            # 步骤 1: 使用 Gemini LLM 生成高质量的图像提示词
            llm_prompt = f"""
            你是一个专业的图像提示词工程师。请根据用户提供的【故事内容】和【目标风格】，生成 5 个独立的、详细的、高质量的图像提示词（Prompt）。
            
            要求：
            1. 图像内容：必须是小说高光场景的描述。
            2. 图像风格：{style}。
            3. 图像比例：必须是竖版 (Portrait, 例如 2:3 或 9:16)。
            4. 图像中不得包含任何文字。
            
            故事内容：
            {img_source}
            
            输出格式：请将5个提示词分行输出，每行一个。
            """

            with st.spinner("1/2 🤖 正在用 Gemini 分析内容并生成图像提示词..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=llm_prompt)
                image_prompts = response.text.strip().split('\n')
                st.success("✅ 已生成 5 个图像提示词。")

            # 步骤 2: 模拟 Image Generation API 调用（此处为模拟展示）
            st.subheader("2/2 🖼️ 模拟封面生成结果 (实际应用需接入 Image API)")
            image_columns = st.columns(5)
            
            for i, col in enumerate(image_columns):
                # 模拟图像内容和垂直显示
                with col:
                    st.image(
                        'https://picsum.photos/300/450?random=' + str(i + random.randint(1, 100)), # 随机生成占位图
                        caption=f"场景 {i+1}：{image_prompts[i]}",
                        use_column_width=True
                    )

        except Exception as e:
            st.error(f"❌ 图像生成流程失败：{e}")
            st.warning("请确保您的 API Key 有效且网络连接正常。")

# -------------------------------------------------------------
# ... (Sections 1-7 are still in the final code block)
# ... (Retained for completeness, not shown again in response block)
# -------------------------------------------------------------
