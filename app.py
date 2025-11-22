import streamlit as st
import time
from google import genai
import io

# --- 0. 页面配置 ---
st.set_page_config(page_title="Gemini AI小说创作台 V10.0", layout="wide")

# --- 变量初始化 (修复点：删除了文件上传的初始化) ---
# 仅初始化文本类变量，文件上传交给 Streamlit 自动处理
if 'outline' not in st.session_state: st.session_state.outline = "点击下方按钮生成大纲。"
if 'story' not in st.session_state: st.session_state.story = "点击开始写作按钮生成正文。"
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是一个拥有系统的厨师..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 文风略带忧郁。\n2. 单章字数控制在2500字左右。"
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🔑 AI 接口设置")
    st.text_input("Gemini API Key", type="password", key='GEMINI_API_KEY')
    if st.session_state.GEMINI_API_KEY:
        st.success("API Key 已输入")
    
    st.divider()
    st.header("📚 0. 核心资料库")
    # 文件上传组件（无需手动初始化 session_state）
    uploaded_file = st.file_uploader("上传风格参考文稿 (TXT格式最佳)", type=['txt', 'md'], key='uploaded_style_file')
    
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
        st.error("❌ 请先在侧边栏输入您的 Gemini API Key！")
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
            
            # 读取风格文件
            style_content = ""
            if st.session_state.uploaded_style_file is not None:
                try:
                    # 获取文件对象
                    file_obj = st.session_state.uploaded_style_file
                    # 读取并解码
                    style_content = file_obj.getvalue().decode("utf-8")
                    st.success(f"✅ 已读取风格文件：{file_obj.name}")
                except Exception as e:
                    st.warning(f"⚠️ 文件读取失败，将不使用风格参考。原因: {e}")

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
                # 使用 Pro 模型以获得更好文笔
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
