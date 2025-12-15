"""
DocMentor 2.1 - С интеграцией локального LLM.
"""

import streamlit as st
import os
from pathlib import Path
from core import DocMentorCore
import tempfile
import time

# Configure page
st.set_page_config(
    page_title="DocMentor 2.1 - AI Medical Assistant",
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
st.markdown('<div class="main-header">🎓 DocMentor 2.1</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-ассистент для медицинского образования с локальным LLM</div>', unsafe_allow_html=True)

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

    # LLM Status
    if st.session_state.docmentor.is_llm_available():
        llm_stats = st.session_state.docmentor.get_llm_stats()
        st.success(f"🤖 LLM: Активен ({llm_stats['total_requests']} запросов)")
    else:
        st.warning("🤖 LLM: Не загружен")
        if st.button("📥 Установить LLM", use_container_width=True):
            st.info("Запусти: `python setup_llm.py`")

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
    **DocMentor 2.1** - с локальным AI.

    **Новое:**
    - ✅ Локальный LLM (Qwen2.5-7B)
    - ✅ RAG Pipeline
    - ✅ AI режим в чате
    - ✅ GGUF квантизация
    - ✅ Metal acceleration (M4)

    **Скоро:**
    - 🔜 Виртуальные пациенты с AI
    - 🔜 AI тестирование знаний
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Чат", "📄 Документы", "👨‍⚕️ Виртуальные пациенты"])

# === TAB 1: Чат ===
with tab1:
    # AI Mode toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("💬 Умный поиск по учебникам")
    with col2:
        if st.session_state.docmentor.is_llm_available():
            use_ai = st.toggle("🤖 AI режим", value=True, help="Использовать локальный LLM для генерации ответов")
        else:
            use_ai = False
            st.info("AI недоступен")

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

        # Generate response
        with st.chat_message("assistant"):
            if use_ai and st.session_state.docmentor.is_llm_available():
                # AI MODE - Use RAG pipeline
                with st.spinner("🤖 AI думает..."):
                    try:
                        result = st.session_state.docmentor.ask_ai(
                            question=user_question,
                            use_context=True,
                            max_tokens=512,
                            temperature=0.7
                        )

                        if result["status"] == "success":
                            # Display AI answer
                            st.markdown(result["answer"])

                            # Show sources if available
                            if result.get("sources"):
                                with st.expander(f"📚 Источники ({len(result['sources'])} фрагментов)"):
                                    for i, source in enumerate(result['sources'], 1):
                                        st.markdown(f"**{i}. {source['metadata'].get('filename', 'Unknown')}**")
                                        st.caption(source['text'][:200] + "...")
                                        st.caption(f"Релевантность: {source['score']:.2f}")

                            # Show stats
                            meta = result["metadata"]
                            st.caption(f"⚡ Сгенерировано за {meta['time_seconds']:.1f}s ({meta['tokens_per_second']:.1f} t/s)")

                            response = result["answer"]
                        else:
                            error_msg = f"❌ AI ошибка: {result.get('error', 'Unknown')}"
                            st.error(error_msg)
                            response = error_msg

                    except Exception as e:
                        error_msg = f"❌ Ошибка AI: {str(e)}"
                        st.error(error_msg)
                        response = error_msg

            else:
                # SIMPLE MODE - Vector search only
                with st.spinner("🔍 Ищу ответ..."):
                    try:
                        results = st.session_state.docmentor.search(user_question, k=3)

                        if results:
                            response = "**Нашел в твоих учебниках:**\n\n"
                            for i, result in enumerate(results, 1):
                                source = result['metadata'].get('filename', 'Неизвестно')
                                response += f"**{i}. 📖 {source}**\n{result['text']}\n\n"

                            # Add note about AI mode
                            if not st.session_state.docmentor.is_llm_available():
                                response += "\n---\n💡 *Установи LLM (`python setup_llm.py`) для AI-объяснений!*"
                        else:
                            response = "❌ Не нашел информации в загруженных документах.\n\n**Советы:**\n- Проверь, загружены ли нужные учебники\n- Попробуй переформулировать вопрос\n- Используй медицинские термины"

                        st.markdown(response)

                    except Exception as e:
                        response = f"❌ Ошибка: {str(e)}"
                        st.error(response)

            # Add to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

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

    if not st.session_state.docmentor.is_llm_available():
        st.warning("⚠️ **LLM не загружен!** Виртуальные пациенты требуют AI.")
        st.info("Запусти: `python setup_llm.py` для установки LLM модели.")
    else:
        st.success("✅ **AI-пациенты доступны!**")

    st.markdown("""
    ### 🎯 Что это?

    **Виртуальные пациенты** - это интерактивные клинические сценарии с AI-пациентами,
    которые реагируют на твои вопросы как настоящие люди!

    ### ✨ Возможности:

    - 💬 **Свободный диалог** - задавай любые вопросы, AI ответит естественно
    - 🔄 **4 этапа консультации**: Анамнез → Осмотр → Диагноз → Лечение
    - 📊 **Оценка работы** - получи детальную обратную связь (100 баллов)
    - 👨‍⚕️ **Экспертное мнение** - узнай правильный подход в конце

    ### 📚 Доступные случаи:

    - 🫀 **Гипертонический криз** (Терапия, ⭐⭐⭐)
    - 🫁 **Внебольничная пневмония** (Терапия, ⭐⭐)
    - 🤒 **Бронхиальная астма** (Пульмонология, ⭐⭐⭐)
    - 🏥 **Острый аппендицит** (Хирургия, ⭐⭐⭐⭐)

    ### 🚀 Начать практику:

    Открой страницу **"Virtual Patients"** в боковой панели слева!
    """)

    # Quick link
    st.info("👈 Найди страницу **Virtual Patients** в боковой панели для начала!")

    # Show statistics
    from core.virtual_patient import PatientLoader

    try:
        loader = PatientLoader()
        cases = loader.list_all_cases()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего случаев", len(cases))

        with col2:
            specialties = set([c.get("specialty", "general") for c in cases])
            st.metric("Специальностей", len(specialties))

        with col3:
            avg_diff = sum([c.get("difficulty", 3) for c in cases]) / len(cases) if cases else 0
            st.metric("Средняя сложность", f"{avg_diff:.1f}/5")

    except Exception as e:
        st.error(f"Ошибка загрузки статистики: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    DocMentor 2.0 - Сделано с ❤️ для студентов-медиков |
    <a href="https://github.com/TemurTurayev/DocMentor" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
