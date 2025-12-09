markdown
# Work Analysis

**Анализ рабочих проверки работ экспертами**


## Описание

Проект предназначен для обработки данных о рабочих процессах с целью:
- отслеживания проверки (домашних заданий, дипломных работ, курсовых работ);
- выявления работ не взятых на проверку экспертами;
- выявления работ не проверенных в установленные сроки экспертами;
- своевременного реагирования и недопущения просрочки проверки работ.

## Функциональные возможности

- Сбор данных из файла Excel.
- Формирование регулярных отчётов.
- Экспорт данных в формате Excel.

## Технические характеристики

- **Язык программирования:** Python 3.x
- **Основные библиотеки:** pandas, matplotlib, seaborn, openpyxl
- **Формат входных данных:** Excel
- **Формат выходных данных:** Excel
- **ОС:** кросс‑платформенный (Windows, Linux, macOS)

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yalexeryal/work_analysis.git
   cd work_analysis
   ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Запустите анализ:
    ```bash
    python main.py
    ```
   
4. Структура проекта
``` 
├── .gitignore
├── README.md
├── config
│   ├── __init__.py
│   ├── config_editor.py
│   ├── config_loader.py
│   ├── constants.py
│   ├── coordinators.yaml
│   ├── dates.json
│   ├── module.yaml
│   ├── modules.py
│   └── professions.yaml
├── core
│   ├── __init__.py
│   ├── create_dataframes.py
│   ├── get_coordinators.py
│   ├── get_module.py
│   └── working_days.py
├── edit_config.py
├── main.py
├── models
│   ├── __init__.py
│   ├── course.py
│   ├── diploma.py
│   ├── homework.py
│   └── utils.py
├── original_files
│   ├── __init__.py
├── print_tree.py
├── requirements.txt
├── result_files
│   ├── __init__.py
└── utils
    ├── __init__.py
    ├── config_editor_gui.py
    ├── install.py
    ├── run_editor.bat
    └── run_editor.sh
```
## Инструкция по использованию GUI для редактирования конфигураций:
Зайдите в папку utils:
1. Запуск:
```
# Запустите редактор
python config_editor_gui.py

# Или откройте пример конфигурации
python config_editor_gui.py example_config.yaml
```
2. Основные функции:
- Открытие файлов - поддерживает YAML (.yaml, .yml) и JSON (.json)
- Древовидное представление - навигация по структуре конфигурации
- Редактирование - изменение значений с подсветкой синтаксиса
- Добавление/удаление - управление элементами конфигурации
- Валидация - проверка структуры конфигурации
- Сохранение - поддержка разных форматов

3. Особенности:
- Автосохранение последнего открытого файла
- Поддержка отмены/повтора действий
- Подсветка синтаксиса YAML/JSON
- Валидация структуры конфигурации
- Всплывающие подсказки
- Горячие клавиши для быстрого доступа
