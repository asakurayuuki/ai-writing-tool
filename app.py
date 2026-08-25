import streamlit as st

from utils.gemini_client import render_api_key_sidebar

st.set_page_config(
    page_title="AIライティングツール",
    page_icon="✍️",
    layout="wide",
)

render_api_key_sidebar()

st.title("✍️ AIライティングツール")
st.caption("Gemini APIを使った、個人用のオールインワン文章作成アシスタント")

st.markdown(
    """
左のサイドバーから使いたい機能を選んでください。
"""
)

features = [
    ("📝", "ブログ記事作成", "テーマとポイントを入力するだけで、ブログ記事の下書きを生成します。"),
    ("✉️", "メール返信作成", "受信メールの内容と返信方針から、返信メール文面を作成します。"),
    ("📄", "文章要約", "長文を指定した長さ・形式で要約します。"),
    ("✅", "校正・推敲", "誤字脱字や表現のおかしな部分を指摘し、改善案を提示します。"),
    ("🔄", "文体変換", "文章のトーン（丁寧語・カジュアル・ビジネス等）を変換します。"),
    ("💡", "タイトル・見出し生成", "文章内容からタイトル案・見出し案を複数生成します。"),
    ("🌐", "翻訳", "日本語⇔多言語の翻訳をニュアンスを保ちつつ行います。"),
    ("📱", "SNS投稿文作成", "X（Twitter）やInstagram向けの投稿文を生成します。"),
]

cols = st.columns(2)
for i, (icon, name, desc) in enumerate(features):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {icon} {name}")
            st.write(desc)

st.divider()
st.markdown(
    """
**使い方**
1. サイドバーの「⚙️ 設定」でGemini APIキーを入力します（`.env`に`GEMINI_API_KEY`を設定していれば不要です）。
2. 使いたい機能のページを開きます。
3. 必要な情報を入力し、生成ボタンを押します。

APIキーはセッション内でのみ保持され、どこにも保存されません。
"""
)
