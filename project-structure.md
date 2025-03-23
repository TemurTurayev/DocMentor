# Обновленная структура проекта DocMentor

```
DocMentor/
├── LICENSE
├── README.md
├── ARCHITECTURE.md                    # Новый файл с описанием архитектуры
├── CONTRIBUTING.md                    # Рекомендации для контрибьюторов
├── .repo-metadata.json
├── requirements.txt
│
├── app/                               # Веб-интерфейс (Streamlit)
│   ├── Home.py                        # Главная страница
│   ├── config.py                      # Конфигурация приложения
│   ├── components/                    # UI компоненты
│   │   ├── chat.py
│   │   ├── pdf_preview.py             # Предпросмотр PDF
│   │   ├── virtual_patient.py         # Новый компонент для виртуальных пациентов
│   │   ├── gamification.py            # Новый компонент для геймификации
│   │   ├── adaptive_learning.py       # Новый компонент для адаптивного обучения
│   │   ├── image_analyzer.py          # Новый компонент для анализа медицинских изображений
│   │   └── social.py                  # Новый компонент для социальной платформы
│   └── pages/                         # Дополнительные страницы
│       ├── virtual_patients.py        # Страница виртуальных пациентов
│       ├── study_materials.py         # Страница учебных материалов
│       ├── achievements.py            # Страница достижений (геймификация)
│       ├── social.py                  # Страница социальной платформы
│       └── settings.py                # Страница настроек
│
├── core/                              # Ядро DocMentor
│   ├── modes/                         # Режимы работы
│   │   ├── __init__.py
│   │   ├── base_mode.py
│   │   ├── private_mode.py            # Переименовать в local_mode.py
│   │   ├── public_mode.py             # Переименовать в cloud_mode.py
│   │   ├── hybrid_mode.py             # Новый режим гибридной работы
│   │   ├── enhanced_model.py
│   │   └── mode_manager.py
│   │
│   ├── tread/                         # TREAD оптимизация
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── optimization.py
│   │   ├── token_router.py
│   │   └── medical_terms_db.py        # База медицинских терминов
│   │
│   ├── converter/                     # Обработка документов
│   │   ├── pdf_processor.py
│   │   ├── enhanced_processor.py
│   │   ├── image_processor.py         # Новый модуль обработки медицинских изображений
│   │   └── dicom_processor.py         # Новый модуль обработки DICOM
│   │
│   ├── vector_store/                  # Векторное хранилище
│   │   ├── __init__.py
│   │   └── faiss_store.py
│   │
│   ├── utils/                         # Утилиты
│   │   ├── cache_manager.py
│   │   ├── sync_manager.py            # Новый модуль синхронизации
│   │   └── analytics.py               # Новый модуль аналитики
│   │
│   ├── modules/                       # Новые модули функциональности
│   │   ├── __init__.py
│   │   ├── virtual_patient/           # Модуль виртуальных пациентов
│   │   │   ├── __init__.py
│   │   │   ├── patient_model.py
│   │   │   ├── case_generator.py
│   │   │   ├── diagnostic_engine.py
│   │   │   └── feedback_analyzer.py
│   │   │
│   │   ├── gamification/              # Модуль геймификации
│   │   │   ├── __init__.py
│   │   │   ├── achievement_system.py
│   │   │   ├── leaderboard.py
│   │   │   ├── challenge_generator.py
│   │   │   └── reward_manager.py
│   │   │
│   │   ├── adaptive_learning/         # Модуль адаптивного обучения
│   │   │   ├── __init__.py
│   │   │   ├── student_model.py
│   │   │   ├── learning_path.py
│   │   │   ├── knowledge_graph.py
│   │   │   └── progress_tracker.py
│   │   │
│   │   ├── social/                    # Модуль социальной платформы
│   │   │   ├── __init__.py
│   │   │   ├── forum.py
│   │   │   ├── chat_system.py
│   │   │   ├── resource_sharing.py
│   │   │   └── mentorship.py
│   │   └── integration/               # Модуль интеграции с внешними системами
│   │       ├── __init__.py
│   │       ├── lms_connector.py
│   │       ├── medical_db_connector.py
│   │       └── external_api.py
│   │
│   └── edge/                          # Новый модуль для edge-узлов
│       ├── __init__.py
│       ├── local_server.py
│       ├── sync_client.py
│       └── offline_manager.py
│
├── cloud/                             # Новый модуль для облачного сервера
│   ├── __init__.py
│   ├── central_server.py
│   ├── update_manager.py
│   ├── backup_system.py
│   └── api/                           # API облачного сервера
│       ├── __init__.py
│       ├── rest_api.py
│       ├── graphql_api.py
│       └── websocket_api.py
│
├── mobile/                            # Новый модуль для мобильного приложения
│   ├── README.md
│   └── flutter/                       # Flutter проект
│
├── desktop/                           # Новый модуль для десктопного приложения
│   ├── README.md
│   └── electron/                      # Electron проект
│
└── tests/                             # Тесты
    ├── conftest.py
    ├── data/                          # Тестовые данные
    │   ├── test.pdf
    │   └── test_comprehensive.pdf
    ├── integration/                   # Интеграционные тесты
    │   ├── README.md
    │   ├── test_pdf_preview.py
    │   ├── test_pdf_to_vector.py
    │   ├── test_streamlit_integration.py
    │   ├── test_virtual_patient.py     # Новый тест
    │   ├── test_gamification.py        # Новый тест
    │   └── test_hybrid_mode.py         # Новый тест
    ├── test_enhanced_processor.py
    ├── test_mode_manager.py
    ├── test_modes.py
    ├── test_pdf_converter.py
    ├── test_tread.py
    ├── test_vector_store.py
    ├── test_edge_sync.py              # Новый тест
    └── test_adaptive_learning.py      # Новый тест
```

