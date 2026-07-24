"""
Модуль обработки данных.
Отвечает за загрузку из input/, фильтрацию, обогащение и разделение на категории.
Списки модулей загружаются из data/modules.json.
"""
import datetime
import json
import re
from pathlib import Path

import pandas as pd

from calendar_module import RussianCalendar
from config import Config, MODULES_JSON


class ModulesConfigError(Exception):
    """Ошибка конфигурации модулей."""
    pass


class DataProcessor:
    """
    Процессор данных: загрузка, фильтрация, обогащение флагами.

    Использует векторные операции pandas для высокой производительности.
    Списки модулей загружаются из JSON при инициализации.
    """

    def __init__(self, calendar: RussianCalendar, modules_json_path: Path = None):
        """
        Args:
            calendar: Экземпляр производственного календаря РФ.
            modules_json_path: Путь к JSON со списками модулей.
                               По умолчанию — из config.MODULES_JSON.
        """
        self.calendar = calendar
        self.today = datetime.datetime.today().date()

        # Загружаем списки модулей из JSON
        self.diploma_modules, self.self_assignment_modules = self._load_modules(
            modules_json_path or MODULES_JSON
        )

        # Предкомпилированные regex для быстрого матчинга модулей
        dip_pattern = (
            r"^("
            + "|".join(re.escape(m) for m in self.diploma_modules)
            + r")(-.*)?$"
        )
        self.diploma_regex = re.compile(dip_pattern, re.IGNORECASE)

        self_pattern = (
            r"^("
            + "|".join(re.escape(m) for m in self.self_assignment_modules)
            + r")(-.*)?$"
        )
        self.self_assign_regex = re.compile(self_pattern, re.IGNORECASE)

        print(
            f"📚 Модули загружены: "
            f"{len(self.diploma_modules)} дипломных, "
            f"{len(self.self_assignment_modules)} self-assignment."
        )

    @staticmethod
    def _load_modules(json_path: Path) -> tuple:
        """
        Загружает списки модулей из JSON-файла.

        Raises:
            ModulesConfigError: Если файл не найден или имеет неверный формат.
        """
        if not json_path.exists():
            raise ModulesConfigError(
                f"Файл со списками модулей не найден: {json_path}\n"
                f"Создайте файл и укажите в нём diploma_modules и self_assignment_modules."
            )

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ModulesConfigError(f"Ошибка чтения JSON: {e}")

        diploma = data.get("diploma_modules")
        self_assign = data.get("self_assignment_modules")

        if not isinstance(diploma, list) or not isinstance(self_assign, list):
            raise ModulesConfigError(
                "В JSON должны быть массивы 'diploma_modules' и 'self_assignment_modules'."
            )

        for name, lst in [
            ("diploma_modules", diploma),
            ("self_assignment_modules", self_assign),
        ]:
            if not all(isinstance(item, str) for item in lst):
                raise ModulesConfigError(
                    f"Все элементы в '{name}' должны быть строками."
                )

        return diploma, self_assign

    def load_and_filter_base(self) -> pd.DataFrame:
        """
        Загружает Excel из папки input/ и применяет базовую фильтрацию.

        Raises:
            FileNotFoundError: Если исходный файл не найден в input/.
        """
        input_path = Config.INPUT_FILE

        if not input_path.exists():
            raise FileNotFoundError(
                f"Входной файл не найден: {input_path}\n"
                f"Пожалуйста, поместите файл в папку: {Config.INPUT_DIR}"
            )

        df = pd.read_excel(input_path)

        # Фильтр по БЮ
        mask_byu = df["БЮ"].isin(Config.VALID_BYU)

        # Фильтр по Продукту (для Апскилла)
        mask_upskill_product = (
            (df["БЮ"] == "ИТ-профессии - Апскилл")
            & (df["Продукт"].isin(Config.ALLOWED_PRODUCTS_UPSKILL))
        )
        mask_reskill = df["БЮ"] == "ИТ-профессии - Рескилл"

        final_mask = mask_reskill | mask_upskill_product
        df_filtered = df[mask_byu & final_mask].copy()

        # Оставляем только нужные колонки
        existing_cols = [
            col for col in Config.COLUMNS_TO_KEEP if col in df_filtered.columns
        ]
        return df_filtered[existing_cols]

    def add_module_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Добавляет булевы флаги: дипломный модуль / self-assignment модуль.
        Использует векторный regex (в разы быстрее, чем apply).
        """
        df = df.copy()
        modules_str = df["Модуль"].astype(str)
        df["is_diploma_module"] = modules_str.str.match(self.diploma_regex, na=False)
        df["is_self_assign_module"] = modules_str.str.match(
            self.self_assign_regex, na=False
        )
        return df

    def add_sla_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Считает рабочие дни ожидания и проставляет флаги прохождения SLA."""
        df = df.copy()
        df["Отправлена_date"] = pd.to_datetime(
            df["Отправлена"], errors="coerce"
        ).dt.date

        df["wait_days"] = df["Отправлена_date"].apply(
            lambda x: self.calendar.count_working_days(x, self.today)
            if pd.notna(x)
            else 0
        )

        df["sla_dz_passed"] = df["wait_days"] >= Config.SLA_DZ_DAYS
        df["sla_kurs_passed"] = df["wait_days"] >= Config.SLA_KURS_DAYS

        return df

    def get_datasets(self, df: pd.DataFrame) -> dict:
        """
        Разделяет обогащённый DataFrame на категории с учётом SLA.

        Returns:
            dict с ключами: 'diploma', 'dz', 'kurs'.
        """
        drop_cols = [
            "is_diploma_module",
            "is_self_assign_module",
            "Отправлена_date",
            "wait_days",
            "sla_dz_passed",
            "sla_kurs_passed",
        ]

        # 1. Дипломы (Тип=Диплом И модуль из списка дипломных)
        mask_diploma = (df["Тип задания"] == "Диплом") & df["is_diploma_module"]
        diploma_df = df[mask_diploma].drop(columns=drop_cols, errors="ignore")

        # 2. ДЗ (Тип=ДЗ И прошло >= 2 рабочих дней)
        mask_dz = (df["Тип задания"] == "ДЗ") & df["sla_dz_passed"]
        dz_df = df[mask_dz].drop(columns=drop_cols, errors="ignore")

        # 3. Курсовые (Тип=Диплом, НО модуль НЕ из дипломных + SLA >= 5 дней)
        mask_kurs = (
            (df["Тип задания"] == "Диплом")
            & (~df["is_diploma_module"])
            & df["sla_kurs_passed"]
        )
        kurs_df = df[mask_kurs].copy()

        return {
            "diploma": diploma_df,
            "dz": dz_df,
            "kurs": kurs_df,
        }
