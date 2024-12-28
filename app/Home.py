import streamlit as st

st.set_page_config(
    page_title="DocMentor - AI Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

st.title("🎓 DocMentor")
st.subheader("Ваш персональный AI-ассистент для медицинского образования")

# Mode selector
mode = st.radio(
    "Выберите режим работы:",
    ["📚 Приватный", "🌐 Общественный"],
    horizontal=True,
    help="В приватном режиме все данные хранятся локально. В общественном доступна расширенная база знаний."
)

# File uploader
st.subheader("📄 Загрузка документов")
uploaded_files = st.file_uploader(
    "Загрузите PDF файлы учебников или конспектов",
    type=["pdf"],
    accept_multiple_files=True
)

# Chat interface
st.subheader("💬 Чат с ассистентом")
user_question = st.text_input("Задайте вопрос по медицине:", placeholder="Например: Опишите патогенез бронхиальной астмы")

if user_question:
    st.info("🤖 Функционал чата будет добавлен позже...")