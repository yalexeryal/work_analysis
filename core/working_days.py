from datetime import date, timedelta, datetime
from typing import Set, Optional
from config.modules import holidays, extra_days


class WorkingDaysCalculator:
    """
    Калькулятор для работы с рабочими днями с учетом праздников и выходных.
    """

    def __init__(self) -> None:
        """Инициализирует калькулятор с пустыми множествами праздников и рабочих дней."""
        self.holidays: Set[date] = set()
        self.extra_working_days: Set[date] = set()

    def add_holiday(self, holiday_date: date) -> None:
        """
        Добавляет дату в список праздников.

        Args:
            holiday_date: Дата праздника
        """
        self.holidays.add(holiday_date)

    def add_extra_working_day(self, working_date: date) -> None:
        """
        Добавляет дату в список дополнительных рабочих дней.

        Args:
            working_date: Дата дополнительного рабочего дня
        """
        self.extra_working_days.add(working_date)

    def is_working_day(self, check_date: date) -> bool:
        """
        Проверяет, является ли день рабочим.

        Args:
            check_date: Дата для проверки

        Returns:
            True если день рабочий, иначе False
        """
        is_weekend = check_date.weekday() >= 5  # 5=Суббота, 6=Воскресенье
        is_holiday = check_date in self.holidays
        is_extra = check_date in self.extra_working_days

        return (not is_weekend and not is_holiday) or is_extra

    def calculate(self, start_date: date, end_date: date) -> int:
        """
        Подсчитывает количество рабочих дней между start_date и end_date (не включая start_date и end_date).

        Args:
            start_date: Начальная дата (не включается в подсчет)
            end_date: Конечная дата (не включается в подсчет)

        Returns:
            Количество рабочих дней между датами
        """
        total_days = 0
        current = start_date + timedelta(days=1)  # Начинаем со следующего дня после start_date

        while current < end_date:  # Не включаем end_date
            if self.is_working_day(current):
                total_days += 1
            current += timedelta(days=1)

        return total_days

    def calculate_inclusive(self, start_date: date, end_date: date) -> int:
        """
        Подсчитывает количество рабочих дней между start_date и end_date включительно.

        Args:
            start_date: Начальная дата (включается в подсчет)
            end_date: Конечная дата (включается в подсчет)

        Returns:
            Количество рабочих дней между датами включительно
        """
        if start_date > end_date:
            raise ValueError("start_date не может быть больше end_date")

        total_days = 0
        current = start_date

        while current <= end_date:
            if self.is_working_day(current):
                total_days += 1
            current += timedelta(days=1)

        return total_days

    def find_date_n_working_days_ago(self, end_date: date, n: int) -> date:
        """
        Находит дату, которая была n рабочих дней назад от end_date.

        Args:
            end_date: Конечная дата (не включается в подсчет)
            n: Количество рабочих дней назад

        Returns:
            Дата отсечения (включительно)
        """
        if n < 0:
            raise ValueError("n не может быть отрицательным")

        if n == 0:
            return end_date

        current = end_date - timedelta(days=1)
        working_days_found = 0

        while working_days_found < n:
            if self.is_working_day(current):
                working_days_found += 1
                if working_days_found == n:
                    return current

            current -= timedelta(days=1)

        return current

    def find_date_n_working_days_after(self, start_date: date, n: int) -> date:
        """
        Находит дату, которая будет через n рабочих дней после start_date.

        Args:
            start_date: Начальная дата (не включается в подсчет)
            n: Количество рабочих дней вперед

        Returns:
            Дата, которая будет через n рабочих дней
        """
        if n < 0:
            raise ValueError("n не может быть отрицательным")

        if n == 0:
            return start_date

        current = start_date + timedelta(days=1)
        working_days_count = 0

        while working_days_count < n:
            if self.is_working_day(current):
                working_days_count += 1
                if working_days_count == n:
                    return current

            current += timedelta(days=1)

        return current

    def find_date_n_working_days_ago_verbose(self, end_date: date, n: int) -> tuple[date, list[date]]:
        """
        Расширенная версия с отладочной информацией.

        Args:
            end_date: Конечная дата
            n: Количество рабочих дней назад

        Returns:
            Кортеж (результирующая_дата, список_найденных_рабочих_дней)
        """
        if n < 0:
            raise ValueError("n не может быть отрицательным")

        if n == 0:
            return end_date, []

        current = end_date - timedelta(days=1)
        working_days_found = 0
        found_working_days = []

        while working_days_found < n:
            if self.is_working_day(current):
                working_days_found += 1
                found_working_days.append(current)
                if working_days_found == n:
                    return current, found_working_days

            current -= timedelta(days=1)

        return current, found_working_days

    def get_working_days_count(self) -> tuple[int, int]:
        """
        Возвращает количество зарегистрированных праздников и дополнительных рабочих дней.

        Returns:
            Кортеж (количество_праздников, количество_дополнительных_рабочих_дней)
        """
        return len(self.holidays), len(self.extra_working_days)