## Ключевые изменения в структуре проекта:

1. **Добавлен файл ARCHITECTURE.md** - подробное описание гибридной архитектуры DocMentor

2. **Реорганизация режимов работы**:
   - `private_mode.py` → `local_mode.py` (для edge-узлов)
   - `public_mode.py` → `cloud_mode.py` (для облачного сервера)
   - Добавлен `hybrid_mode.py` для гибридной работы

3. **Новые модули функциональности**:
   - Виртуальные пациенты (`core/modules/virtual_patient/`)
   - Геймификация (`core/modules/gamification/`)
   - Адаптивное обучение (`core/modules/adaptive_learning/`)
   - Социальная платформа (`core/modules/social/`)
   - Интеграция с внешними системами (`core/modules/integration/`)

4. **Инфраструктура для гибридной архитектуры**:
   - Edge-узлы (`core/edge/`)
   - Облачный сервер (`cloud/`)

5. **Новые компоненты UI**:
   - Виртуальные пациенты (`app/components/virtual_patient.py`)
   - Геймификация (`app/components/gamification.py`)
   - Адаптивное обучение (`app/components/adaptive_learning.py`)
   - Анализ медицинских изображений (`app/components/image_analyzer.py`)
   - Социальная платформа (`app/components/social.py`)

6. **Новые страницы в UI**:
   - Виртуальные пациенты (`app/pages/virtual_patients.py`)
   - Учебные материалы (`app/pages/study_materials.py`)
   - Достижения (`app/pages/achievements.py`)
   - Социальная платформа (`app/pages/social.py`)
   - Настройки (`app/pages/settings.py`)

7. **Поддержка мобильной и десктопной платформ**:
   - Мобильное приложение на Flutter (`mobile/flutter/`)
   - Десктопное приложение на Electron (`desktop/electron/`)

8. **Расширенные тесты**:
   - Тесты для новых компонентов и функций
   - Тесты для гибридной архитектуры