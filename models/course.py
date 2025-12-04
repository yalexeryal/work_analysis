"""
Модуль для обработки курсовых работ.
"""
import pandas as pd
from datetime import date, datetime
from pathlib import Path
from typing import Set
import time

from config.modules import DIPLOMA_MODULES, SELF_ASSIGNMENT_MODULES, COORDINATORS
from config.constants import REVIEW_DEADLINES
from core.get_coordinators import get_coordinator_name
from core.get_module import get_base_module


class CourseWorksProcessor:
    """
    Класс для обработки курсовых работ.
    Использует уже подготовленные данные из DataProcessor.
    """

    def __init__(self):
        self.diploma_modules: Set[str] = set(DIPLOMA_MODULES)
        self.self_assignment_modules: Set[str] = set(SELF_ASSIGNMENT_MODULES)
        self.coordinators = COORDINATORS
        self.deadline_cor = REVIEW_DEADLINES['COURSE_PROJECT']

    def process_course_works(self, course_df: pd.DataFrame, output_folder: str, strict_filter: bool = False) -> None:
        """
        Основная функция обработки курсовых работ.

        Args:
            course_df: DataFrame с курсовыми работами (уже подготовленный DataProcessor)
            output_folder: Папка для сохранения результатов
            strict_filter: Если True - использовать >5 дней, если False - >=5 дней
        """
        try:
            # Проверяем входные данные
            if course_df is None or course_df.empty:
                print("Нет данных по курсовым работам для обработки!")
                return

            # Добавляем базовый модуль если его нет
            if 'Базовый_модуль' not in course_df.columns:
                course_df = course_df.copy()
                course_df['Базовый_модуль'] = course_df['Модуль'].apply(get_base_module)

            # ОПЕРАЦИЯ 1: Создаем файл "Курсовые без проверяющих"
            self._create_no_reviewers_file(course_df, output_folder)

            # ОПЕРАЦИЯ 2: Создаем файл с координаторами просроченных работ
            self._create_overdue_coordinators_file(course_df, output_folder, strict_filter)

            # ОПЕРАЦИЯ 3: Создаем файл с просроченными работами
            self._create_overdue_works_file(course_df, output_folder, strict_filter)

        except Exception as e:
            print(f"Ошибка при обработке курсовых работ: {e}")
            raise

    def _create_no_reviewers_file(self, course_df: pd.DataFrame, output_folder: str) -> None:
        """
        ОПЕРАЦИЯ 1: Создает файл "Курсовые без проверяющих"
        Исключает модули из SELF_ASSIGNMENT_MODULES

        Args:
            course_df: DataFrame с курсовыми работами
            output_folder: Папка для сохранения
        """
        try:
            # Создаем копию данных
            course_df_copy = course_df.copy()

            # Фильтруем: работы без проверяющих И исключаем self-assignment модули
            no_reviewer_df = course_df_copy[
                (course_df_copy['Проверяющий'].isna() | (course_df_copy['Проверяющий'] == '')) &
                (~course_df_copy['Базовый_модуль'].isin(self.self_assignment_modules))
                ].copy()

            # Группируем по координаторам
            coordinators_without_reviewers = {}
            unknown_coordinators = set()

            for _, row in no_reviewer_df.iterrows():
                coord_id = row['coord_id']
                coordinator_name = get_coordinator_name(coord_id)

                if coordinator_name == str(coord_id):  # Координатор не найден
                    unknown_coordinators.add(str(coord_id))
                    continue

                if coordinator_name not in coordinators_without_reviewers:
                    coordinators_without_reviewers[coordinator_name] = []

                coordinators_without_reviewers[coordinator_name].append(row)

            # Создаем файлы
            today_str = date.today().strftime("%Y-%m-%d")
            output_path = Path(output_folder)

            # Файл с работами без проверяющих
            no_reviewers_file = output_path / f'Курсовые_без_проверяющих_{today_str}.txt'
            with open(no_reviewers_file, 'w', encoding='utf-8') as f:
                if coordinators_without_reviewers:
                    for coordinator_name, works in coordinators_without_reviewers.items():
                        f.write(f"@{coordinator_name}\n")
                        for work in works:
                            f.write(
                                f" {work['Модуль']}  {work['Название задания']}  "
                                f"{work['Ссылка на работу в админке']}  "
                                f"{work['ID студента']}  {work['Отправлена']}\n"
                            )
                        f.write("\n")
                    print(f"Создан файл: {no_reviewers_file}")
                else:
                    f.write("Нет работ без проверяющих\n")
                    print("Нет работ без проверяющих")

            # Файл с неизвестными координаторами
            if unknown_coordinators:
                unknown_coords_file = output_path / f'Неизвестные_координаторы_{today_str}.txt'
                with open(unknown_coords_file, 'w', encoding='utf-8') as f:
                    for coord_id in unknown_coordinators:
                        f.write(f"{coord_id}\n")
                print(f"Создан файл: {unknown_coords_file}")

        except Exception as e:
            print(f"Ошибка при создании файла 'Курсовые без проверяющих': {e}")
            raise

    def _create_overdue_coordinators_file(self, course_df: pd.DataFrame, output_folder: str,
                                          strict_filter: bool = False) -> None:
        """
        ОПЕРАЦИЯ 2: Создает файл с координаторами просроченных работ

        Args:
            course_df: DataFrame с курсовыми работами
            output_folder: Папка для сохранения
            strict_filter: Если True - использовать >5 дней, если False - >=5 дней
        """
        try:
            # Фильтруем просроченные работы
            overdue_df = self._filter_overdue_works(course_df, strict_filter)

            # Получаем уникальных координаторов с просроченными работами
            overdue_coordinators = set()
            for coord_id in overdue_df['coord_id'].unique():
                coordinator_name = get_coordinator_name(coord_id)
                overdue_coordinators.add(coordinator_name)

            # Создаем файл
            today_str = date.today().strftime("%Y-%m-%d")
            output_path = Path(output_folder)

            coords_file = output_path / f'Координаторы_просроченных_курсовых_работ_{today_str}.txt'
            with open(coords_file, 'w', encoding='utf-8') as f:
                if overdue_coordinators:
                    sorted_coordinators = sorted([str(coord) for coord in overdue_coordinators])
                    for coordinator in sorted_coordinators:
                        f.write(f"{coordinator}\n")
                    print(f"Создан файл: {coords_file}")
                else:
                    f.write("Нет координаторов с просроченными работами\n")
                    print("Нет координаторов с просроченными работами")

        except Exception as e:
            print(f"Ошибка при создании файла координаторов просроченных работ: {e}")
            raise

    def _create_overdue_works_file(self, course_df: pd.DataFrame, output_folder: str,
                                   strict_filter: bool = False) -> None:
        """
        ОПЕРАЦИЯ 3: Создает файл с просроченными работами

        Args:
            course_df: DataFrame с курсовыми работами
            output_folder: Папка для сохранения
            strict_filter: Если True - использовать >5 дней, если False - >=5 дней
        """
        try:
            # Фильтруем просроченные работы
            overdue_df = self._filter_overdue_works(course_df, strict_filter)

            # Создаем Excel файл с просроченными работами
            result_columns = [
                'Модуль',
                'Название задания',
                'Ссылка на работу в админке',
                'Ссылка на работу в ЛК эксперта',
                'ID студента',
                'Отправлена',
                'Проверяющий',
                'Возможные проверяющие',
                'Дней на проверке',
            ]

            # Проверяем наличие всех нужных колонок
            available_columns = [col for col in result_columns if col in overdue_df.columns]

            today_str = date.today().strftime("%Y-%m-%d")
            output_path = Path(output_folder)
            excel_file = output_path / f'Просроченные_курсовые_{today_str}.xlsx'

            if len(overdue_df) > 0:
                # Используем только доступные колонки
                overdue_df_to_save = overdue_df[available_columns].copy()

                # Переименовываем колонки для читаемости
                column_rename = {
                    'Дней на проверке': 'Рабочих дней на проверке'
                }
                overdue_df_to_save = overdue_df_to_save.rename(columns=column_rename)

                # Сохранение с обработкой ошибок доступа к файлу
                self._save_dataframe_safe(overdue_df_to_save, excel_file)
                print(f"Создан файл: {excel_file}")
            else:
                # Создаем пустой файл с правильными заголовками
                empty_df = pd.DataFrame(columns=result_columns)
                self._save_dataframe_safe(empty_df, excel_file)
                print(f"Создан пустой файл: {excel_file}")

        except Exception as e:
            print(f"Ошибка при создании файла просроченных работ: {e}")
            raise

    def _filter_overdue_works(self, course_df: pd.DataFrame, strict_filter: bool = False) -> pd.DataFrame:
        """
        Фильтрует просроченные работы по количеству дней на проверке.

        Args:
            course_df: DataFrame с курсовыми работами
            strict_filter: Если True - использовать >5 дней, если False - >=5 дней

        Returns:
            DataFrame с просроченными работами
        """
        min_days = self.deadline_cor

        # Применяем фильтр
        if strict_filter:
            # Строгая фильтрация: >5 дней
            overdue_df = course_df[course_df['Дней на проверке'] > min_days]
        else:
            # Нестрогая фильтрация: >=5 дней
            overdue_df = course_df[course_df['Дней на проверке'] >= min_days]

        return overdue_df

    def _save_dataframe_safe(self, df: pd.DataFrame, file_path: Path) -> None:
        """
        Безопасно сохраняет DataFrame в файл с обработкой ошибок доступа.

        Args:
            df: DataFrame для сохранения
            file_path: Путь к файлу
        """
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                # Создаем папку если она не существует
                file_path.parent.mkdir(parents=True, exist_ok=True)

                df.to_excel(file_path, index=False, engine='openpyxl')
                break

            except PermissionError:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    # Генерируем уникальное имя файла
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    backup_filename = f"Просроченные_курсовые_{timestamp}.xlsx"
                    backup_path = file_path.parent / backup_filename
                    df.to_excel(backup_path, index=False, engine='openpyxl')
                    print(f"Файл сохранен с альтернативным именем: {backup_path}")
                    break

            except Exception as e:
                raise IOError(f"Ошибка при сохранении файла {file_path}: {e}")


# Функция для обратной совместимости
def process_course_works_legacy(input_file: str, output_folder: str, strict_filter: bool = False) -> None:
    """
    Основная функция обработки курсовых работ (легаси-версия).

    Args:
        input_file: Путь к входному файлу
        output_folder: Папка для сохранения результатов
        strict_filter: Если True - использовать >5 дней, если False - >=5 дней
    """
    processor = CourseWorksProcessor()

    # Загружаем данные из файла
    import pandas as pd
    df = pd.read_excel(input_file, sheet_name='Непроверенные работы')

    # Создаем временный DataProcessor для подготовки данных
    from core.create_dataframes import DataProcessor
    temp_processor = DataProcessor(input_file)
    temp_processor.create_base_df()
    course_df = temp_processor.create_course_df()

    processor.process_course_works(course_df, output_folder, strict_filter)


# Для совместимости с существующим кодом
process_course_works = process_course_works_legacy