"""Gemini API とのやり取り、共通UIパーツをまとめたモジュール。"""
import os
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 3

MODEL_OPTIONS = {
    "Gemini Flash-Lite（推奨・無料枠に余裕あり）": "gemini-flash-lite-latest",
    "Gemini Flash（高性能・無料枠の上限が低い場合あり）": "gemini-flash-latest",
    "Gemini Pro（高精度・無料枠では利用不可の場合あり）": "gemini-pro-latest",
}


def get_api_key() -> str | None:
    # .envなどの環境変数を優先する（サイドバーの手入力欄はその場合非表示になるため、
    # 過去にセッションへ残った古い手入力キーで上書きされないようにする）
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    return st.session_state.get("gemini_api_key")


def get_client() -> genai.Client | None:
    api_key = get_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def render_api_key_sidebar() -> None:
    """全ページ共通：サイドバーにAPIキー入力欄を表示する。"""
    with st.sidebar:
        st.subheader("⚙️ 設定")
        if os.environ.get("GEMINI_API_KEY"):
            st.success("環境変数からAPIキーを読み込み済みです", icon="✅")
        else:
            key_input = st.text_input(
                "Gemini APIキー",
                type="password",
                value=st.session_state.get("gemini_api_key", ""),
                help="https://aistudio.google.com/app/apikey で取得できます。"
                "このセッション内でのみ保持され、保存されません。",
            )
            if key_input:
                st.session_state["gemini_api_key"] = key_input

        if "model_label" not in st.session_state:
            st.session_state["model_label"] = list(MODEL_OPTIONS.keys())[0]

        st.selectbox(
            "使用モデル",
            options=list(MODEL_OPTIONS.keys()),
            key="model_label",
        )
        st.slider(
            "創造性（temperature）",
            min_value=0.0,
            max_value=1.5,
            value=st.session_state.get("temperature", 0.7),
            step=0.1,
            key="temperature",
            help="低いほど堅実・一貫、高いほど自由で多様な出力になります。",
        )


def get_selected_model() -> str:
    label = st.session_state.get("model_label", list(MODEL_OPTIONS.keys())[0])
    return MODEL_OPTIONS[label]


def get_temperature() -> float:
    return st.session_state.get("temperature", 0.7)


def generate_stream(prompt: str, system_instruction: str | None = None):
    """Gemini APIにリクエストを送り、テキストチャンクを順次yieldする。

    503（サーバー混雑）は接続開始時に限り自動リトライする。
    まだ何も出力していない失敗のみ再試行対象とし、途中で切れた場合は
    重複出力を避けるためそのままエラーを送出する。
    """
    client = get_client()
    if client is None:
        raise RuntimeError("Gemini APIキーが設定されていません。サイドバーから入力してください。")

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=get_temperature(),
    )

    attempt = 0
    while True:
        try:
            for chunk in client.models.generate_content_stream(
                model=get_selected_model(),
                contents=prompt,
                config=config,
            ):
                if chunk.text:
                    yield chunk.text
            return
        except errors.ServerError:
            attempt += 1
            if attempt > MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY_SECONDS * attempt)


def require_api_key() -> bool:
    """APIキー未設定の場合は警告を表示してFalseを返す。"""
    if get_api_key() is None:
        st.warning("先にサイドバーからGemini APIキーを入力してください。", icon="🔑")
        return False
    return True


def run_generation(prompt: str, system_instruction: str | None = None) -> str | None:
    """各ページから呼び出す想定のラッパー。ストリーミング生成を行い、
    失敗時は分かりやすいメッセージを表示してNoneを返す（生の例外は出さない）。
    """
    try:
        return st.write_stream(generate_stream(prompt, system_instruction))
    except errors.ServerError:
        st.error(
            "Gemini APIが現在混雑しています（Google側の一時的な問題です）。"
            "少し時間をおいてから、もう一度ボタンを押してください。",
            icon="⏳",
        )
    except errors.ClientError as e:
        if getattr(e, "status", None) == "RESOURCE_EXHAUSTED":
            st.error(
                f"選択中のモデル「{get_selected_model()}」の無料枠の利用上限に達しました。"
                "サイドバーで別のモデル（Flash-Liteなど）に切り替えるか、"
                "しばらく時間をおいてから再度お試しください。",
                icon="📉",
            )
        else:
            st.error(
                f"Gemini APIにリクエストが拒否されました。APIキーやモデル選択をご確認ください。\n\n詳細: {e}",
                icon="🚫",
            )
    except RuntimeError as e:
        st.warning(str(e), icon="🔑")
    return None
