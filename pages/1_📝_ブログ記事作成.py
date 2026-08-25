import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="ブログ記事作成", page_icon="📝", layout="wide")
render_api_key_sidebar()

st.title("📝 ブログ記事作成")
st.caption("テーマとポイントを入力すると、ブログ記事の下書きを生成します。")

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("記事のテーマ", placeholder="例：在宅ワークの生産性を上げる5つの習慣")
    audience = st.text_input("想定読者", placeholder="例：在宅勤務歴1年未満の会社員")
    tone = st.selectbox(
        "文体・トーン",
        ["丁寧・解説調", "カジュアル・親しみやすい", "ビジネス・フォーマル", "エッセイ風"],
    )
with col2:
    length = st.select_slider(
        "文章の長さ",
        options=["短め（600字程度）", "標準（1200字程度）", "長め（2000字程度）"],
        value="標準（1200字程度）",
    )
    keywords = st.text_area("含めたいキーワード・要点（任意、改行区切り）", height=100)
    seo = st.checkbox("SEOを意識した見出し構成にする", value=True)

if st.button("記事を生成する", type="primary", disabled=not topic):
    if require_api_key():
        system_instruction = (
            "あなたはプロのブログライター兼編集者です。"
            "自然で読みやすい日本語のブログ記事を作成してください。"
            "見出し（##など）を使い、構成の整った記事にしてください。"
        )
        prompt = f"""以下の条件でブログ記事を書いてください。

テーマ: {topic}
想定読者: {audience or "指定なし（一般読者向け）"}
文体・トーン: {tone}
長さ: {length}
含めたい要点・キーワード:
{keywords or "特になし"}
SEOを意識した見出し構成にする: {"はい" if seo else "いいえ"}

タイトル案を1つ提示したうえで、本文を書いてください。
"""
        with st.spinner("生成中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["blog_result"] = result

if st.session_state.get("blog_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["blog_result"],
        file_name="blog_draft.md",
        mime="text/markdown",
    )
