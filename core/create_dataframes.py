import pandas as pd
from datetime import date
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from config.constants import REQUIRED_COLUMNS, DEFAULT_INPUT_FILE, REVIEW_DEADLINES
from config.modules import DIPLOMA_MODULES, holidays, extra_days
from core.working_days import WorkingDaysCalculator

from core.get_module import get_base_module


class DataProcessor:
    """
    Класс для обработки данных о заданиях студентов.

    Загружает данные из Excel файла, проверяет обязательные колонки,
    добавляет вычисляемые поля и создает специализированные DataFrame
    для разных типов заданий.
    """

    def __init__(self, input_file_path: Optional[str] = None) -> None:
        """
        Инициализация процессора данных.

        Args:
            input_file_path: Путь к входному файлу Excel. Если не указан,
                           используется путь из констант.
        """
        self.input_file_path: Path = Path(input_file_path or f"../{DEFAULT_INPUT_FILE}")
        self.base_df: Optional[pd.DataFrame] = None
        self.diploma_df: Optional[pd.DataFrame] = None
        self.homework_df: Optional[pd.DataFrame] = None
        self.course_df: Optional[pd.DataFrame] = None
        self._processed: bool = False  # Флаг для отслеживания обработки

        self._initialize_working_days_calculator()

    def _initialize_working_days_calculator(self) -> None:
        """Инициализирует калькулятор рабочих дней."""
        self.calculator = WorkingDaysCalculator()
        for holiday in holidays:
            self.calculator.add_holiday(holiday)
        for day in extra_days:
            self.calculator.add_extra_working_day(day)

    def create_base_df(self) -> Optional[pd.DataFrame]:
        """
        Создает базовый DataFrame из входного файла.

        Returns:
            Базовый DataFrame или None в случае ошибки.

        Raises:
            FileNotFoundError: Если файл не найден.
            Exception: При других ошибках обработки.
        """
        try:
            df_base = self._load_dataframe()
            df_base = self._validate_and_prepare_dataframe(df_base)
            df_base = self._add_calculated_columns(df_base)

            self.base_df = df_base
            return df_base

        except FileNotFoundError:
            print(f"Файл не найден: {self.input_file_path}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {type(e).__name__}: {e}")
            return None

    def _load_dataframe(self) -> pd.DataFrame:
        """
        Загружает DataFrame из Excel файла.

        Returns:
            Загруженный DataFrame.

        Raises:
            FileNotFoundError: Если файл не найден.
        """
        if not self.input_file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.input_file_path}")

        df_base = pd.read_excel(self.input_file_path)
        print(f"Успешно загружен файл: {self.input_file_path}")
        print(f"Количество строк: {len(df_base)}")
        return df_base

    def _validate_and_prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Проверяет и подготавливает DataFrame.

        Args:
            df: Исходный DataFrame для проверки.

        Returns:
            Проверенный и подготовленный DataFrame.

        Raises:
            ValueError: Если отсутствуют обязательные колонки.
        """
        missing_columns = self._get_missing_columns(df)
        if missing_columns:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")

        return df[REQUIRED_COLUMNS].copy()

    def _get_missing_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Возвращает список отсутствующих обязательных колонок.

        Args:
            df: DataFrame для проверки.

        Returns:
            Список отсутствующих колонок.
        """
        return [col for col in REQUIRED_COLUMNS if col not in df.columns]

    def _add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Добавляет вычисляемые колонки в DataFrame.

        Args:
            df: Исходный DataFrame.

        Returns:
            DataFrame с добавленными колонки.
        """
        df = df.copy()

        # Добавление базового модуля
        df['Базовый_модуль'] = df['Модуль'].apply(get_base_module)

        # Преобразование даты
        df['Отправлена'] = pd.to_datetime(df['Отправлена']).dt.date

        # Расчет дней на проверке
        today = date.today()
        df['Дней на проверке'] = df['Отправлена'].apply(
            lambda x: self._calculate_days_on_review(x, today)
        )

        return df

    def _calculate_days_on_review(self, submission_date: date, current_date: date) -> int:
        """
        Вычисляет количество дней на проверке.

        Args:
            submission_date: Дата отправки задания.
            current_date: Текущая дата.

        Returns:
            Количество рабочих дней на проверке.
        """
        if pd.isna(submission_date):
            return 0
        return self.calculator.calculate(submission_date, current_date)

    def create_diploma_df(self) -> Optional[pd.DataFrame]:
        """
        Создает DataFrame для дипломных работ.

        Returns:
            DataFrame с дипломными работами или None в случае ошибки.
        """
        if not self._validate_base_df():
            return None

        # Сначала фильтруем по дипломным модулям
        diploma_df = self._filter_dataframe_by_modules(
            self.base_df,
            DIPLOMA_MODULES,
            include=True
        )

        # Дополнительно фильтруем по типу задания "Диплом"
        if 'Тип задания' in diploma_df.columns:
            diploma_df = diploma_df[diploma_df['Тип задания'] == 'Диплом']

        columns_to_drop = ['Базовый_модуль', 'Тип задания', 'coord_id']
        diploma_df = self._drop_columns(diploma_df, columns_to_drop)

        print(f"Количество строк в дипломном DF: {len(diploma_df)}")
        self.diploma_df = diploma_df
        return diploma_df

    def create_homework_df(self, strict_filter: bool = False) -> Optional[pd.DataFrame]:
        """
        Создает DataFrame для домашних заданий.

        Args:
            strict_filter: Если True - использовать >2 дней, если False - >=2 дней

        Returns:
            DataFrame с домашними заданиями или None в случае ошибки.
        """
        if not self._validate_base_df():
            return None

        # Фильтрация по типу задания 'ДЗ'
        homework_df = self.base_df[self.base_df['Тип задания'] == 'ДЗ'].copy()
        # print(f"После фильтрации по типу 'ДЗ': {len(homework_df)} записей")
        # print(f"После исключения дипломных модулей: {len(homework_df)} записей")

        # Фильтрация по количеству дней на проверке
        min_days = REVIEW_DEADLINES['HOMEWORK']

        if strict_filter:
            # Строгая фильтрация: >2 дней
            homework_df = homework_df[homework_df['Дней на проверке'] > min_days]
            filter_text = f"> {min_days}"
        else:
            # Нестрогая фильтрация: >=2 дней
            homework_df = homework_df[homework_df['Дней на проверке'] >= min_days]
            filter_text = f">= {min_days}"

        # print(f"После фильтрации по дням ({filter_text}): {len(homework_df)} записей")

        columns_to_drop = ['Базовый_модуль', 'Тип задания']
        homework_df = self._drop_columns(homework_df, columns_to_drop)

        # print(f"Итоговое количество строк в ДЗ DF: {len(homework_df)}")

        self.homework_df = homework_df
        return homework_df

    def create_course_df(self) -> Optional[pd.DataFrame]:
        """
        Создает DataFrame для курсовых работ.

        Returns:
            DataFrame с курсовыми работами или None в случае ошибки.
        """
        if not self._validate_base_df():
            return None

        # Фильтрация по типу задания 'Диплом'
        course_df = self.base_df[self.base_df['Тип задания'] == 'Диплом'].copy()

        # Исключение дипломных модулей
        course_df = self._filter_dataframe_by_modules(
            course_df,
            DIPLOMA_MODULES,
            include=False
        )

        columns_to_drop = ['Тип задания', 'Возможные проверяющие']
        course_df = self._drop_columns(course_df, columns_to_drop)

        # print(f"Количество строк в курсовом DF: {len(course_df)}")
        self.course_df = course_df
        return course_df

    def check_homework_stats(self):
        """Проверка статистики по домашним заданиям БЕЗ фильтрации по дипломным модулям"""
        if self.base_df is None:
            print("Сначала создайте base_df")
            return

        # Только фильтрация по типу задания, без исключения дипломных модулей
        homework_df = self.base_df[self.base_df['Тип задания'] == 'ДЗ'].copy()
        total_homeworks = len(homework_df)
        # print(f"Всего записей с типом 'ДЗ' в base_df: {total_homeworks}")

        # Проверим распределение дней на проверке
        days_distribution = homework_df['Дней на проверке'].value_counts().sort_index()
        # print("Распределение дней на проверке (все ДЗ):")
        for days, count in days_distribution.items():
            print(f"  {days} дней: {count} записей")

        # Проверим сколько будет при >2 дней (строго больше)
        strict_filter = len(homework_df[homework_df['Дней на проверке'] > 2])
        # print(f"ДЗ с >2 дней на проверке: {strict_filter} записей")

        # И сколько при >=2 дней (текущая логика)
        current_filter = len(homework_df[homework_df['Дней на проверке'] >= 2])
        # print(f"ДЗ с >=2 дней на проверке: {current_filter} записей")

    def _validate_base_df(self) -> bool:
        """
        Проверяет, создан ли базовый DataFrame.

        Returns:
            True если базовый DataFrame создан, иначе False.
        """
        if self.base_df is None:
            print("Сначала необходимо создать базовый DataFrame")
            return False
        return True

    def _filter_dataframe_by_modules(
            self,
            df: pd.DataFrame,
            modules: List[str],
            include: bool = True
    ) -> pd.DataFrame:
        """
        Фильтрует DataFrame по списку модулей.

        Args:
            df: DataFrame для фильтрации.
            modules: Список модулей для фильтрации.
            include: Если True - включать модули, если False - исключать.

        Returns:
            Отфильтрованный DataFrame.
        """
        module_names_lower = [module.lower() for module in modules]

        if include:
            mask = df['Базовый_модуль'].str.lower().isin(module_names_lower)
        else:
            mask = ~df['Базовый_модуль'].str.lower().isin(module_names_lower)

        return df[mask].copy()

    def _drop_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Удаляет указанные колонки из DataFrame, если они существуют.

        Args:
            df: Исходный DataFrame.
            columns: Список колонки для удаления.

        Returns:
            DataFrame без указанных колонок.
        """
        existing_columns = [col for col in columns if col in df.columns]
        return df.drop(existing_columns, axis=1)

    def process_all(self, homework_strict_filter: bool = False) -> Tuple[
        Optional[pd.DataFrame],
        Optional[pd.DataFrame],
        Optional[pd.DataFrame],
        Optional[pd.DataFrame]
    ]:
        """
        Выполняет полную обработку всех данных.

        Args:
            homework_strict_filter: Если True - использовать строгую фильтрацию (>2 дней) для ДЗ

        Returns:
            Кортеж (base_df, diploma_df, homework_df, course_df)
        """
        # Если уже обработано - возвращаем существующие данные
        if self._processed:
            return self.base_df, self.diploma_df, self.homework_df, self.course_df

        self.create_base_df()
        self.create_diploma_df()
        self.create_homework_df(strict_filter=homework_strict_filter)
        self.create_course_df()

        self._processed = True

        return self.base_df, self.diploma_df, self.homework_df, self.course_df

    def print_results(self) -> None:
        """Выводит результаты обработки в консоль."""
        if self.diploma_df is not None:
            self._print_dataframe("Дипломные работы", self.diploma_df)

        if self.homework_df is not None:
            min_days = REVIEW_DEADLINES['HOMEWORK']
            self._print_dataframe(f"Домашние задания (≥{min_days} дней)", self.homework_df)

        if self.course_df is not None:
            self._print_dataframe("Курсовые работы", self.course_df)

    def _print_dataframe(self, title: str, df: pd.DataFrame) -> None:
        """
        Выводит DataFrame в консоль с заголовком.

        Args:
            title: Заголовок для вывода.
            df: DataFrame для вывода.
        """
        print(title)
        print('=' * 50)
        print(df.to_string())

    def get_dataframes_dict(self) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Возвращает словарь со всеми DataFrame.

        Returns:
            Словарь с ключами: base, diploma, homework, course.
        """
        return {
            'base': self.base_df,
            'diploma': self.diploma_df,
            'homework': self.homework_df,
            'course': self.course_df
        }

    @property
    def is_processed(self) -> bool:
        """
        Проверяет, были ли обработаны все данные.

        Returns:
            True если все DataFrame созданы, иначе False.
        """
        return all(df is not None for df in [
            self.base_df,
            self.diploma_df,
            self.homework_df,
            self.course_df
        ])


def list_df(homework_strict_filter: bool = False) -> Tuple[
    Optional[pd.DataFrame],
    Optional[pd.DataFrame],
    Optional[pd.DataFrame],
    Optional[pd.DataFrame]
]:
    """
    Создает и возвращает все DataFrame.

    Args:
        homework_strict_filter: Если True - использовать строгую фильтрацию для ДЗ

    Returns:
        Кортеж (base_df, diploma_df, homework_df, course_df)
    """
    processor = DataProcessor()
    return processor.process_all(homework_strict_filter=homework_strict_filter)


# # Пример использования
# if __name__ == "__main__":
#     # Создание экземпляра процессора
#     processor = DataProcessor()
#
#     print("=== ТЕСТ С >=2 ДНЕЙ (ТЕКУЩАЯ ЛОГИКА) ===")
#     base_df, diploma_df, homework_df1, course_df = processor.process_all(homework_strict_filter=False)
#     df_corse = course_df[course_df['Дней на проверке'] >= 2]
#     print(course_df.info())
#     print(df_corse.info())
#
#     print(df_corse.to_string())
#     processor.check_homework_stats()
#
#     # print("\n=== ТЕСТ С >2 ДНЕЙ (СТРОГАЯ ФИЛЬТРАЦИЯ) ===")
#     # # Сбросим флаг для повторной обработки
#     # processor._processed = False
#     # processor.homework_df = None
#     # base_df, diploma_df, homework_df2, course_df = processor.process_all(homework_strict_filter=True)
#
#     if processor.is_processed:
#         min_days = REVIEW_DEADLINES['HOMEWORK']
#         print("\n=== ИТОГИ ===")
#         print(f"Дипломных работ: {len(diploma_df) if diploma_df is not None else 0}")
#         print(f"Домашних заданий (≥{min_days} дней): {len(homework_df1) if homework_df1 is not None else 0}")
#         # print(f"Домашних заданий (>{min_days} дней): {len(homework_df2) if homework_df2 is not None else 0}")
#         print(f"Курсовых работ: {len(course_df) if course_df is not None else 0}")