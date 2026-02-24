import pandas as pd
from datetime import datetime, date
import os


def process_diploma_works(diploma_df, output_folder=None):
    """
    Обрабатывает DataFrame с дипломными работами и сохраняет в Excel-файл.

    Args:
        diploma_df (pd.DataFrame): Исходный DataFrame с данными о дипломных работах
        output_folder (str, optional): Папка для сохранения файла.
            Если None — сохраняется в текущую директорию.


    Returns:
        pd.DataFrame: Обработанный DataFrame (без столбца 'Возможные проверяющие')
    """
    # Проверка входных данных
    if not isinstance(diploma_df, pd.DataFrame):
        raise TypeError("diploma_df должен быть объектом pandas.DataFrame")

    if diploma_df.empty:
        print("Предупреждение: входной DataFrame пуст!")
        return diploma_df

    # # Удаление столбца 'Возможные проверяющие'
    # if 'Возможные проверяющие' in diploma_df.columns:
    #     diploma_df = diploma_df.drop(['Возможные проверяющие'], axis=1)
    # else:
    #     print("Столбец 'Возможные проверяющие' не найден — пропуск удаления.")

    # Формирование имени файла с текущей датой
    today_date = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"Дипломные_работы_{today_date}.xlsx"

    # Определение полного пути для сохранения
    if output_folder:
        # Проверяем существование папки
        if not os.path.exists(output_folder):
            raise FileNotFoundError(f"Папка не найдена: {output_folder}")
        output_path = os.path.join(output_folder, output_filename)
    else:
        output_path = output_filename

    # Сохранение в Excel
    try:
        diploma_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Файл успешно сохранён: {output_path}")
        print(f"Сохранено {len(diploma_df)} записей")
    except Exception as e:
        raise IOError(f"Ошибка при сохранении файла: {e}")

    return diploma_df

