#!/usr/bin/env python3
"""
Основной файл для запуска приложения анализа рабочего времени
"""

import tkinter as tk
from gui.main_window import WorkAnalysisApp
import warnings
import os
import sys

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Игнорировать предупреждения pandas
warnings.filterwarnings('ignore')


def check_dependencies():
    """Проверка наличия необходимых зависимостей"""
    try:
        import pandas
        import numpy
        print("✓ Основные зависимости найдены")
        return True
    except ImportError as e:
        print(f"✗ Отсутствует зависимость: {e}")
        print("\nУстановите зависимости командой:")
        print("pip install -r requirements.txt")
        return False


def check_analysis_modules():
    """Проверка наличия модулей анализа"""
    try:
        from config import constants
        from core import create_dataframes
        from models import course, diploma, homework
        print("✓ Модули анализа найдены")
        return True
    except ImportError as e:
        print(f"⚠ Некоторые модули анализа не найдены: {e}")
        print("Приложение запустится в ограниченном режиме.")
        return False


def main():
    """Основная функция запуска приложения"""
    print("=" * 50)
    print("Work Analysis - GUI Application")
    print("=" * 50)

    # Проверка зависимостей
    if not check_dependencies():
        input("\nНажмите Enter для выхода...")
        return

    # Проверка модулей анализа
    check_analysis_modules()

    try:
        # Создаем главное окно
        root = tk.Tk()

        # Настройки окна
        root.title("Work Analysis")
        root.geometry("1100x800")

        # Минимальный размер окна
        root.minsize(900, 600)

        # Иконка приложения (если есть)
        try:
            root.iconbitmap('icon.ico')
        except:
            pass

        # Создание приложения
        app = WorkAnalysisApp(root)

        print("\nПриложение запущено успешно!")
        print("Журнал выполнения смотрите в интерфейсе приложения.")

        # Запуск главного цикла
        root.mainloop()

    except Exception as e:
        print(f"\n❌ Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()