def create_calculator(holidays, extra_days) -> WorkingDaysCalculator:
    """
    Создает и настраивает калькулятор рабочих дней.

    Returns:
        Настроенный экземпляр WorkingDaysCalculator
    """
    calculator = WorkingDaysCalculator()

    for holiday in holidays:
        calculator.add_holiday(holiday)

    for day in extra_days:
        calculator.add_extra_working_day(day)

    return calculator


def test_all_methods():
    """Тестирование всех методов калькулятора"""
    calc = create_calculator()

    print("ТЕСТИРОВАНИЕ ВСЕХ МЕТОДОВ КАЛЬКУЛЯТОРА:")
    print("=" * 50)

    # Тест метода calculate
    print("\n1. Метод calculate() - рабочие дни МЕЖДУ датами:")
    start_date = date(2025, 12, 25)
    end_date = date(2025, 12, 31)
    result = calc.calculate(start_date, end_date)
    print(f"   Рабочих дней между {start_date.strftime('%d.%m.%Y')} и {end_date.strftime('%d.%m.%Y')}: {result}")

    # Тест метода calculate_inclusive
    print("\n2. Метод calculate_inclusive() - рабочие дни ВКЛЮЧАЯ даты:")
    result_inc = calc.calculate_inclusive(start_date, end_date)
    print(
        f"   Рабочих дней между {start_date.strftime('%d.%m.%Y')} и {end_date.strftime('%d.%m.%Y')} включительно: {result_inc}")

    # Тест метода find_date_n_working_days_ago
    print("\n3. Метод find_date_n_working_days_ago() - дата отсечки:")
    test_dates = [
        (date(2026, 1, 14), 2),
        (date(2026, 1, 13), 2),
        (date(2026, 1, 12), 2),
        (date(2025, 12, 30), 2),
    ]

    for end_date, n in test_dates:
        result = calc.find_date_n_working_days_ago(end_date, n)
        print(f"   {end_date.strftime('%d.%m.%Y')} - {n} рабочих дня назад → {result.strftime('%d.%m.%Y')}")

    # Тест метода find_date_n_working_days_after
    print("\n4. Метод find_date_n_working_days_after() - дата вперед:")
    start_date_fwd = date(2025, 12, 25)
    n_fwd = 3
    result_fwd = calc.find_date_n_working_days_after(start_date_fwd, n_fwd)
    print(f"   {start_date_fwd.strftime('%d.%m.%Y')} + {n_fwd} рабочих дня вперед → {result_fwd.strftime('%d.%m.%Y')}")

    # Информация о калькуляторе
    print("\n5. Информация о калькуляторе:")
    holidays_count, extra_days_count = calc.get_working_days_count()
    print(f"   Загружено праздников: {holidays_count}")
    print(f"   Загружено дополнительных рабочих дней: {extra_days_count}")


def demonstrate_calculate_method():
    """Демонстрация работы метода calculate"""
    calc = create_calculator()

    print("\nДЕМОНСТРАЦИЯ МЕТОДА calculate():")
    print("=" * 40)

    # Примеры для метода calculate
    examples = [
        (date(2025, 12, 25), date(2025, 12, 31), "25.12 - 31.12"),
        (date(2025, 12, 29), date(2026, 1, 5), "29.12 - 05.01"),
        (date(2025, 12, 30), date(2026, 1, 12), "30.12 - 12.01"),
    ]

    for start, end, description in examples:
        result = calc.calculate(start, end)
        print(f"{description}: {result} рабочих дней")

        # Покажем какие дни считались
        current = start + timedelta(days=1)
        counted_days = []
        while current < end:
            if calc.is_working_day(current):
                counted_days.append(current.strftime('%d.%m'))
            current += timedelta(days=1)

        print(f"  Учтены дни: {counted_days}")


if __name__ == "__main__":
    calculator = create_calculator(holidays, extra_days)

    n = 2
    end_date = date(2026, 1, 13)
    start_date = date(2025, 12, 26)
    staff_day = calculator.find_date_n_working_days_ago(end_date, n)
    # staff_day = calculator.(date(2026,1,13), n)
    print(staff_day)
    day_ago = calculator.calculate(start_date, end_date)
    print(day_ago)