"""
Chat interface components.
"""

import streamlit as st
from typing import List, Dict
from datetime import datetime

def format_message(message: Dict) -> str:
    """Format chat message with Markdown."""
    role_icons = {
        "user": "👤",
        "assistant": "🤖",
        "system": "⚙️"
    }
    
    icon = role_icons.get(message["role"], "❔")
    timestamp = datetime.now().strftime("%H:%M")
    
    return f"{icon} **{message['role'].title()}** [{timestamp}]:\n{message['content']}"

def display_chat_history(messages: List[Dict]):
    """Display chat history with styling."""
    for msg in messages:
        with st.container():
            st.markdown(format_message(msg))
            st.divider()

def chat_input_area() -> str:
    """Render chat input area with styling."""
    return st.text_input(
        "Задайте вопрос по медицине:",
        placeholder="Например: Опишите патогенез бронхиальной астмы",
        key="chat_input"
    )

def display_citations(citations: List[Dict]):
    """Display search results and citations."""
    if not citations:
        return
        
    st.markdown("### 📚 Источники:")
    for citation in citations:
        with st.expander(f"📖 {citation['metadata'].get('filename', 'Источник')}"):
            st.markdown(f"**Релевантность:** {citation['score']:.2f}")
            st.markdown(citation['text'])