import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="文章要約", page_icon="📄", layout="wide")
render_api_key_sidebar()

st.title("📄 文章要約")
st.caption("長い文章を、指定した形式・長さで要約します。")

text = st.text_area("要約したい文章", height=300, placeholder="ここに要約したいテキストを貼り付けてください")

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "要約の形式",
        ["箇条書き（要点3〜5個）", "一段落の文章", "1行の一文要約", "見出し＋箇条書き"],
    )
with col2:
    length = st.select_slider(
        "要約の長さ",
        options=["とても短く", "短め", "標準", "やや詳しく"],
        value="標準",
    )

if st.button("要約する", type="primary", disabled=not text):
    if require_api_key():
        system_instruction = (
            "あなたは文章要約のプロです。原文の意味を正確に保ちながら、"
            "指定された形式・長さで簡潔に要約してください。"
        )
        prompt = f"""以下の文章を要約してください。

【形式】{style}
【長さ】{length}

【原文】
{text}
"""
        with st.spinner("要約中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["summary_result"] = result

if st.session_state.get("summary_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["summary_result"],
        file_name="summary.txt",
        mime="text/plain",
    )
