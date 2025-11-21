# --- V6.0 核心代码更新 ---

# 初始化 Session State (请确保您的文件顶部有这行)
if 'outline' not in st.session_state: st.session_state.outline = ""
if 'story' not in st.session_state: st.session_state.story = ""
# 确保所有输入变量都初始化
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "严格遵循三幕式结构..."
if 'raw_story' not in st.session_state: st.session_state.raw_story = "主角是个厨师..."

# ... (省略板块 1 的代码) ...

# --- 板块 2 & 3: 提纲输入 ---
c2, c3 = st.columns(2)
with c2:
    st.header("2️⃣ 提纲规则设定")
    # 使用 st.session_state 绑定变量
    st.text_area("输入提纲生成的复杂要求", key='outline_rules', height=150) 
with c3:
    st.header("3️⃣ 故事素材输入")
    # 使用 st.session_state 绑定变量
    st.text_area("输入您零散的故事脑洞/讲述", key='raw_story', height=150)

st.divider()

# --- 板块 4: 提纲输出 (替换为真实 Gemini 调用) ---
st.header("4️⃣ 生成的提纲")
if st.button("⚡ 结合 [板块2] + [板块3] 生成提纲"):
    if not GEMINI_API_KEY:
        st.error("❌ 请先在侧边栏输入您的 Gemini API Key！")
    else:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # 使用 st.session_state 来获取变量，而不是直接使用 outline_rules
            prompt = f"请严格按照以下规则和故事素材，生成一个详细的小说大纲：\n\n规则：{st.session_state.outline_rules}\n\n素材：{st.session_state.raw_story}"
            
            with st.spinner("🤖 正在连接 Gemini 生成提纲..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                st.session_state.outline = response.text
                st.success("提纲已通过 Gemini API 成功生成！")
        except Exception as e:
            st.error(f"❌ Gemini API 调用失败：{e}")

st.text_area("提纲结果 (可手动微调)", st.session_state.outline, height=200)

# ... (省略后续代码) ...
