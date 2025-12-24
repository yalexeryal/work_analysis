"""
Константы для обработки Excel файлов.
"""

REQUIRED_COLUMNS = [
    'Модуль', 'Название задания', 'Ссылка на работу в админке',
    'Ссылка на работу в ЛК эксперта', 'ID студента', 'Отправлена',
    'Проверяющий', 'Возможные проверяющие', 'Дней на проверке', 'Тип задания', 'coord_id'
]

# Сроки проверки в рабочих днях
REVIEW_DEADLINES = {
    'DIPLOMA': 7,
    'HOMEWORK': 2,
    'COURSE_PROJECT': 5
}

# Форматы дат
DATE_FORMATS = ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d']

# Пути к файлам
DEFAULT_INPUT_FILE = "original_files/Непроверенные_работы.xlsx"
DEFAULT_OUTPUT_FOLDER = "result_files/"
DEFAULT_input_FOLDER = "original_files/"

