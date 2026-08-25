import streamlit as st

from utils.gemini_client import render_api_key_sidebar, require_api_key, run_generation

st.set_page_config(page_title="メール返信作成", page_icon="✉️", layout="wide")
render_api_key_sidebar()

st.title("✉️ メール返信作成")
st.caption("受信メールの内容と返信の方針から、返信文面を作成します。")

original_mail = st.text_area("受信したメール本文", height=200, placeholder="ここに受信メールの本文を貼り付けてください")

col1, col2 = st.columns(2)
with col1:
    intent = st.text_area(
        "返信の要点・伝えたいこと",
        height=120,
        placeholder="例：提案内容には賛成。ただし納期は2週間後ろ倒しにしてほしい。",
    )
    relationship = st.selectbox(
        "相手との関係性",
        ["社外（取引先・お客様）", "社内（上司）", "社内（同僚・部下）", "友人・知人"],
    )
with col2:
    tone = st.selectbox("トーン", ["丁寧なビジネス敬語", "フォーマルだが柔らかい", "カジュアル"])
    action = st.text_input("依頼したいアクション（任意）", placeholder="例：来週水曜までに回答がほしい")

if st.button("返信文を生成する", type="primary", disabled=not (original_mail and intent)):
    if require_api_key():
        system_instruction = (
            "あなたは日本語のビジネスメール作成のプロです。"
            "自然で失礼のない、読みやすいメール文面を作成してください。"
            "宛名・書き出し・本文・結びの挨拶・署名欄（〇〇の部分はプレースホルダのままでよい）を含めてください。"
        )
        prompt = f"""以下の受信メールに対する返信文を作成してください。

【受信メール】
{original_mail}

【返信で伝えたい内容】
{intent}

【相手との関係性】{relationship}
【トーン】{tone}
【依頼したいアクション】{action or "特になし"}
"""
        with st.spinner("生成中..."):
            result = run_generation(prompt, system_instruction)
        if result:
            st.session_state["mail_result"] = result

if st.session_state.get("mail_result"):
    st.divider()
    st.download_button(
        "テキストとして保存",
        data=st.session_state["mail_result"],
        file_name="reply_mail.txt",
        mime="text/plain",
    )
