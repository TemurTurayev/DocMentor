"""
DocMentor main application with improved UI/UX.
"""

import streamlit as st
import os
from pathlib import Path
from core.modes import LocalMode, CloudMode
import tempfile
import time

# Configure page
st.set_page_config(
    page_title="DocMentor - AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'processing_stats' not in st.session_state:
    st.session_state.processing_stats = {
        'total_documents': 0,
        'total_chunks': 0,
        'total_queries': 0
    }

def initialize_mode(mode_type: str):
    """Initialize operation mode."""
    base_path = Path(tempfile.gettempdir()) / "docmentor"
    if mode_type == "local":
        return LocalMode(storage_path=base_path / "local")
    else:
        return CloudMode(
            storage_path=base_path / "cloud",
            cloud_endpoint=os.getenv("CLOUD_ENDPOINT", "")
        )

# Header
st.markdown('<div class="main-header">🎓 DocMentor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ваш персональный AI-ассистент для медицинского образования</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Настройки")

    # Mode selector
    mode = st.radio(
        "Режим работы:",
        ["📚 Локальный", "🌐 Облачный"],
        help="Локальный: все данные хранятся локально. Облачный: доступ к общей базе знаний."
    )

    # Initialize or update mode
    current_mode = "local" if mode == "📚 Локальный" else "cloud"
    if st.session_state.current_mode != current_mode:
        with st.spinner("Инициализация режима..."):
            st.session_state.current_mode = current_mode
            st.session_state.mode_handler = initialize_mode(current_mode)
            st.success(f"Режим {mode} активирован!")

    st.divider()

    # Statistics
    st.header("📊 Статистика")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Документов", st.session_state.processing_stats['total_documents'])
        st.metric("Вопросов", st.session_state.processing_stats['total_queries'])
    with col2:
        st.metric("Фрагментов", st.session_state.processing_stats['total_chunks'])
        st.metric("Ответов", len([m for m in st.session_state.chat_history if m['role'] == 'assistant']))

    st.divider()

    # Info section
    st.header("ℹ️ Информация")
    with st.expander("О проекте"):
        st.markdown("""
        **DocMentor** - AI-ассистент для медицинского образования.

        **Возможности:**
        - 📄 Загрузка и анализ PDF документов
        - 🔍 Умный поиск по содержимому
        - 💬 Контекстные ответы на вопросы
        - 📚 Векторная база знаний
        """)

    with st.expander("Как использовать"):
        st.markdown("""
        1. **Загрузите документы** в разделе "Управление документами"
        2. **Дождитесь обработки** - появится зеленое уведомление
        3. **Задайте вопрос** в чате
        4. **Получите ответ** на основе ваших материалов
        """)

    st.divider()

    # Actions
    if st.button("🗑️ Очистить историю", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("💾 Экспорт чата", use_container_width=True):
        if st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{'👤 Вы' if m['role'] == 'user' else '🤖 Ассистент'}: {m['content']}"
                for m in st.session_state.chat_history
            ])
            st.download_button(
                label="⬇️ Скачать",
                data=chat_text,
                file_name=f"docmentor_chat_{int(time.time())}.txt",
                mime="text/plain"
            )
        else:
            st.info("История чата пуста")

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Чат", "📄 Документы", "❓ Помощь"])

with tab1:
    st.header("💬 Чат с ассистентом")

    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(f"**Вопрос:** {message['content']}")
            else:
                with st.chat_message("assistant"):
                    st.markdown(message['content'])
    else:
        st.info("👋 Привет! Я DocMentor. Загрузите документы и задайте вопрос по медицине.")

    # Chat input
    user_question = st.chat_input("Задайте вопрос по медицине...")

    if user_question and st.session_state.current_mode:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.spinner("🔍 Ищу ответ в документах..."):
            try:
                # Search for relevant information
                results = st.session_state.mode_handler.search(
                    user_question,
                    k=4
                )

                # Update stats
                st.session_state.processing_stats['total_queries'] += 1

                # Format and display response
                if results:
                    response = "**На основе ваших материалов:**\n\n"
                    for i, result in enumerate(results, 1):
                        source = result['metadata'].get('filename', 'Документ')
                        response += f"**{i}. 📖 {source}**\n{result['text']}\n\n"
                else:
                    response = "❌ К сожалению, я не нашел релевантной информации в загруженных документах. Попробуйте переформулировать вопрос или загрузите дополнительные материалы."

                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

                st.rerun()

            except Exception as e:
                st.error(f"❌ Ошибка при поиске: {str(e)}")

with tab2:
    st.header("📄 Управление документами")

    # Document upload
    uploaded_files = st.file_uploader(
        "Загрузите PDF файлы учебников или конспектов",
        type=["pdf"],
        accept_multiple_files=True,
        help="Поддерживаются файлы PDF до 200MB"
    )

    if uploaded_files and st.session_state.current_mode:
        process_button = st.button("🚀 Обработать документы", type="primary")

        if process_button:
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Обработка {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))

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

                    # Add to session documents
                    if uploaded_file.name not in [doc['name'] for doc in st.session_state.documents]:
                        st.session_state.documents.append({
                            'name': uploaded_file.name,
                            'chunks': result['chunks'],
                            'metadata': result['metadata']
                        })

                        # Update stats
                        st.session_state.processing_stats['total_documents'] += 1
                        st.session_state.processing_stats['total_chunks'] += result['chunks']

                    st.success(f"✅ {uploaded_file.name} обработан ({result['chunks']} фрагментов)")

                except Exception as e:
                    st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
                finally:
                    # Cleanup
                    if temp_path.exists():
                        temp_path.unlink()

            progress_bar.empty()
            status_text.empty()
            st.balloons()

    # Display document list
    if st.session_state.documents:
        st.divider()
        st.subheader("📚 Загруженные документы")

        for doc in st.session_state.documents:
            with st.expander(f"📖 {doc['name']} ({doc['chunks']} фрагментов)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Название:**", doc['metadata'].get('title', doc['name']))
                    st.write("**Фрагментов:**", doc['chunks'])
                with col2:
                    st.write("**Режим:**", doc['metadata'].get('mode', 'N/A'))
                    st.write("**Страниц:**", doc['metadata'].get('total_pages', 'N/A'))
    else:
        st.info("📭 Документы еще не загружены. Используйте форму выше для загрузки.")

