import streamlit as st
import time
from google import genai
import io

# 尝试导入 docx 库，如果用户忘了更新 requirements.txt，给予提示
try:
    import docx
except ImportError:
    docx = None

# --- 0. 页面配置 ---
st.set_page_config(page_title="Gemini AI小说创作台 V11.0 (Word支持版)", layout="wide")

# --- 变量初始化 ---
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

# --- 辅助函数：读取文件内容 (TXT/MD/DOCX) ---
def read_file_content(uploaded_file):
    if uploaded_file is None:
        return ""
    
    try:
        # 处理 Word 文档 (.docx)
        if uploaded_file.name.endswith('.docx'):
            if docx is None:
                st.error("⚠️ 缺少 python-docx 库，请在 requirements.txt 中添加 'python-docx'")
                return ""
            doc = docx.Document(uploaded_file)
            # 将所有段落拼接成字符串
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
            
        # 处理普通文本 (.txt, .md)
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        st.error(f"❌ 文件读取失败: {e}")
        return ""

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY:
        st.success("API Key 已输入")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    # V11.0 更新：type 中增加了 'docx'
    uploaded_file = st.file_uploader("上传风格参考 (支持 TXT/MD/DOCX)", type=['txt', 'md', 'docx'], key='uploaded_style_file')
    
    if uploaded_file is not None:
        st.info(f"文件 '{uploaded_file.name}' 已上传。")

# --- 1. 资料库问答 ---
st.header("1️⃣ 资料库问答 (模拟)")
user_query = st.text_input("输入问题 (例如：主角第二次觉醒是什么时候？)")
if user_query:
    st.info("🤖 AI 回复：根据资料库... (模拟回复)")
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
        st.error("❌ 请先在侧边栏输入 Gemini API Key！")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            prompt = f"""
            请严格按照以下规则和故事素材，为我创作一部小说大纲：
            规则：{st.session_state.outline_rules}
            素材：{st.session_state.raw_story}
            """
            with st.spinner("🤖 正在连接 Gemini 生成提纲..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.session_state.outline = response.text
                st.success("提纲已生成！")
        except Exception as e:
            st.error(f"❌ 调用失败: {e}")

st.text_area("提纲结果", st.session_state.outline, height=200)
st.divider()

# --- 5. 写作要求 ---
st.header("5️⃣ 正文写作要求")
st.text_area("输入本章的具体写作要求", height=100, key='writing_rules')

# --- 6. 正文输出 ---
st.header("6️⃣ 生成的小说正文")
if st.button("✍️ 结合 [板块4] + [板块5] 撰写正文"):
    if not st.session_state.GEMINI_API_KEY:
        st.error("❌ 请先在侧边栏输入 Gemini API Key！")
    else:
        try:
            client = genai.Client(api_key=st.session_state.GEMINI_API_KEY)
            
            # V11.0 更新：使用 helper 函数读取 Word 或 TXT
            style_content = read_file_content(st.session_state.uploaded_style_file)
            
            if style_content:
                st.success(f"✅ 成功读取风格文件内容 (前100字预览): {style_content[:100]}...")
            else:
                st.warning("⚠️ 未检测到风格文件或文件内容为空，将不使用风格参考。")

            prompt = f"""
            请模仿以下【风格参考】进行创作。
            --- 风格参考 ---
            {style_content[:3000]}
            --- 参考结束 ---
            大纲：{st.session_state.outline}
            要求：{st.session_state.writing_rules}
            创作第一章正文：
            """
            with st.spinner("🚀 正在连接 Gemini 创作正文..."):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.session_state.story = response.text
                st.success("创作完成！")
        except Exception as e:
            st.error(f"❌ 调用失败: {e}")

st.text_area("正文最终结果", st.session_state.story, height=400)
st.divider()

# --- 7. 自检 ---
st.header("7️⃣ 逻辑自检 (模拟)")
if st.button("🔍 检查冲突"):
    st.info("⚠️ (模拟) 发现潜在冲突：主角年龄设定不符。")
