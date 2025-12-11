"""
Адаптер для интеграции существующей логики обработки в GUI приложение.
"""
import pandas as pd
from datetime import datetime
import traceback
from typing import Dict, Any, Tuple, Optional
import os

# Импорт существующих модулей
try:
    from config.constants import DEFAULT_OUTPUT_FOLDER, DEFAULT_INPUT_FILE
    from core.create_dataframes import DataProcessor
    from models.course import CourseWorksProcessor
    from models.diploma import process_diploma_works
    from models.homework import process_unverified_works

    HAS_ANALYSIS_MODULES = True
except ImportError as e:
    print(f"Предупреждение: Некоторые модули анализа не найдены: {e}")
    HAS_ANALYSIS_MODULES = False


class AnalysisAdapter:
    """Адаптер для интеграции существующей логики обработки."""

    def __init__(self, input_file: str, output_folder: str = None):
        """
        Инициализация адаптера.

        Args:
            input_file: Путь к входному файлу
            output_folder: Папка для сохранения результатов (опционально)
        """
        self.input_file = input_file
        # self.output_folder = output_folder or os.path.join(os.path.dirname(input_file), "output")
        self.output_folder = DEFAULT_OUTPUT_FOLDER or os.path.join(os.path.dirname(input_file), "output")
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.day_name = datetime.now().strftime('%A')

        # Создаем папку для выходных данных если её нет
        os.makedirs(self.output_folder, exist_ok=True)

    def validate_file(self) -> Tuple[bool, str]:
        """
        Проверяет файл на корректность.

        Returns:
            Кортеж (успешно, сообщение)
        """
        if not os.path.exists(self.input_file):
            return False, f"Файл '{self.input_file}' не найден"

        if not self.input_file.endswith(('.xlsx', '.xls', '.csv')):
            return False, "Поддерживаются только файлы Excel (.xlsx, .xls) и CSV"

        try:
            # Быстрая проверка что файл можно прочитать
            if self.input_file.endswith('.csv'):
                pd.read_csv(self.input_file, nrows=1)
            else:
                pd.read_excel(self.input_file, nrows=1)
            return True, "Файл корректен"
        except Exception as e:
            return False, f"Ошибка чтения файла: {str(e)}"

    def get_file_info(self) -> Dict[str, Any]:
        """
        Получает информацию о файле.

        Returns:
            Словарь с информацией о файле
        """
        info = {
            "filename": os.path.basename(self.input_file),
            "path": os.path.dirname(self.input_file),
            "size_kb": os.path.getsize(self.input_file) / 1024,
            "modified": datetime.fromtimestamp(os.path.getmtime(self.input_file)).strftime("%Y-%m-%d %H:%M"),
            "created": datetime.fromtimestamp(os.path.getctime(self.input_file)).strftime("%Y-%m-%d %H:%M"),
        }

        try:
            # Получаем информацию о данных
            if self.input_file.endswith('.csv'):
                df = pd.read_csv(self.input_file, nrows=1000)  # Читаем первые 1000 строк для анализа
            else:
                df = pd.read_excel(self.input_file, nrows=1000)

            info.update({
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "sample_data": df.head(5).to_dict('records'),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
            })

            # Проверяем наличие ожидаемых колонок
            expected_columns = ['Дата', 'Время начала', 'Время окончания', 'Тип задачи', 'Описание']
            missing_columns = [col for col in expected_columns if col not in df.columns]
            info["missing_columns"] = missing_columns

        except Exception as e:
            info["error"] = f"Ошибка анализа файла: {str(e)}"

        return info

    def process_with_existing_logic(self) -> Dict[str, Any]:
        """
        Запускает существующую логику обработки.

        Returns:
            Словарь с результатами обработки
        """
        if not HAS_ANALYSIS_MODULES:
            return {
                "success": False,
                "error": "Модули анализа не найдены. Проверьте установку зависимостей.",
                "details": "Убедитесь, что все файлы проекта скопированы правильно."
            }

        try:
            # Создаем процессор по аналогии с MainProcessor
            processor = DataProcessor(self.input_file)
            base_df, diploma_df, homework_df, course_df = processor.process_all()

            # Собираем статистику
            stats = {
                "total_records": len(base_df) if base_df is not None else 0,
                "diploma_records": len(diploma_df) if diploma_df is not None else 0,
                "homework_records": len(homework_df) if homework_df is not None else 0,
                "course_records": len(course_df) if course_df is not None else 0,
                "date": self.today_date,
                "day": self.day_name
            }

            # Обрабатываем данные в зависимости от дня недели
            output_files = []

            if self.day_name == 'Thursday':
                # Обработка курсовых работ
                course_processor = CourseWorksProcessor()
                course_processor.process_course_works(course_df, self.output_folder, strict_filter=False)
                output_files.append(os.path.join(self.output_folder, "course_works_output.xlsx"))
            else:
                # Обработка дипломных работ
                if diploma_df is not None and not diploma_df.empty:
                    process_diploma_works(diploma_df, self.output_folder)
                    output_files.append(os.path.join(self.output_folder, "diploma_works_output.xlsx"))

                # Обработка домашних работ
                if homework_df is not None and not homework_df.empty:
                    process_unverified_works(homework_df, self.output_folder)
                    output_files.append(os.path.join(self.output_folder, "homework_output.xlsx"))

            # Проверяем какие файлы создались
            created_files = []
            for file_path in output_files:
                if os.path.exists(file_path):
                    created_files.append({
                        "name": os.path.basename(file_path),
                        "path": file_path,
                        "size_kb": os.path.getsize(file_path) / 1024
                    })

            return {
                "success": True,
                "statistics": stats,
                "created_files": created_files,
                "output_folder": self.output_folder,
                "message": f"Обработка завершена успешно! Создано файлов: {len(created_files)}"
            }

        except Exception as e:
            error_details = traceback.format_exc()
            return {
                "success": False,
                "error": str(e),
                "details": error_details,
                "statistics": None
            }

    def simple_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Простой анализ данных без использования сложной логики.

        Args:
            df: DataFrame с данными

        Returns:
            Словарь с результатами анализа
        """
        if df is None or df.empty:
            return {"error": "Нет данных для анализа"}

        try:
            results = {}

            # Базовая статистика
            results["total_records"] = len(df)
            results["total_columns"] = len(df.columns)
            results["columns"] = list(df.columns)

            # Анализ по датам если есть столбец с датой
            date_columns = [col for col in df.columns if 'дата' in col.lower() or 'date' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    results["date_range"] = {
                        "min": df[date_col].min().strftime("%Y-%m-%d") if not pd.isna(df[date_col].min()) else None,
                        "max": df[date_col].max().strftime("%Y-%m-%d") if not pd.isna(df[date_col].max()) else None,
                        "unique_days": df[date_col].dt.date.nunique() if not df[date_col].isna().all() else 0
                    }
                except:
                    pass

            # Анализ по типам задач если есть соответствующий столбец
            type_columns = [col for col in df.columns if 'тип' in col.lower() or 'type' in col.lower()]
            if type_columns:
                type_col = type_columns[0]
                type_counts = df[type_col].value_counts().to_dict()
                results["task_types"] = type_counts

            # Анализ по времени если есть столбцы времени
            time_columns = [col for col in df.columns if 'время' in col.lower() or 'time' in col.lower()]
            if len(time_columns) >= 2:
                start_col = time_columns[0]
                end_col = time_columns[1]

                try:
                    # Преобразуем время
                    df['start_time'] = pd.to_datetime(df[start_col], errors='coerce')
                    df['end_time'] = pd.to_datetime(df[end_col], errors='coerce')

                    # Рассчитываем длительность
                    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600  # в часах

                    results["time_analysis"] = {
                        "total_hours": df['duration'].sum(),
                        "avg_duration": df['duration'].mean(),
                        "max_duration": df['duration'].max(),
                        "min_duration": df['duration'].min()
                    }
                except:
                    pass

            return results

        except Exception as e:
            return {"error": f"Ошибка при анализе: {str(e)}"}