with tab3:
    st.header("❓ Помощь")

    st.markdown("""
    ### 🚀 Быстрый старт

    1. **Выберите режим работы** в боковой панели
    2. **Загрузите PDF документы** во вкладке "Документы"
    3. **Задайте вопрос** во вкладке "Чат"

    ---

    ### 📚 Режимы работы

    **📚 Локальный режим:**
    - Все данные хранятся на вашем компьютере
    - Работает без интернета
    - Максимальная конфиденциальность

    **🌐 Облачный режим:**
    - Доступ к общей базе знаний
    - Синхронизация между устройствами
    - Расширенные возможности

    ---

    ### 💡 Советы по использованию

    - Загружайте учебники по одной теме для лучших результатов
    - Формулируйте вопросы конкретно и ясно
    - Используйте медицинскую терминологию
    - Проверяйте информацию в первоисточниках

    ---

    ### 🆘 Поддержка

    **Возникли проблемы?**
    - 📧 Email: temurturayev7822@gmail.com
    - 📱 Telegram: @Turayev_Temur
    - 🌐 GitHub: [TemurTurayev/DocMentor](https://github.com/TemurTurayev/DocMentor)

    ---

    ### 📖 Версия

    DocMentor v0.2.0 - Персональный AI-ассистент для медицинского образования
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    Сделано с ❤️ для студентов-медиков | DocMentor v0.2.0
</div>
""", unsafe_allow_html=True)
