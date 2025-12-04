"""
Константы для обработки Excel файлов.
"""

REQUIRED_COLUMNS = [
    'Модуль', 'Название задания', 'Ссылка на работу в админке',
    'Ссылка на работу в ЛК эксперта', 'ID студента', 'Отправлена',
    'Проверяющий', 'Возможные проверяющие', 'Дней на проверке', 'Тип задания', 'coord_id'
]

# # Типы заданий
# TASK_TYPES = {
#     'DIPLOMA': 'Диплом',
#     'HOMEWORK': 'ДЗ',
#     'COURSE_PROJECT': 'Курсовой проект'
# }

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

# # Настройки логирования
# LOG_CONFIG = {
#     'level': 'INFO',
#     'format': '%(asctime)s - %(levelname)s - %(message)s'
# }

# # Выходные дни (0 = понедельник, 6 = воскресенье)
# WEEKEND_DAYS = {5, 6}

# Названия выходных файлов
# OUTPUT_FILES = {
#     'DIPLOMA': 'result_files/дипломные_работы_отчет.xlsx',
#     'HOMEWORK': 'result_files/домашние_задания_отчет.xlsx',
#     'COURSE_PROJECTS': 'result_files/курсовые_проекты_отчет.xlsx',
#     'NO_REVIEWER': 'result_files/работы_без_проверяющего.txt',
#     'COORD_OVERDUE': 'result_files/коорд_просроченных_работ.txt',
#
# }
