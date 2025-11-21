import streamlit as st
import time

st.set_page_config(page_title="线性流小说创作台", layout="wide")

# 初始化 Session State
if 'outline' not in st.session_state: st.session_state.outline = ""
if 'story' not in st.session_state: st.session_state.story = ""
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

st.title("📜 深度小说创作流 (Linear Flow)")

# --- 侧边栏：资料上传 ---
with st.sidebar:
    st.header("📚 0. 核心资料库")
    st.file_uploader("上传设定集/旧稿", accept_multiple_files=True)
    st.info("上传后，下方的【板块1】和【板块7】将基于这些资料工作。")

# --- 板块 1: 资料库交互 (Chat) ---
st.header("1️⃣ 资料库问答")
st.caption("遇到设定遗忘？在这里随时向您的资料库提问。")
q_col, a_col = st.columns([3, 1])
with q_col:
    user_query = st.text_input("输入问题 (例如：主角第二次觉醒是什么时候？)", key="kb_query")
if user_query:
    st.info(f"🤖 AI 回复：根据资料库，主角在第20章遭遇雷劫时觉醒... (模拟回复)")

st.divider()

# --- 板块 2 & 3: 提纲输入 ---
c2, c3 = st.columns(2)
with c2:
    st.header("2️⃣ 提纲规则设定")
    outline_rules = st.text_area("输入提纲生成的复杂要求", "严格遵循三幕式结构，每章结尾留悬念...", height=150)
with c3:
    st.header("3️⃣ 故事素材输入")
    raw_story = st.text_area("输入您零散的故事脑洞/讲述", "主角是个厨师，但是这天他捡到了一把剑...", height=150)

st.divider()

# --- 板块 4: 提纲输出 ---
st.header("4️⃣ 生成的提纲")
if st.button("⚡ 结合 [板块2] + [板块3] 生成提纲"):
    st.session_state.outline = f"【已生成提纲】\n基于规则：{outline_rules[:10]}...\n1. 第一章：厨师的奇遇\n2. 第二章：剑的秘密..."
    st.success("提纲已生成！")
st.text_area("提纲结果 (可手动微调)", st.session_state.outline, height=200)

st.divider()

# --- 板块 5 & 6: 正文写作 ---
st.header("5️⃣ 正文写作要求")
writing_rules = st.text_area("输入本章的具体写作要求 (文风、字数、视角)", "要求模仿我上传的文风，略带忧郁，2500字左右...", height=100)

st.header("6️⃣ 生成的小说正文")
if st.button("✍️ 结合 [板块4] + [板块5] 撰写正文"):
    st.session_state.story = f"【第N章 正文】\n(AI严格执行要求：{writing_rules[:10]}...)\n\n那把剑生锈了，就像他此刻的心情一样..."
    st.success("写作完成！")
st.text_area("正文最终结果", st.session_state.story, height=400)

st.divider()

# --- 板块 7: 逻辑自检 ---
st.header("7️⃣ 逻辑/冲突自检")
if st.button("🔍 检查正文是否与资料库冲突"):
    with st.status("正在进行深度一致性扫描..."):
        time.sleep(1)
        st.write("正在比对人物性格...")
        time.sleep(1)
        st.write("正在核查时间线...")
    # 模拟检测结果
    st.error("⚠️ 发现 1 个潜在冲突！")
    st.markdown("""
    - **冲突点**：正文中提到主角"不吃辣"，但资料库（第3章）设定主角"嗜辣如命"。
    - **建议**：请确认是否需要修改设定或正文。
    """)
