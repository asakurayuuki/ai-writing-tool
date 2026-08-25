import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="文体変換", page_icon="🔄", layout="wide")
render_api_key_sidebar()

st.title("🔄 文体変換")
st.caption("文章のトーンや文体を、目的に合わせて変換します。")

text = st.text_area("変換したい文章", height=250, placeholder="ここに文章を貼り付けてください")

target_style = st.selectbox(
    "変換後のスタイル",
    [
        "丁寧なビジネス敬語",
        "カジュアル・フランク",
        "フォーマル・学術的",
        "です・ます調",
        "だ・である調",
        "子供にもわかる簡単な言葉",
        "SNS向けの短くキャッチーな文体",
    ],
)
extra_note = st.text_input("その他の要望（任意）", placeholder="例：もっと簡潔にしてほしい")

if st.button("変換する", type="primary", disabled=not text):
    if require_api_key():
        system_instruction = (
            "あなたは日本語の文章スタイル変換の専門家です。"
            "文章の意味・情報量を保ったまま、指定されたスタイルに書き換えてください。"
        )
        prompt = f"""以下の文章を、指定したスタイルに変換してください。

【変換後のスタイル】{target_style}
【その他の要望】{extra_note or "特になし"}

【原文】
{text}
"""
        with st.spinner("変換中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["style_result"] = result

if st.session_state.get("style_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["style_result"],
        file_name="rewritten.txt",
        mime="text/plain",
    )