# """
# Модуль для обработки дипломных работ.
# """
# import pandas as pd
# from datetime import date, datetime
# from pathlib import Path
# from typing import Set, Dict, List
# import time
#
# from config.modules import DIPLOMA_MODULES
# from config.constants import REVIEW_DEADLINES
# from core.get_coordinators import get_coordinator_name
# from core.get_module import get_base_module
#
#
# class DiplomaWorksProcessor:
#     """
#     Класс для обработки дипломных работ.
#     """
#
#     def __init__(self):
#         self.diploma_modules: Set[str] = set(DIPLOMA_MODULES)
#         self.deadline_diploma = REVIEW_DEADLINES['DIPLOMA']
#
#     def process_diploma_works(self, diploma_df: pd.DataFrame, output_folder: str, strict_filter: bool = False) -> None:
#         """
#         Основная функция обработки дипломных работ.
#
#         Args:
#             diploma_df: DataFrame с дипломными работами
#             output_folder: Папка для сохранения результатов
#             strict_filter: Если True - использовать >5 дней, если False - >=5 дней
#         """
#         try:
#             # Проверяем входные данные
#             if diploma_df is None or diploma_df.empty:
#                 print("Нет данных по дипломным работам для обработки!")
#                 return
#
#             # Добавляем базовый модуль если его нет
#             if 'Базовый_модуль' not in diploma_df.columns:
#                 diploma_df = diploma_df.copy()
#                 diploma_df['Базовый_модуль'] = diploma_df['Модуль'].apply(get_base_module)
#
#             # Удаляем столбец 'Возможные проверяющие' если он существует
#             if 'Возможные проверяющие' in diploma_df.columns:
#                 diploma_df = diploma_df.drop(columns=['Возможные проверяющие'])
#
#             # ОПЕРАЦИЯ 1: Создаем основной файл с дипломными работами
#             self._create_main_diploma_file(diploma_df, output_folder)
#
#             # ОПЕРАЦИЯ 2: Создаем файл с просроченными работами
#             self._create_overdue_diploma_file(diploma_df, output_folder, strict_filter)
#
#             # ОПЕРАЦИЯ 3: Создаем файл с группировкой по проверяющим
#             self._create_reviewers_grouped_file(diploma_df, output_folder, strict_filter)
#
#         except Exception as e:
#             print(f"Ошибка при обработке дипломных работ: {e}")
#             raise
#
#     def _create_main_diploma_file(self, diploma_df: pd.DataFrame, output_folder: str) -> None:
#         """
#         Создает основной файл с дипломными работами (все работы).
#
#         Args:
#             diploma_df: DataFrame с дипломными работами
#             output_folder: Папка для сохранения
#         """
#         try:
#             today_str = date.today().strftime("%Y-%m-%d")
#             output_path = Path(output_folder)
#
#             # Определяем колонки для сохранения
#             result_columns = [
#                 'Модуль',
#                 'Название задания',
#                 'Ссылка на работу в админке',
#                 'Ссылка на работу в ЛК эксперта',
#                 'ID студента',
#                 'Отправлена',
#                 'Проверяющий',
#                 'Возможные проверяющие',
#                 'Дней на проверке',
#             ]
#
#
#             # Выбираем только существующие колонки
#             available_columns = [col for col in result_columns if col in diploma_df.columns]
#
#             excel_file = output_path / f'Дипломные_работы_{today_str}.xlsx'
#
#             if len(diploma_df) > 0:
#                 diploma_df_to_save = diploma_df[available_columns].copy()
#                 self._save_dataframe_safe(diploma_df_to_save, excel_file)
#                 print(f"Создан основной файл с дипломными работами: {excel_file}")
#             else:
#                 # Создаем пустой файл с правильными заголовками
#                 empty_df = pd.DataFrame(columns=result_columns)
#                 self._save_dataframe_safe(empty_df, excel_file)
#                 print(f"Создан пустой основной файл: {excel_file}")
#
#         except Exception as e:
#             print(f"Ошибка при создании основного файла дипломных работ: {e}")
#             raise
#
#     def _create_overdue_diploma_file(self, diploma_df: pd.DataFrame, output_folder: str,
#                                      strict_filter: bool = False) -> None:
#         """
#         Создает файл с просроченными дипломными работами (более 5 дней).
#
#         Args:
#             diploma_df: DataFrame с дипломными работами
#             output_folder: Папка для сохранения
#             strict_filter: Если True - использовать >5 дней, если False - >=5 дней
#         """
#         try:
#             # Фильтруем просроченные работы
#             overdue_df = self._filter_overdue_diploma_works(diploma_df, strict_filter)
#
#             today_str = date.today().strftime("%Y-%m-%d")
#             output_path = Path(output_folder)
#
#             # Определяем колонки для сохранения
#             result_columns = [
#                 'Модуль',
#                 'Название задания',
#                 'Ссылка на работу в админке',
#                 'Ссылка на работу в ЛК эксперта',
#                 'ID студента',
#                 'Отправлена',
#                 'Проверяющий',
#                 'Дней на проверке',
#             ]
#
#             # Выбираем только существующие колонки
#             available_columns = [col for col in result_columns if col in overdue_df.columns]
#
#             excel_file = output_path / f'Просроченные_дипломные_{today_str}.xlsx'
#
#             if len(overdue_df) > 0:
#                 overdue_df_to_save = overdue_df[available_columns].copy()
#
#                 # Переименовываем колонку для читаемости
#                 column_rename = {
#                     'Дней на проверке': 'Рабочих дней на проверке'
#                 }
#                 overdue_df_to_save = overdue_df_to_save.rename(columns=column_rename)
#
#                 self._save_dataframe_safe(overdue_df_to_save, excel_file)
#                 print(f"Создан файл с просроченными дипломными работами: {excel_file}")
#                 print(f"Найдено просроченных работ: {len(overdue_df)}")
#             else:
#                 # Создаем пустой файл с правильными заголовками
#                 empty_df = pd.DataFrame(columns=result_columns)
#                 self._save_dataframe_safe(empty_df, excel_file)
#                 print(f"Создан пустой файл просроченных работ: {excel_file}")
#
#         except Exception as e:
#             print(f"Ошибка при создании файла просроченных дипломных работ: {e}")
#             raise
#
#     def _create_reviewers_grouped_file(self, diploma_df: pd.DataFrame, output_folder: str,
#                                        strict_filter: bool = False) -> None:
#         """
#         Создает файл с группировкой по проверяющим.
#         Ключ: Проверяющий, значение: список работ с указанными полями.
#
#         Args:
#             diploma_df: DataFrame с дипломными работами
#             output_folder: Папка для сохранения
#             strict_filter: Если True - использовать >5 дней, если False - >=5 дней
#         """
#         try:
#             # Фильтруем просроченные работы, если нужно
#             if strict_filter:
#                 # Фильтруем только просроченные работы
#                 filtered_df = self._filter_overdue_diploma_works(diploma_df, strict_filter)
#             else:
#                 # Берем все работы
#                 filtered_df = diploma_df.copy()
#
#             # Группируем по проверяющим
#             reviewers_dict: Dict[str, List[Dict]] = {}
#
#             for _, row in filtered_df.iterrows():
#                 reviewer = row['Проверяющий']
#
#                 # Если проверяющий не указан, пропускаем
#                 if pd.isna(reviewer) or reviewer == '':
#                     continue
#
#                 if reviewer not in reviewers_dict:
#                     reviewers_dict[reviewer] = []
#
#                 # Формируем запись о работе
#                 work_info = {
#                     'Модуль': row.get('Модуль', ''),
#                     'Название задания': row.get('Название задания', ''),
#                     'Ссылка на работу в ЛК эксперта': row.get('Ссылка на работу в ЛК эксперта', ''),
#                     'Студент': row.get('ID студента', ''),
#                     'Отправлена': row.get('Отправлена', ''),
#                     'Рабочих дней на проверке': row.get('Дней на проверке', 0)
#                 }
#
#                 reviewers_dict[reviewer].append(work_info)
#
#             # Создаем файл
#             today_str = date.today().strftime("%Y-%m-%d")
#             output_path = Path(output_folder)
#
#             if strict_filter:
#                 txt_file = output_path / f'Проверяющие_просроченные_дипломы_{today_str}.txt'
#             else:
#                 txt_file = output_path / f'Проверяющие_все_дипломы_{today_str}.txt'
#
#             with open(txt_file, 'w', encoding='utf-8') as f:
#                 if reviewers_dict:
#                     # Сортируем проверяющих по алфавиту
#                     sorted_reviewers = sorted(reviewers_dict.keys())
#
#                     for reviewer in sorted_reviewers:
#                         works = reviewers_dict[reviewer]
#                         f.write(f"=== {reviewer} ===\n")
#
#
#                         # Сортируем работы по количеству дней на проверке (по убыванию)
#                         works_sorted = sorted(works, key=lambda x: x['Рабочих дней на проверке'], reverse=True)
#
#                         for work in works_sorted:
#                             f.write(
#                                 f"Модуль: {work['Модуль']}\n"
#                                 f"Задание: {work['Название задания']}\n"
#                                 f"Ссылка: {work['Ссылка на работу в ЛК эксперта']}\n"
#                                 f"Студент: {work['Студент']}\n"
#                                 f"Отправлена: {work['Отправлена']}\n"
#                                 f"Дней на проверке: {work['Рабочих дней на проверке']}\n"
#                                 f"{'-' * 50}\n"
#                             )
#                         f.write("\n\n")
#
#                     print(f"Создан файл с группировкой по проверяющим: {txt_file}")
#                     print(f"Обработано проверяющих: {len(reviewers_dict)}")
#                 else:
#                     f.write("Нет данных для отображения\n")
#                     print("Нет данных для создания файла с группировкой по проверяющим")
#
#         except Exception as e:
#             print(f"Ошибка при создании файла с группировкой по проверяющим: {e}")
#             raise
#
#     def _filter_overdue_diploma_works(self, diploma_df: pd.DataFrame, strict_filter: bool = False) -> pd.DataFrame:
#         """
#         Фильтрует просроченные дипломные работы по количеству дней на проверке.
#
#         Args:
#             diploma_df: DataFrame с дипломными работами
#             strict_filter: Если True - использовать >5 дней, если False - >=5 дней
#
#         Returns:
#             DataFrame с просроченными работами
#         """
#         min_days = self.deadline_diploma
#
#         # Применяем фильтр
#         if strict_filter:
#             # Строгая фильтрация: >5 дней
#             overdue_df = diploma_df[diploma_df['Дней на проверке'] > min_days]
#         else:
#             # Нестрогая фильтрация: >=5 дней
#             overdue_df = diploma_df[diploma_df['Дней на проверке'] >= min_days]
#
#         return overdue_df
#
#     def _save_dataframe_safe(self, df: pd.DataFrame, file_path: Path) -> None:
#         """
#         Безопасно сохраняет DataFrame в файл с обработкой ошибок доступа.
#
#         Args:
#             df: DataFrame для сохранения
#             file_path: Путь к файлу
#         """
#         max_attempts = 3
#
#         for attempt in range(max_attempts):
#             try:
#                 # Создаем папку если она не существует
#                 file_path.parent.mkdir(parents=True, exist_ok=True)
#
#                 df.to_excel(file_path, index=False, engine='openpyxl')
#                 break
#
#             except PermissionError:
#                 if attempt < max_attempts - 1:
#                     time.sleep(2)
#                 else:
#                     # Генерируем уникальное имя файла
#                     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#                     backup_filename = f"{file_path.stem}_{timestamp}.xlsx"
#                     backup_path = file_path.parent / backup_filename
#                     df.to_excel(backup_path, index=False, engine='openpyxl')
#                     print(f"Файл сохранен с альтернативным именем: {backup_path}")
#                     break
#
#             except Exception as e:
#                 raise IOError(f"Ошибка при сохранении файла {file_path}: {e}")
#
#
# # Функция для обратной совместимости
# def process_diploma_works_legacy(diploma_df: pd.DataFrame, output_folder: str,
#                                  strict_filter: bool = False) -> pd.DataFrame:
#     """
#     Основная функция обработки дипломных работ (легаси-версия).
#
#     Args:
#         diploma_df: DataFrame с дипломными работами
#         output_folder: Папка для сохранения результатов
#         strict_filter: Если True - использовать >5 дней, если False - >=5 дней
#
#     Returns:
#         DataFrame: Обработанный DataFrame (без столбца 'Возможные проверяющие')
#     """
#     processor = DiplomaWorksProcessor()
#
#     # Проверка входных данных
#     if not isinstance(diploma_df, pd.DataFrame):
#         raise TypeError("diploma_df должен быть объектом pandas.DataFrame")
#
#     if diploma_df.empty:
#         print("Предупреждение: входной DataFrame пуст!")
#         return diploma_df
#
#     # Обрабатываем работы
#     processor.process_diploma_works(diploma_df, output_folder, strict_filter)
#
#     # Удаляем столбец 'Возможные проверяющие' если он существует
#     if 'Возможные проверяющие' in diploma_df.columns:
#         diploma_df = diploma_df.drop(columns=['Возможные проверяющие'])
#
#     return diploma_df
#
#
# # Для совместимости с существующим кодом
# process_diploma_works = process_diploma_works_legacy
