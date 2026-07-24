"""
Модуль работы с производственным календарём РФ.
Данные о праздниках и переносах загружаются из data/calendar.json.
"""
import datetime
import json
from pathlib import Path
from typing import Set

from config import CALENDAR_JSON


class CalendarConfigError(Exception):
    """Ошибка конфигурации календаря."""
    pass


class RussianCalendar:
    """
    Производственный календарь РФ.
    Данные берутся из файла data/calendar.json.
    """

    def __init__(self, json_path: Path = None):
        """
        Загружает календарь из JSON-файла.

        Args:
            json_path: Путь к JSON-файлу. По умолчанию — из config.CALENDAR_JSON.

        Raises:
            CalendarConfigError: Если файл не найден или имеет неверный формат.
        """
        path = json_path or CALENDAR_JSON

        if not path.exists():
            raise CalendarConfigError(
                f"Файл календаря не найден: {path}\n"
                f"Создайте файл и укажите в нём праздники и рабочие субботы."
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CalendarConfigError(f"Ошибка чтения JSON: {e}")

        try:
            self.holidays_set: Set[datetime.date] = {
                datetime.date.fromisoformat(d) for d in data.get("holidays", [])
            }
            self.working_weekends: Set[datetime.date] = {
                datetime.date.fromisoformat(d) for d in data.get("extra_days", [])
            }
        except (ValueError, TypeError) as e:
            raise CalendarConfigError(
                f"Неверный формат даты в JSON. Ожидался YYYY-MM-DD. Ошибка: {e}"
            )

        print(
            f"📅 Календарь загружен: "
            f"{len(self.holidays_set)} праздников, "
            f"{len(self.working_weekends)} рабочих суббот."
        )

    def is_working_day(self, date: datetime.date) -> bool:
        """
        Проверяет, является ли указанная дата рабочим днём.

        Логика:
        1. Если дата в extra_days → рабочий день (даже если это суббота).
        2. Если дата в holidays → нерабочий день.
        3. Если это суббота/воскресенье → нерабочий день.
        4. Иначе → рабочий день.
        """
        if date in self.working_weekends:
            return True
        if date.weekday() >= 5:  # Суббота (5) или Воскресенье (6)
            return False
        if date in self.holidays_set:
            return False
        return True

    def count_working_days(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> int:
        """
        Считает количество рабочих дней между start_date и end_date.
        ВАЖНО: start_date (день сдачи работы) НЕ включается в расчёт.
        """
        if start_date is None or end_date is None:
            return 0

        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        if end_date <= start_date:
            return 0

        current = start_date + datetime.timedelta(days=1)
        count = 0
        while current <= end_date:
            if self.is_working_day(current):
                count += 1
            current += datetime.timedelta(days=1)
        return count
    