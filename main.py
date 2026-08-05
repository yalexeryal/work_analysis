"""
Главный модуль приложения.
Оркестрирует работу всех компонентов: календарь, процессор, экспорт.
"""
import datetime
import sys
from pathlib import Path

from calendar_module import RussianCalendar, CalendarConfigError
from config import Config, INPUT_DIR, OUTPUT_DIR
from exporter import DataExporter
from processor import DataProcessor, ModulesConfigError


def _clean_directory(directory: Path, keep_files: list[str] | None = None) -> None:
    """Очищает директорию от файлов и подпапок, сохраняя указанные исключения."""
    if not directory.exists():
        return
    exclusions = {"__init__.py"} if keep_files is None else set(keep_files)
    for item in directory.iterdir():
        if item.name in exclusions:
            continue
        try:
            if item.is_dir():
                for sub_item in item.rglob('*'):
                    if sub_item.is_file():
                        sub_item.unlink(missing_ok=True)
                item.rmdir()
            elif item.is_file():
                item.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Не удалось удалить {item}: {e}")


def ensure_directories() -> None:
    """Создаёт папки input/ и output/, если они не существуют."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def should_export_dz_diploma() -> bool:
    """Проверяет, сегодня ли день выгрузки ДЗ и Дипломов (Пн/Ср/Пт)."""
    return datetime.datetime.today().weekday() in Config.CHECK_DAYS_DZ_DIPLOMA


def should_export_kurs() -> bool:
    """Проверяет, сегодня ли день выгрузки Курсовых (Чт)."""
    return datetime.datetime.today().weekday() in Config.CHECK_DAYS_KURS


def main() -> None:
    """Точка входа в приложение."""
    today = datetime.datetime.today().date()
    print(f"🚀 Запуск скрипта. Сегодня: {today} (weekday={today.weekday()})")
    print(f"📥 Папка входа: {INPUT_DIR}")
    print(f"📤 Папка выхода: {OUTPUT_DIR}\n")

    print("🧹 Очищаю папку output/...")
    _clean_directory(OUTPUT_DIR)

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

    # Главный блок try-finally для гарантированной очистки input/
    try:
        # 2. Базовая загрузка из input/
        try:
            df_base = processor.load_and_filter_base()
            print(f"📥 Загружено и отфильтровано по БЮ: {len(df_base)} строк\n")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")
            sys.exit(1)

        # 3. Обогащение данными
        df_enriched = processor.add_module_flags(df_base)
        df_enriched = processor.add_sla_flags(df_enriched)

        # 4. Разделение на датасеты (здесь сработают отладочные принты)
        datasets = processor.get_datasets(df_enriched)

        # 5. Выгрузка ДЗ и Дипломов (Пн, Ср, Пт)
        if should_export_dz_diploma():
            print("📅 Сегодня день выгрузки ДЗ и Дипломов (Пн/Ср/Пт)")
            exporter.save_excel(datasets["diploma"], "Дипломные_работы", today)
            exporter.save_excel(datasets["dz"], "Непроверенные_ДЗ", today)
        else:
            print("📅 Сегодня не день выгрузки ДЗ и Дипломов. Пропускаем.")

        # 6. Выгрузка Курсовых (Чт)
        if should_export_kurs():
            print("📅 Сегодня день выгрузки Курсовых (Чт)")
            # TXT из базового набора (без SLA, но с фильтрацией проверяющих внутри экспортера)
            exporter.save_kurs_txt(datasets["kurs_base"], today)
            # Excel из набора с соблюдением SLA
            exporter.save_excel(datasets["kurs"], "Курсовые_работы", today)
        else:
            print("📅 Сегодня не день выгрузки Курсовых. Пропускаем.")

        # 7. Базовый файл сохраняем всегда
        print()
        exporter.save_excel(df_base, "Непроверенные_работы", today)

        print("\n🎉 Скрипт успешно завершён!")
        print(f"📂 Результаты в папке: {OUTPUT_DIR}")

    finally:
        # Выполняется всегда: и при успехе, и при любом исключении выше
        print("\n🧹 Очищаю папку input/...")
        _clean_directory(INPUT_DIR)


if __name__ == "__main__":
    main()