"""
DocMentor main application.
"""

import streamlit as st
import os
from pathlib import Path
from core.modes import PrivateMode, PublicMode
import tempfile

# Configure page
st.set_page_config(
    page_title="DocMentor - AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
)

# Initialize session state
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents' not in st.session_state:
    st.session_state.documents = []

def initialize_mode(mode_type: str):
    """Initialize operation mode."""
    base_path = Path(tempfile.gettempdir()) / "docmentor"
    if mode_type == "private":
        return PrivateMode(storage_path=base_path / "private")
    else:
        return PublicMode(storage_path=base_path / "public")

# Title and description
st.title("🎓 DocMentor")
st.subheader("Ваш персональный AI-ассистент для медицинского образования")

# Mode selector
with st.expander("⚙️ Настройки режима работы", expanded=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        mode = st.radio(
            "Выберите режим работы:",
            ["📚 Приватный", "🌐 Общественный"],
            horizontal=True,
            help="В приватном режиме все данные хранятся локально. В общественном доступна расширенная база знаний.",
            key="mode_selector"
        )

    # Initialize or update mode
    current_mode = "private" if mode == "📚 Приватный" else "public"
    if st.session_state.current_mode != current_mode:
        st.session_state.current_mode = current_mode
        st.session_state.mode_handler = initialize_mode(current_mode)
        st.rerun()

# Document management
st.subheader("📄 Управление документами")

# Document upload
uploaded_files = st.file_uploader(
    "Загрузите PDF файлы учебников или конспектов",
    type=["pdf"],
    accept_multiple_files=True,
    help="Поддерживаются файлы PDF до 200MB"
)

# Process uploaded documents
if uploaded_files:
    with st.spinner("Обработка документов..."):
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily
            temp_dir = Path(tempfile.gettempdir()) / "docmentor_uploads"
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / uploaded_file.name
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            try:
                # Process document
                result = st.session_state.mode_handler.process_document(
                    temp_path,
                    metadata={"source": uploaded_file.name}
                )
                st.success(f"✅ Документ {uploaded_file.name} успешно обработан")
                
                # Add to session documents
                if uploaded_file.name not in [doc['name'] for doc in st.session_state.documents]:
                    st.session_state.documents.append({
                        'name': uploaded_file.name,
                        'metadata': result['metadata']
                    })
                    
            except Exception as e:
                st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
            finally:
                # Cleanup
                if temp_path.exists():
                    temp_path.unlink()

# Display document list
if st.session_state.documents:
    st.write("📚 Загруженные документы:")
    for doc in st.session_state.documents:
        with st.expander(f"📖 {doc['name']}"):
            st.json(doc['metadata'])

# Chat interface
st.subheader("💬 Чат с ассистентом")

# Chat input
user_question = st.text_input(
    "Задайте вопрос по медицине:",
    placeholder="Например: Опишите патогенез бронхиальной астмы"
)

if user_question:
    with st.spinner("Поиск ответа..."):
        try:
            # Search for relevant information
            results = st.session_state.mode_handler.search(
                user_question,
                k=4
            )
            
            # Add to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })
            
            # Format and display response
            if results:
                response = "На основе доступных материалов:\n\n"
                for result in results:
                    response += f"📖 {result['metadata'].get('filename', 'Документ')}:\n{result['text']}\n\n"
            else:
                response = "К сожалению, я не нашел релевантной информации в загруженных документах."
                
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            st.error(f"❌ Ошибка при поиске ответа: {str(e)}")

# Display chat history
st.write("📜 История диалога:")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"👤 **Вы**: {message['content']}")
    else:
        st.markdown(f"🤖 **Ассистент**: {message['content']}")

# Settings and information
with st.sidebar:
    st.header("ℹ️ Информация")
    st.markdown("""
    **DocMentor** - это AI-ассистент для медицинского образования.
    
    **Режимы работы:**
    - 📚 Приватный: все данные хранятся локально
    - 🌐 Общественный: доступ к общей базе знаний
    
    **Возможности:**
    - Загрузка и анализ медицинских учебников
    - Умный поиск по содержимому
    - Контекстные ответы на вопросы
    """)
    
    if st.button("🗑️ Очистить историю"):
        st.session_state.chat_history = []
        st.rerun()