from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Space Explorer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }

        header {
            visibility: hidden;
        }

        #MainMenu {
            visibility: hidden;
        }

        iframe {
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

game_path = Path(__file__).parent / "game.html"
game_html = game_path.read_text(encoding="utf-8")

components.html(game_html, height=900, scrolling=False)
