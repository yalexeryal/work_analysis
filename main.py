"""
Основной модуль для запуска обработки данных о заданиях студентов.
"""
import os
import shutil
from functools import wraps
from datetime import datetime
from pathlib import Path

from config.constants import DEFAULT_OUTPUT_FOLDER, DEFAULT_INPUT_FILE, DEFAULT_input_FOLDER
from core.create_dataframes import DataProcessor
from models.course import CourseWorksProcessor
from models.diploma import process_diploma_works
from models.homework import process_unverified_works


def clean_folders_decorator():
    """
    Декоратор для очистки папок:
    - перед вызовом функции: удаляет все файлы из DEFAULT_OUTPUT_FOLDER (кроме __init__.py);
    - после вызова функции: удаляет все файлы из DEFAULT_INPUT_FILE (кроме __init__.py).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Очистка выходной папки ПЕРЕД запуском функции
            if os.path.exists(DEFAULT_OUTPUT_FOLDER):
                for filename in os.listdir(DEFAULT_OUTPUT_FOLDER):
                    filepath = os.path.join(DEFAULT_OUTPUT_FOLDER, filename)
                    # Сохраняем __init__.py и директории
                    if filename == '__init__.py' or os.path.isdir(filepath):
                        continue
                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                        elif os.path.islink(filepath):
                            os.unlink(filepath)
                    except Exception as e:
                        print(f"Ошибка при удалении файла {filepath}: {e}")
            else:
                print(f"Папка {DEFAULT_OUTPUT_FOLDER} не существует, пропускаем очистку.")

            # 2. Вызов основной функции
            result = func(*args, **kwargs)

            # 3. Очистка входной папки ПОСЛЕ выполнения функции
            if os.path.exists(DEFAULT_input_FOLDER):
                for filename in os.listdir(DEFAULT_input_FOLDER):
                    filepath = os.path.join(DEFAULT_input_FOLDER, filename)
                    # Сохраняем __init__.py и директории
                    if filename == '__init__.py' or os.path.isdir(filepath):
                        continue
                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                        elif os.path.islink(filepath):
                            os.unlink(filepath)
                    except Exception as e:
                        print(f"Ошибка при удалении файла {filepath}: {e}")
            else:
                print(f"Папка {DEFAULT_INPUT_FILE} не существует, пропускаем очистку.")

            return result
        return wrapper
    return decorator

class MainProcessor:
    """Основной класс для управления процессом обработки данных."""

    def __init__(self, input_file: str = None, output_folder: str = None):
        """
        Инициализация процессора.

        Args:
            input_file: Путь к входному файлу
            output_folder: Папка для сохранения результатов
        """
        self.input_file_path = Path(input_file or DEFAULT_INPUT_FILE)
        self.output_folder = Path(output_folder or DEFAULT_OUTPUT_FOLDER)
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.day_name = datetime.now().strftime('%A')

    def validate_input_file(self) -> bool:
        """
        Проверяет существование входного файла.

        Returns:
            True если файл существует, иначе False
        """
        if not self.input_file_path.exists():
            print(f"Входной файл '{self.input_file_path}' не найден!")
            print("Убедитесь, что файл находится в правильной директории.")
            return False
        return True

    def process_data(self) -> tuple:
        """
        Обрабатывает данные и создает DataFrame.

        Returns:
            Кортеж (base_df, diploma_df, homework_df, course_df)
        """
        print(f"Обработка данных за {self.today_date}")

        processor = DataProcessor(str(self.input_file_path))
        base_df, diploma_df, homework_df, course_df = processor.process_all()

        # Вывод статистики
        self._print_statistics(base_df, diploma_df, homework_df, course_df)

        return base_df, diploma_df, homework_df, course_df

    def _print_statistics(self, base_df, diploma_df, homework_df, course_df) -> None:
        """Выводит статистику по обработанным данным."""
        print(f"Найдено записей:")
        print(f"  - Всего: {len(base_df) if base_df is not None else 0}")
        print(f"  - Дипломы: {len(diploma_df) if diploma_df is not None else 0}")
        print(f"  - Домашние работы: {len(homework_df) if homework_df is not None else 0}")
        print(f"  - Курсовые: {len(course_df) if course_df is not None else 0}")
        print(f"Сегодня: {self.today_date} ({self.day_name})")

    def run_thursday_processing(self, course_df) -> None:
        """Запускает обработку для четверга."""
        print("Четверг - обработка курсовых работ")
        processor = CourseWorksProcessor()
        processor.process_course_works(course_df, str(self.output_folder), strict_filter=False)

    def run_regular_processing(self, diploma_df, homework_df) -> None:
        """Запускает регулярную обработку (все дни кроме четверга)."""
        print("Обработка дипломных и домашних работ")

        # Обработка дипломных работ
        self._process_diploma_works(diploma_df)

        # Обработка домашних работ
        self._process_homework_works(homework_df)

        # Обработка курсовых работ
        # self._process_course_works(course_df)

    def _process_diploma_works(self, diploma_df) -> None:
        """Обрабатывает дипломные работы."""
        if diploma_df is not None and not diploma_df.empty:
            process_diploma_works(diploma_df, str(self.output_folder))
        else:
            print("Нет данных по дипломным работам для обработки")

    def _process_homework_works(self, homework_df) -> None:
        """Обрабатывает домашние работы."""
        if homework_df is not None and not homework_df.empty:
            process_unverified_works(homework_df, str(self.output_folder))
        else:
            print("Нет данных по домашним работам для обработки")

    def _process_course_works(self, course_df) -> None:
        """Обрабатывает курсовые работы."""
        if course_df is not None and not course_df.empty:
            processor = CourseWorksProcessor()
            processor.process_course_works(course_df, str(self.output_folder))
        else:
            print("Нет данных по курсовым работам для обработки")

    def execute(self) -> None:
        """Основной метод выполнения обработки."""
        if not self.validate_input_file():
            return

        try:
            # Обработка данных
            base_df, diploma_df, homework_df, course_df = self.process_data()

            # Запуск соответствующей обработки в зависимости от дня недели
            if self.day_name == 'Thursday':
                self.run_thursday_processing(course_df)
            else:
                self.run_regular_processing(diploma_df, homework_df)
                # self.run_regular_processing(diploma_df, homework_df, course_df)

            print("Обработка завершена успешно!")

        except Exception as e:
            print(f"Произошла ошибка при обработке: {e}")
            raise

@clean_folders_decorator()
def main():
    """
    Основная функция для запуска обработки.
    """
    processor = MainProcessor()
    processor.execute()


if __name__ == '__main__':
    main()