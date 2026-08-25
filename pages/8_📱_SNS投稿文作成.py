import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="SNS投稿文作成", page_icon="📱", layout="wide")
render_api_key_sidebar()

st.title("📱 SNS投稿文作成")
st.caption("プラットフォームに合わせた投稿文を作成します。")

topic = st.text_area("投稿したい内容・伝えたいこと", height=150, placeholder="例：新しいブログ記事を公開したので告知したい")

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("プラットフォーム", ["X（Twitter）", "Instagram", "Threads", "Facebook", "LinkedIn"])
    tone = st.selectbox("トーン", ["カジュアル・親しみやすい", "ビジネス・フォーマル", "ユーモアあり", "熱意を伝える"])
with col2:
    hashtags = st.checkbox("ハッシュタグ案も付ける", value=True)
    variations = st.slider("生成するパターン数", min_value=1, max_value=5, value=3)

if st.button("投稿文を生成する", type="primary", disabled=not topic):
    if require_api_key():
        char_limit_note = "280字以内（日本語は全角140字目安）" if platform == "X（Twitter）" else "プラットフォームの一般的な慣習に沿った長さ"
        system_instruction = (
            "あなたはSNSマーケティングの専門家です。"
            "プラットフォームの特性に合った、読者の反応を引き出す投稿文を作成してください。"
        )
        prompt = f"""以下の内容でSNS投稿文を{variations}パターン作成してください。

【プラットフォーム】{platform}
【トーン】{tone}
【文字数の目安】{char_limit_note}
【ハッシュタグ】{"末尾に3〜5個の関連ハッシュタグを付ける" if hashtags else "不要"}

【投稿したい内容】
{topic}

各パターンには番号を付け、区別しやすいようにしてください。
"""
        with st.spinner("生成中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["sns_result"] = result

if st.session_state.get("sns_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["sns_result"],
        file_name="sns_posts.txt",
        mime="text/plain",
    )
