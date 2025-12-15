"""
Virtual Patients - Interactive clinical scenarios with AI patients.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.virtual_patient import AIPatient, ScenarioManager, PatientLoader
from core import DocMentorCore

# Page config
st.set_page_config(
    page_title="Виртуальные пациенты - DocMentor",
    page_icon="👨‍⚕️",
    layout="wide"
)

# Initialize session state
if 'docmentor' not in st.session_state:
    st.session_state.docmentor = DocMentorCore()

if 'patient_loader' not in st.session_state:
    st.session_state.patient_loader = PatientLoader()

if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None

if 'ai_patient' not in st.session_state:
    st.session_state.ai_patient = None

if 'scenario_manager' not in st.session_state:
    st.session_state.scenario_manager = None

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Custom CSS
st.markdown("""
<style>
    .patient-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .stage-anamnesis { background-color: #e3f2fd; color: #1976d2; }
    .stage-examination { background-color: #f3e5f5; color: #7b1fa2; }
    .stage-diagnosis { background-color: #fff3e0; color: #f57c00; }
    .stage-treatment { background-color: #e8f5e9; color: #388e3c; }
    .stage-completed { background-color: #c8e6c9; color: #2e7d32; }

    .score-excellent { color: #4caf50; font-weight: bold; }
    .score-good { color: #8bc34a; font-weight: bold; }
    .score-fair { color: #ff9800; font-weight: bold; }
    .score-poor { color: #f44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("👨‍⚕️ Виртуальные пациенты")
st.markdown("Интерактивные клинические сценарии с AI-пациентами")

# Check if LLM is available
llm_available = st.session_state.docmentor.is_llm_available()

if not llm_available:
    st.warning("⚠️ **LLM не загружен!** Виртуальные пациенты используют AI для реалистичных диалогов.")
    st.info("Запусти: `python setup_llm.py` для установки LLM модели.")
    st.stop()

# Sidebar - Patient selection or info
with st.sidebar:
    if st.session_state.current_patient is None:
        # No patient selected - show selection
        st.header("📋 Выбор пациента")

        # Filter options
        st.subheader("Фильтры")

        all_cases = st.session_state.patient_loader.list_all_cases()

        if not all_cases:
            st.error("Нет доступных случаев!")
            st.info("Случаи должны быть в: `core/modules/virtual_patient/examples/`")
            st.stop()

        # Specialty filter
        specialties = list(set([c.get("specialty", "general") for c in all_cases]))
        specialty_filter = st.selectbox("Специальность", ["Все"] + specialties)

        # Difficulty filter
        difficulty_filter = st.select_slider(
            "Сложность",
            options=[1, 2, 3, 4, 5],
            value=3
        )

        # Filter cases
        if specialty_filter == "Все":
            filtered_cases = all_cases
        else:
            filtered_cases = [c for c in all_cases if c.get("specialty") == specialty_filter]

        filtered_cases = [c for c in filtered_cases if c.get("difficulty", 3) == difficulty_filter]

        st.write(f"**Найдено случаев:** {len(filtered_cases)}")

        # Show available cases
        if filtered_cases:
            st.subheader("Доступные случаи")

            for case in filtered_cases:
                with st.expander(f"👤 {case['name']}, {case['age']} лет"):
                    st.write(f"**Пол:** {case['gender']}")
                    st.write(f"**Жалобы:** {', '.join(case['chief_complaint'][:2])}")
                    st.write(f"**Сложность:** {'⭐' * case['difficulty']}")

                    if st.button(f"Начать консультацию", key=f"start_{case['id']}"):
                        # Load full case
                        patient_data = st.session_state.patient_loader.load_case(case['id'])

                        if patient_data:
                            # Initialize AI patient
                            ai_patient = AIPatient(
                                patient_data=patient_data,
                                llm_pipeline=st.session_state.docmentor.rag_pipeline,
                                language="russian"
                            )

                            # Initialize scenario manager
                            scenario_mgr = ScenarioManager(
                                patient_data=patient_data,
                                ai_patient=ai_patient
                            )

                            st.session_state.current_patient = patient_data
                            st.session_state.ai_patient = ai_patient
                            st.session_state.scenario_manager = scenario_mgr
                            st.session_state.chat_messages = []

                            st.rerun()
        else:
            st.info("Нет случаев с такими фильтрами")

    else:
        # Patient selected - show info
        patient = st.session_state.current_patient
        ai_patient = st.session_state.ai_patient
        scenario = st.session_state.scenario_manager

        st.header("📊 Информация о пациенте")

        st.write(f"**Имя:** {patient['name']}")
        st.write(f"**Возраст:** {patient['age']} лет")
        st.write(f"**Пол:** {patient['gender']}")

        # Current stage
        stage = scenario.get_current_stage()
        stage_names = {
            "anamnesis": "Сбор анамнеза",
            "examination": "Осмотр",
            "diagnosis": "Диагноз",
            "treatment": "Лечение",
            "completed": "Завершено"
        }

        stage_classes = {
            "anamnesis": "stage-anamnesis",
            "examination": "stage-examination",
            "diagnosis": "stage-diagnosis",
            "treatment": "stage-treatment",
            "completed": "stage-completed"
        }

        st.markdown(
            f'<span class="stage-badge {stage_classes.get(stage, "")}">{stage_names.get(stage, stage)}</span>',
            unsafe_allow_html=True
        )

        st.divider()

        # Progress
        progress = ai_patient.get_progress()
        st.subheader("Прогресс")
        st.progress(progress['completeness'] / 100)
        st.caption(f"{progress['completeness']}% информации собрано")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Вопросов", progress['questions_asked'])
        with col2:
            st.metric("Сообщений", progress['total_messages'])

        st.divider()

        # Actions
        st.subheader("⚡ Действия")

        # Next stage button
        can_proceed, message = scenario.can_proceed_to_next_stage()

        if can_proceed and stage != "completed":
            if st.button("➡️ Следующий этап", use_container_width=True, type="primary"):
                result = scenario.proceed_to_next_stage()
                if result["status"] == "success":
                    st.success(result["message"])
                    st.rerun()
        else:
            if stage != "completed":
                st.info(message)

        # Complete case
        if stage == "treatment":
            if st.button("✅ Завершить случай", use_container_width=True):
                scenario.set_final_diagnosis(
                    scenario.student_decisions.get("differential_diagnosis", [{}])[0].get("diagnosis", "Не указан")
                    if scenario.student_decisions.get("differential_diagnosis") else "Не указан"
                )
                result = scenario.proceed_to_next_stage()
                st.rerun()

        # Reset button
        if st.button("🔄 Начать заново", use_container_width=True):
            st.session_state.current_patient = None
            st.session_state.ai_patient = None
            st.session_state.scenario_manager = None
            st.session_state.chat_messages = []
            st.rerun()

# Main area
if st.session_state.current_patient is None:
    # No patient selected
    st.info("👈 Выбери пациента в боковой панели, чтобы начать")

    # Show statistics
    col1, col2, col3 = st.columns(3)

    all_cases = st.session_state.patient_loader.list_all_cases()

    with col1:
        st.metric("Всего случаев", len(all_cases))

    with col2:
        specialties = set([c.get("specialty", "general") for c in all_cases])
        st.metric("Специальностей", len(specialties))

    with col3:
        avg_difficulty = sum([c.get("difficulty", 3) for c in all_cases]) / len(all_cases) if all_cases else 0
        st.metric("Средняя сложность", f"{avg_difficulty:.1f}/5")

    # Show example cases
    st.subheader("📚 Доступные случаи")

    for case in all_cases[:5]:  # Show first 5
        with st.expander(f"👤 {case['name']} - {case['diagnosis']}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Возраст:** {case['age']} лет")
                st.write(f"**Пол:** {case['gender']}")
                st.write(f"**Специальность:** {case['specialty']}")
                st.write(f"**Жалобы:** {', '.join(case['chief_complaint'])}")

            with col2:
                st.write(f"**Сложность:**")
                st.write("⭐" * case.get('difficulty', 3))

else:
    # Patient selected - show interaction
    patient = st.session_state.current_patient
    ai_patient = st.session_state.ai_patient
    scenario = st.session_state.scenario_manager
    stage = scenario.get_current_stage()

    # Different UI based on stage
    if stage == "completed":
        # Show evaluation and feedback
        st.success("✅ Консультация завершена!")

        # Get evaluation
        anamnesis_eval = ai_patient.get_evaluation()
        diagnosis_eval = scenario.evaluate_diagnosis()
        treatment_eval = scenario.evaluate_treatment()
        expert_feedback = scenario.get_expert_feedback()

        # Overall score
        total_score = (anamnesis_eval['percentage'] + diagnosis_eval['score'] + treatment_eval['score']) / 3

        st.subheader("📊 Итоговая оценка")

        # Score color
        if total_score >= 80:
            score_class = "score-excellent"
            emoji = "🎉"
        elif total_score >= 60:
            score_class = "score-good"
            emoji = "👍"
        elif total_score >= 40:
            score_class = "score-fair"
            emoji = "😐"
        else:
            score_class = "score-poor"
            emoji = "📚"

        st.markdown(
            f'<h1 class="{score_class}">{emoji} {total_score:.1f}%</h1>',
            unsafe_allow_html=True
        )

        # Detailed scores
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Сбор анамнеза", f"{anamnesis_eval['percentage']:.1f}%")
        with col2:
            st.metric("Диагностика", f"{diagnosis_eval['score']:.1f}%")
        with col3:
            st.metric("Лечение", f"{treatment_eval['score']:.1f}%")

        # Feedback tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Анамнез", "🔬 Диагноз", "💊 Лечение", "👨‍⚕️ Эксперт"])

        with tab1:
            st.subheader("Сбор анамнеза")
            for feedback in anamnesis_eval['feedback']:
                st.write(feedback)

            with st.expander("Детали оценки"):
                st.write(f"**Информация:** {anamnesis_eval['details']['information_gathered']:.1f}/40")
                st.write(f"**Качество вопросов:** {anamnesis_eval['details']['question_quality']:.1f}/30")
                st.write(f"**Эффективность:** {anamnesis_eval['details']['efficiency']:.1f}/20")
                st.write(f"**Эмпатия:** {anamnesis_eval['details']['empathy']}/10")

        with tab2:
            st.subheader("Дифференциальная диагностика")

            st.write("**Твой диагноз:**")
            for dx in diagnosis_eval['student']:
                st.write(f"- {dx}")

            st.write("**Правильные диагнозы:**")
            for dx in diagnosis_eval['correct_diagnoses']:
                st.success(f"✅ {dx['student']}")

            if diagnosis_eval['missed_diagnoses']:
                st.write("**Пропущено:**")
                for dx in diagnosis_eval['missed_diagnoses']:
                    st.error(f"❌ {dx}")

            if diagnosis_eval['incorrect_diagnoses']:
                st.write("**Неверные:**")
                for dx in diagnosis_eval['incorrect_diagnoses']:
                    st.warning(f"⚠️ {dx}")

        with tab3:
            st.subheader("План лечения")

            st.write("**Твой план:**")
            for tx in scenario.student_decisions['treatment_plan']:
                st.write(f"- {tx['treatment']}")

            st.write(f"**Оценка:** {treatment_eval['score']:.1f}%")
            st.write(f"**Совпадений:** {treatment_eval['matches']}/{treatment_eval['total_expected']}")

        with tab4:
            st.subheader("Экспертное мнение")

            st.write(f"**Окончательный диагноз:** {expert_feedback['final_diagnosis']}")

            st.write("**Обоснование:**")
            st.info(expert_feedback['reasoning'])

            st.write("**Ключевые находки:**")
            for finding in expert_feedback['key_findings']:
                st.write(f"- {finding}")

            if expert_feedback.get('treatment_rationale'):
                st.write("**Обоснование лечения:**")
                st.write(expert_feedback['treatment_rationale'])

    elif stage in ["anamnesis", "examination"]:
        # Chat interface for anamnesis and examination
        st.subheader(f"💬 {'Сбор анамнеза' if stage == 'anamnesis' else 'Физикальный осмотр'}")

        # Instructions
        if stage == "anamnesis":
            st.info("📝 Задавай вопросы пациенту свободным текстом. AI будет отвечать как настоящий пациент.")
        else:
            # Show examination data
            exam_data = scenario.get_examination_data()

            if exam_data['available']:
                with st.expander("📋 Данные осмотра", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Витальные показатели:**")
                        for key, value in exam_data['vitals'].items():
                            st.write(f"- {key}: {value}")

                    with col2:
                        st.write("**Общее состояние:**")
                        st.write(exam_data['general'])

                st.info("💬 Можешь задать уточняющие вопросы пациенту об осмотре.")

        # Chat history
        chat_container = st.container()

        with chat_container:
            for msg in st.session_state.chat_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                with st.chat_message(role):
                    st.markdown(content)

                    # Show feedback if available
                    if role == "assistant" and msg.get("feedback"):
                        feedback = msg["feedback"]
                        if feedback.get("tips"):
                            with st.expander("💡 Подсказка"):
                                for tip in feedback["tips"]:
                                    st.write(tip)

        # Chat input
        user_input = st.chat_input("Напиши вопрос пациенту...")

        if user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })

            # Get AI response
            with st.spinner("🤖 Пациент думает..."):
                response = ai_patient.chat(user_input)

            if response["status"] == "success":
                # Add AI response
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "feedback": response.get("feedback")
                })
            else:
                st.error(f"Ошибка: {response.get('error')}")

            st.rerun()

    elif stage == "diagnosis":
        # Diagnosis formulation
        st.subheader("🔬 Постановка диагноза")

        st.info("📝 Сформулируй дифференциальный диагноз на основе собранной информации.")

        # Show collected information
        with st.expander("📊 Собранная информация"):
            progress = ai_patient.get_progress()
            st.write(f"**Собрано:** {progress['completeness']}% информации")

            revealed = progress['revealed_info']
            for key, value in revealed.items():
                st.write(f"- {key}: {'✅' if value else '❌'}")

        # Diagnosis input
        st.write("**Дифференциальный диагноз:**")

        num_diagnoses = st.number_input("Сколько диагнозов в дифф. диагнозе?", min_value=1, max_value=5, value=3)

        for i in range(int(num_diagnoses)):
            col1, col2 = st.columns([3, 1])

            with col1:
                dx = st.text_input(f"Диагноз {i+1}", key=f"dx_{i}")

            with col2:
                prob = st.slider("Вероятность %", 0, 100, 50, key=f"prob_{i}")

            if dx and st.button(f"Добавить диагноз {i+1}", key=f"add_dx_{i}"):
                scenario.add_differential_diagnosis(dx, prob)
                st.success(f"✅ Добавлен: {dx}")

        # Show current diagnoses
        if scenario.student_decisions['differential_diagnosis']:
            st.write("**Текущие диагнозы:**")
            for dx in scenario.student_decisions['differential_diagnosis']:
                st.write(f"- {dx['diagnosis']} ({dx['probability']}%)")

    elif stage == "treatment":
        # Treatment planning
        st.subheader("💊 План лечения")

        st.info("📝 Составь план лечения для пациента.")

        # Show diagnosis
        if scenario.student_decisions['differential_diagnosis']:
            st.write("**Твой диагноз:**")
            for dx in scenario.student_decisions['differential_diagnosis']:
                st.write(f"- {dx['diagnosis']} ({dx['probability']}%)")

        # Treatment categories
        treatment_category = st.selectbox(
            "Категория",
            ["Медикаментозное", "Режим", "Диета", "Рекомендации", "Обследование"]
        )

        treatment_text = st.text_area("Назначение")

        if st.button("➕ Добавить в план"):
            if treatment_text:
                scenario.add_treatment(treatment_text, treatment_category)
                st.success("✅ Добавлено в план лечения")

        # Show current plan
        if scenario.student_decisions['treatment_plan']:
            st.write("**Текущий план лечения:**")
            for tx in scenario.student_decisions['treatment_plan']:
                st.write(f"- [{tx['category']}] {tx['treatment']}")

# Footer
st.divider()
st.caption("DocMentor 2.1 - Виртуальные пациенты с AI | Сделано для студентов-медиков")
