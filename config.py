"""
Модуль конфигурации.
Содержит пути к папкам, константы, настройки SLA и фильтры БЮ.
Все списки модулей и календарь вынесены в JSON-файлы в папке data/.
"""
from pathlib import Path
from typing import List, Set

PROJECT_ROOT: Path = Path(__file__).parent.resolve()

INPUT_DIR: Path = PROJECT_ROOT / "input"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"
DATA_DIR: Path = PROJECT_ROOT / "data"

CALENDAR_JSON: Path = DATA_DIR / "calendar.json"
MODULES_JSON: Path = DATA_DIR / "modules.json"


class Config:
    INPUT_FILE: Path = INPUT_DIR / "Непроверенные_работы.xlsx"

    VALID_BYU: List[str] = ["ИТ-профессии - Рескилл", "ИТ-профессии - Апскилл"]
    ALLOWED_PRODUCTS_UPSKILL: List[str] = ["APBI", "APDX", "dj", "tab"]

    COLUMNS_TO_KEEP: List[str] = [
        "Модуль", "Название задания", "Ссылка на студента", "Отправлена",
        "Проверяющий", "Возможные проверяющие", "Ссылка на работу в ЛК эксперта",
        "Ссылка на работу в админке", "Тип задания", "coord_id",
    ]

    # ==========================================
    # SLA (в рабочих днях, не считая дня сдачи)
    # ==========================================
    SLA_DZ_DAYS: int = 3  # Исправлено на 2 (Пн -> Ср = 2 раб. дня)
    SLA_KURS_DAYS: int = 5  # Курсовые ждут проверки 5+ рабочих дней

    # ==========================================
    # ДНИ НЕДЕЛИ ДЛЯ ВЫГРУЗКИ (0=Пн ... 6=Вс)
    # ==========================================
    CHECK_DAYS_DZ_DIPLOMA: Set[int] = {0, 2, 4}  # Пн, Ср, Пт
    CHECK_DAYS_KURS: Set[int] = {3}  # Чт