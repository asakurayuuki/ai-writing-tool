import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="校正・推敲", page_icon="✅", layout="wide")
render_api_key_sidebar()

st.title("✅ 校正・推敲")
st.caption("誤字脱字や不自然な表現をチェックし、改善案を提示します。")

text = st.text_area("チェックしたい文章", height=300, placeholder="ここに文章を貼り付けてください")

focus = st.multiselect(
    "チェックの観点",
    ["誤字脱字", "文法・助詞の誤り", "表現の重複・冗長さ", "論理の飛躍・分かりにくさ", "敬語の誤用"],
    default=["誤字脱字", "文法・助詞の誤り", "表現の重複・冗長さ"],
)

if st.button("校正する", type="primary", disabled=not text):
    if require_api_key():
        system_instruction = (
            "あなたはプロの日本語校正者・編集者です。"
            "指摘事項を一覧で示したうえで、修正済みの全文を提示してください。"
            "出力は「■ 指摘一覧」と「■ 修正後の全文」の2セクションに分けてください。"
        )
        prompt = f"""以下の文章を校正してください。

【チェックの観点】
{"、".join(focus) if focus else "全般"}

【原文】
{text}
"""
        with st.spinner("校正中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["proof_result"] = result

if st.session_state.get("proof_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["proof_result"],
        file_name="proofread.txt",
        mime="text/plain",
    )
