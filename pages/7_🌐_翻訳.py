import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="翻訳", page_icon="🌐", layout="wide")
render_api_key_sidebar()

st.title("🌐 翻訳")
st.caption("ニュアンスを保ちながら、自然な訳文に翻訳します。")

text = st.text_area("翻訳したい文章", height=250, placeholder="ここに文章を入力してください")

col1, col2 = st.columns(2)
with col1:
    target_lang = st.selectbox(
        "翻訳先の言語",
        ["英語", "日本語", "中国語（簡体字）", "韓国語", "フランス語", "スペイン語", "ドイツ語"],
    )
with col2:
    tone = st.selectbox("トーン", ["自然・標準", "ビジネスフォーマル", "カジュアル"])

if st.button("翻訳する", type="primary", disabled=not text):
    if require_api_key():
        system_instruction = (
            "あなたはプロの翻訳者です。原文のニュアンス・トーンを保ちながら、"
            "不自然な直訳を避け、目標言語として自然な訳文にしてください。"
            "訳文のみを出力してください。"
        )
        prompt = f"""以下の文章を{target_lang}に翻訳してください。

【トーン】{tone}

【原文】
{text}
"""
        with st.spinner("翻訳中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["translate_result"] = result

if st.session_state.get("translate_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["translate_result"],
        file_name="translation.txt",
        mime="text/plain",
    )
