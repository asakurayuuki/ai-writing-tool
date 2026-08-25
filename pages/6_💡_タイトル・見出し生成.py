import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="タイトル・見出し生成", page_icon="💡", layout="wide")
render_api_key_sidebar()

st.title("💡 タイトル・見出し生成")
st.caption("文章の内容やテーマから、タイトル案・見出し案を複数生成します。")

mode = st.radio("入力方法", ["テーマから生成", "本文から生成"], horizontal=True)

if mode == "テーマから生成":
    content = st.text_input("テーマ・内容", placeholder="例：初心者向けNISA活用術")
else:
    content = st.text_area("本文", height=250, placeholder="ここに本文を貼り付けてください")

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "タイトルの雰囲気",
        ["わかりやすく端的", "興味を引くキャッチー系", "SEOを意識した検索されやすい形", "SNS向けでインパクト重視"],
    )
with col2:
    count = st.slider("生成する案の数", min_value=3, max_value=15, value=8)

if st.button("タイトル案を生成する", type="primary", disabled=not content):
    if require_api_key():
        system_instruction = (
            "あなたはコピーライター兼編集者です。"
            "読者の興味を引きつつ内容を正確に反映したタイトル案を作成してください。"
            "番号付きリストで出力してください。"
        )
        prompt = f"""以下の{"テーマ" if mode == "テーマから生成" else "本文"}をもとに、タイトル案を{count}個生成してください。

【雰囲気】{style}

【{"テーマ" if mode == "テーマから生成" else "本文"}】
{content}
"""
        with st.spinner("生成中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["title_result"] = result

if st.session_state.get("title_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["title_result"],
        file_name="titles.txt",
        mime="text/plain",
    )
