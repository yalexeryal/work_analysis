"""
Модуль для обработки домашних работ.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.constants import REVIEW_DEADLINES


class HomeworkProcessor:
    """
    Класс для обработки и сохранения домашних работ.
    """

    def __init__(
            self,
            deadline_hw: Optional[int] = None,
            date_format: str = "%Y-%m-%d"
    ):
        """
        Args:
            deadline_hw: Дедлайн для домашних работ в рабочих днях
            date_format: Формат даты для именования файлов
        """
        self.deadline_hw = deadline_hw or REVIEW_DEADLINES['HOMEWORK']
        self.date_format = date_format

    def process_unverified_works(
            self,
            homework_df: pd.DataFrame,
            output_folder: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Обрабатывает DataFrame с домашними работами и сохраняет в Excel-файл.

        Args:
            homework_df: DataFrame с данными о домашних работах
            output_folder: Папка для сохранения файла

        Returns:
            Обработанный DataFrame

        Raises:
            TypeError: Если homework_df не является DataFrame
            ValueError: Если homework_df пуст
            FileNotFoundError: Если папка не существует
            IOError: При ошибках сохранения файла
        """
        self._validate_input_data(homework_df)

        # Обработка данных
        processed_df = self._process_dataframe(homework_df)

        # Сохранение файла
        self._save_to_excel(processed_df, output_folder)

        return processed_df

    def _validate_input_data(self, homework_df: pd.DataFrame) -> None:
        """
        Проверяет корректность входных данных.

        Args:
            homework_df: DataFrame для проверки

        Raises:
            TypeError: Если не DataFrame
            ValueError: Если пустой
        """
        if not isinstance(homework_df, pd.DataFrame):
            raise TypeError("homework_df должен быть объектом pandas.DataFrame")

        if homework_df.empty:
            raise ValueError("Входной DataFrame пуст")

    def _process_dataframe(self, homework_df: pd.DataFrame) -> pd.DataFrame:
        """
        Обрабатывает DataFrame: удаляет колонки.

        Args:
            homework_df: Исходный DataFrame

        Returns:
            Обработанный DataFrame
        """
        df = homework_df.copy()

        # Удаление ненужных колонок
        columns_to_drop = ['coord_id']
        existing_columns = [col for col in columns_to_drop if col in df.columns]

        if existing_columns:
            df = df.drop(columns=existing_columns)
            # print(f"Удалены колонки: {existing_columns}")

        return df

    def _save_to_excel(
            self,
            df: pd.DataFrame,
            output_folder: Optional[str] = None
    ) -> None:
        """
        Сохраняет DataFrame в Excel файл.

        Args:
            df: DataFrame для сохранения
            output_folder: Папка для сохранения

        Raises:
            FileNotFoundError: Если папка не существует
            IOError: При ошибках сохранения
        """
        output_path = self._get_output_path(output_folder)

        try:
            # Создаем папку если она не существует
            output_path.parent.mkdir(parents=True, exist_ok=True)

            df.to_excel(output_path, index=False, engine='openpyxl')
            print(f"Файл успешно сохранён: {output_path}")
            print(f"Сохранено {len(df)} записей")
        except Exception as e:
            raise IOError(f"Ошибка при сохранении файла: {e}")

    def _get_output_path(self, output_folder: Optional[str] = None) -> Path:
        """
        Формирует путь для сохранения файла.

        Args:
            output_folder: Папка для сохранения

        Returns:
            Полный путь к файлу
        """
        today_date = datetime.now().strftime(self.date_format)
        output_filename = f"Непроверенные_ДЗ_{today_date}.xlsx"

        if output_folder:
            output_path = Path(output_folder)
            return output_path / output_filename
        else:
            return Path(output_filename)


def process_unverified_works(
        homework_df: pd.DataFrame,
        output_folder: Optional[str] = None
) -> pd.DataFrame:
    """
    Основная функция обработки домашних работ.

    Args:
        homework_df: DataFrame с домашними работами
        output_folder: Папка для сохранения

    Returns:
        Обработанный DataFrame
    """
    processor = HomeworkProcessor()
    return processor.process_unverified_works(homework_df, output_folder)


# Пример использования
if __name__ == "__main__":
    # Создание тестового DataFrame
    test_data = {
        'ID студента': [1, 2, 3],
        'coord_id': [101, 102, 103],
        'Отправлена': [
            datetime(2024, 1, 1).date(),
            datetime(2024, 1, 15).date(),
            datetime(2024, 1, 20).date()
        ],
        'Модуль': ['math-101', 'physics-102', 'chemistry-103'],
        'Студент': ['Иван Иванов', 'Петр Петров', 'Мария Сидорова']
    }
    test_df = pd.DataFrame(test_data)

    # Использование класса
    processor = HomeworkProcessor()

    try:
        result_df = processor.process_unverified_works(
            homework_df=test_df,
            output_folder="result_files/"
        )
        print("Обработка завершена успешно")
        print(f"Результат: {len(result_df)} записей")

    except (TypeError, ValueError, FileNotFoundError, IOError) as e:
        print(f"Ошибка обработки: {e}")