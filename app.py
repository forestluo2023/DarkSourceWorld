import streamlit as st
from google import genai
import io
import re

# 尝试导入 docx
try:
    import docx
except ImportError:
    docx = None

st.set_page_config(page_title="Gemini AI小说创作工作流 V17.0", layout="wide")

# --- 初始化 Session State ---
if 'GEMINI_API_KEY' not in st.session_state: st.session_state.GEMINI_API_KEY = ""
if 'outline_rules' not in st.session_state: st.session_state.outline_rules = "要求：\n1. 严格按照三幕式结构设计。\n2. 每章结尾必须以此留有悬念。"
if 'raw_story' not in st.session_state: st.session_state.raw_story = "在此输入您的故事梗概..."
if 'writing_rules' not in st.session_state: st.session_state.writing_rules = "要求：\n1. 必须保留我的文风特点。\n2. 单章字数控制在2500字左右。"
if 'chapter_target_words' not in st.session_state: st.session_state.chapter_target_words = 2500
if 'target_chapter_count' not in st.session_state: st.session_state.target_chapter_count = 5 
if 'refinement_stage' not in st.session_state: st.session_state.refinement_stage = "A" 
if 'refinement_chat' not in st.session_state: st.session_state.refinement_chat = []
if 'initial_outlines' not in st.session_state: st.session_state.initial_outlines = ""
if 'final_outlines' not in st.session_state: st.session_state.final_outlines = "请先完成提纲精炼。"
if 'current_chapter_index' not in st.session_state: st.session_state.current_chapter_index = 0
if 'story_content' not in st.session_state: st.session_state.story_content = "请选择章节并开始写作。"
if 'extracted_style_prompt' not in st.session_state: st.session_
