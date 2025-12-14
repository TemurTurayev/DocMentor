"""
DocMentor 2.0 - Упрощенная версия с фокусом на практику.
"""

import streamlit as st
import os
from pathlib import Path
from core import DocMentorCore
import tempfile
import time

# Configure page
st.set_page_config(
    page_title="DocMentor 2.0 - AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'docmentor' not in st.session_state:
    base_path = Path(tempfile.gettempdir()) / "docmentor_data"
    st.session_state.docmentor = DocMentorCore(storage_path=base_path)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown('<div class="main-header">🎓 DocMentor 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-ассистент для медицинского образования</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Статистика")

    stats = st.session_state.docmentor.get_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Документов", stats['total_documents'])
    with col2:
        st.metric("Фрагментов", stats['total_chunks'])

    st.metric("Вопросов задано", len([m for m in st.session_state.chat_history if m['role'] == 'user']))

    st.divider()

    # Quick actions
    st.header("⚡ Быстрые действия")

    if st.button("🗑️ Очистить историю", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("💾 Экспорт чата", use_container_width=True):
        if st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{'👤 Вы' if m['role'] == 'user' else '🤖 DocMentor'}: {m['content']}"
                for m in st.session_state.chat_history
            ])
            st.download_button(
                label="⬇️ Скачать",
                data=chat_text,
                file_name=f"docmentor_chat_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("История пуста")

    if st.button("🧹 Очистить кэш", use_container_width=True):
        st.session_state.docmentor.clear_cache()
        st.success("Кэш очищен!")

    st.divider()

    # Info
    st.header("ℹ️ О проекте")
    st.markdown("""
    **DocMentor 2.0** - упрощенная версия с фокусом на практику.

    **Что нового:**
    - ✅ Простая архитектура
    - ✅ Быстрая работа
    - ✅ Локальное хранение
    - 🔜 Виртуальные пациенты
    - 🔜 Тестирование знаний
    - 🔜 Локальная LLM
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Чат", "📄 Документы", "👨‍⚕️ Виртуальные пациенты"])

# === TAB 1: Чат ===
with tab1:
    st.header("💬 Умный поиск по учебникам")

    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message['content'])
    else:
        st.info("👋 Привет! Загрузи учебники во вкладке 'Документы' и задай вопрос.")

    # Chat input
    user_question = st.chat_input("Задай вопрос по медицине...")

    if user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # Search and respond
        with st.chat_message("assistant"):
            with st.spinner("🔍 Ищу ответ..."):
                try:
                    results = st.session_state.docmentor.search(user_question, k=3)

                    if results:
                        response = "**Нашел в твоих учебниках:**\n\n"
                        for i, result in enumerate(results, 1):
                            source = result['metadata'].get('filename', 'Неизвестно')
                            response += f"**{i}. 📖 {source}**\n{result['text']}\n\n"

                        # Add note about future LLM
                        response += "\n---\n💡 *В следующей версии здесь будет AI-объяснение на основе этих фрагментов!*"
                    else:
                        response = "❌ Не нашел информации в загруженных документах.\n\n**Советы:**\n- Проверь, загружены ли нужные учебники\n- Попробуй переформулировать вопрос\n- Используй медицинские термины"

                    st.markdown(response)

                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")

# === TAB 2: Документы ===
with tab2:
    st.header("📄 Управление документами")

    # Upload section
    st.subheader("📤 Загрузка")

    uploaded_files = st.file_uploader(
        "Выбери PDF файлы",
        type=["pdf"],
        accept_multiple_files=True,
        help="Учебники, лекции, конспекты - все в формате PDF"
    )

    if uploaded_files:
        if st.button("🚀 Обработать документы", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"⚙️ Обрабатываю {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))

                # Save temp
                temp_dir = Path(tempfile.gettempdir()) / "docmentor_uploads"
                temp_dir.mkdir(exist_ok=True)
                temp_path = temp_dir / uploaded_file.name

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                try:
                    result = st.session_state.docmentor.process_document(
                        temp_path,
                        metadata={"source": "user_upload"}
                    )

                    st.success(f"✅ {uploaded_file.name} - {result['chunks']} фрагментов")

                except Exception as e:
                    st.error(f"❌ Ошибка с {uploaded_file.name}: {str(e)}")
                finally:
                    if temp_path.exists():
                        temp_path.unlink()

            progress_bar.empty()
            status_text.empty()
            st.balloons()
            st.rerun()

    # Documents list
    st.divider()
    st.subheader("📚 Загруженные документы")

    documents = st.session_state.docmentor.get_documents()

    if documents:
        for doc in documents:
            with st.expander(f"📖 {doc['filename']} ({doc['size_mb']} MB)"):
                st.write(f"**Путь:** `{doc['path']}`")
    else:
        st.info("📭 Пока нет документов. Загрузи выше!")

# === TAB 3: Виртуальные пациенты ===
with tab3:
    st.header("👨‍⚕️ Виртуальные пациенты")

    st.info("🚧 **В разработке!**\n\nСкоро здесь появятся интерактивные клинические сценарии для отработки практических навыков.")

    st.markdown("""
    ### Что будет:
    - 🏥 Интерактивные клинические случаи
    - 🔍 Пошаговая диагностика
    - 💊 Выбор тактики лечения
    - 📊 Оценка твоих действий
    - 📈 Статистика прогресса

    ### Примеры случаев:
    - Острый аппендицит
    - Бронхиальная астма
    - Инфаркт миокарда
    - Менингит у ребенка
    - ...и многое другое!

    **Следи за обновлениями!** 🚀
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    DocMentor 2.0 - Сделано с ❤️ для студентов-медиков |
    <a href="https://github.com/TemurTurayev/DocMentor" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
