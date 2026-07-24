"""
Главный модуль приложения.
Оркестрирует работу всех компонентов: календарь, процессор, экспорт.
Создаёт папки input/ и output/ при первом запуске.
"""
import datetime
import sys

from calendar_module import RussianCalendar, CalendarConfigError
from config import Config, INPUT_DIR, OUTPUT_DIR
from exporter import DataExporter
from processor import DataProcessor, ModulesConfigError


def ensure_directories() -> None:
    """Создаёт папки input/ и output/, если они не существуют."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not Config.INPUT_FILE.exists():
        print(f"⚠️  Папка input/ создана, но файл не найден:")
        print(f"   {Config.INPUT_FILE}")
        print(f"   Поместите Excel-файл в папку input/ и запустите скрипт повторно.")


def should_export_dz_diploma() -> bool:
    """Проверяет, сегодня ли день выгрузки ДЗ и Дипломов (Пн/Ср/Пт)."""
    return datetime.datetime.today().weekday() in Config.CHECK_DAYS_DZ_DIPLOMA


def should_export_kurs() -> bool:
    """Проверяет, сегодня ли день выгрузки Курсовых (Чт)."""
    return datetime.datetime.today().weekday() in Config.CHECK_DAYS_KURS


def main() -> None:
    """Точка входа в приложение."""
    today = datetime.datetime.today().date()
    print(f"🚀 Запуск скрипта. Сегодня: {today}")
    print(f"📥 Папка входа:  {INPUT_DIR}")
    print(f"📤 Папка выхода: {OUTPUT_DIR}\n")

    # 0. Создаём папки
    ensure_directories()

    # 1. Инициализация компонентов
    try:
        calendar = RussianCalendar()
    except CalendarConfigError as e:
        print(f"❌ Ошибка календаря: {e}")
        sys.exit(1)

    try:
        processor = DataProcessor(calendar)
    except ModulesConfigError as e:
        print(f"❌ Ошибка конфигурации модулей: {e}")
        sys.exit(1)

    exporter = DataExporter()

    # 2. Базовая загрузка из input/
    try:
        df_base = processor.load_and_filter_base()
        print(f"📥 Загружено и отфильтровано: {len(df_base)} строк\n")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        sys.exit(1)

    # 3. Обогащение данными
    df_enriched = processor.add_module_flags(df_base)
    df_enriched = processor.add_sla_flags(df_enriched)

    # 4. Разделение на датасеты
    datasets = processor.get_datasets(df_enriched)

    # 5. Выгрузка в output/ в зависимости от дня недели
    if should_export_dz_diploma():
        print("📅 Сегодня день выгрузки ДЗ и Дипломов (Пн/Ср/Пт)")
        exporter.save_excel(datasets["diploma"], "Дипломные_работы", today)
        exporter.save_excel(datasets["dz"], "Непроверенные_ДЗ", today)
    else:
        print("📅 Сегодня не день выгрузки ДЗ и Дипломов. Пропускаем.")

    if should_export_kurs():
        print("📅 Сегодня день выгрузки Курсовых (Чт)")
        exporter.save_excel(datasets["kurs"], "Курсовые_работы", today)
        exporter.save_kurs_txt(datasets["kurs"], today)
    else:
        print("📅 Сегодня не день выгрузки Курсовых. Пропускаем.")

    # 6. Базовый файл сохраняем всегда
    print()
    exporter.save_excel(df_base, "Непроверенные_работы", today)

    print("\n🎉 Скрипт успешно завершён!")
    print(f"📂 Результаты в папке: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
    