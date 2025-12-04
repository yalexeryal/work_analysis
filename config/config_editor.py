"""
Интерфейс для редактирования конфигурационных данных.
"""
from datetime import datetime
from config.config_loader import ConfigManager


class ConfigEditor:
    """Редактор конфигурационных данных."""

    def __init__(self):
        self.manager = ConfigManager('config')

    def show_menu(self):
        """Показывает меню редактора."""
        while True:
            print("\n" + "=" * 50)
            print("РЕДАКТОР КОНФИГУРАЦИЙ")
            print("=" * 50)
            print("1. Просмотр данных")
            print("2. Редактирование координаторов")
            print("3. Редактирование праздников")
            print("4. Редактирование модулей")
            print("5. Сохранить все изменения")
            print("6. Перезагрузить из файлов")
            print("0. Выход")

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                self.view_data()
            elif choice == '2':
                self.edit_coordinators()
            elif choice == '3':
                self.edit_holidays()
            elif choice == '4':
                self.edit_modules()
            elif choice == '5':
                self.manager.save_all()
            elif choice == '6':
                self.manager.reload()
                print("Конфигурация перезагружена")
            elif choice == '0':
                print("Выход из редактора")
                break
            else:
                print("Неверный выбор")

    def view_data(self):
        """Просмотр данных."""
        print("\n" + "-" * 30)
        print("ПРОСМОТР ДАННЫХ")
        print("-" * 30)
        print("1. Координаторы")
        print("2. Ведущие координаторы")
        print("3. Праздники")
        print("4. Дипломные модули")
        print("5. Модули самозакрепления")

        choice = input("\nВыберите данные для просмотра: ").strip()

        config = self.manager.get_config()

        if choice == '1':
            print("\nКоординаторы:")
            for uid, name in config['COORDINATORS'].items():
                print(f"  {uid}: {name}")
        elif choice == '2':
            print("\nВедущие координаторы:")
            for lead, professions in config['LEAD_COORDINATORS_TO_PROFESSION'].items():
                print(f"  {lead}: {', '.join(professions)}")
        elif choice == '3':
            print("\nПраздники:")
            for d in sorted(config['HOLIDAYS']):
                print(f"  {d.isoformat()}")
        elif choice == '4':
            print("\nДипломные модули:")
            for i, module in enumerate(sorted(config['DIPLOMA_MODULES']), 1):
                print(f"  {i:3}. {module}")
        elif choice == '5':
            print("\nМодули самозакрепления:")
            for i, module in enumerate(sorted(config['SELF_ASSIGNMENT_MODULES']), 1):
                print(f"  {i:3}. {module}")

    def edit_coordinators(self):
        """Редактирование координаторов."""
        while True:
            print("\n" + "-" * 30)
            print("РЕДАКТИРОВАНИЕ КООРДИНАТОРОВ")
            print("-" * 30)
            print("1. Добавить координатора")
            print("2. Удалить координатора")
            print("3. Изменить имя координатора")
            print("0. Назад")

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                try:
                    uid = int(input("UID координатора: "))
                    name = input("Имя координатора: ").strip()
                    self.manager.add_coordinator(uid, name)
                except ValueError:
                    print("Ошибка: UID должен быть числом")
            elif choice == '2':
                try:
                    uid = int(input("UID координатора для удаления: "))
                    self.manager.remove_coordinator(uid)
                except ValueError:
                    print("Ошибка: UID должен быть числом")
            elif choice == '3':
                try:
                    uid = int(input("UID координатора: "))
                    new_name = input("Новое имя: ").strip()
                    self.manager.update_coordinator(uid, new_name)
                except ValueError:
                    print("Ошибка: UID должен быть числом")
            elif choice == '0':
                break

    def edit_holidays(self):
        """Редактирование праздников."""
        while True:
            print("\n" + "-" * 30)
            print("РЕДАКТИРОВАНИЕ ПРАЗДНИКОВ")
            print("-" * 30)
            print("1. Добавить праздник")
            print("2. Удалить праздник")
            print("0. Назад")

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                date_str = input("Дата (ГГГГ-ММ-ДД): ").strip()
                try:
                    holiday_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.manager.add_holiday(holiday_date)
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ГГГГ-ММ-ДД")
            elif choice == '2':
                date_str = input("Дата (ГГГГ-ММ-ДД): ").strip()
                try:
                    holiday_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.manager.remove_holiday(holiday_date)
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ГГГГ-ММ-ДД")
            elif choice == '0':
                break

    def edit_modules(self):
        """Редактирование модулей."""
        while True:
            print("\n" + "-" * 30)
            print("РЕДАКТИРОВАНИЕ МОДУЛЕЙ")
            print("-" * 30)
            print("1. Добавить дипломный модуль")
            print("2. Удалить дипломный модуль")
            print("0. Назад")

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                module = input("Название модуля: ").strip()
                self.manager.add_diploma_module(module)
            elif choice == '2':
                module = input("Название модуля: ").strip()
                self.manager.remove_diploma_module(module)
            elif choice == '0':
                break


def edit_config_from_cli():
    """Запуск редактора из командной строки."""
    editor = ConfigEditor()
    editor.show_menu()


if __name__ == "__main__":
    edit_config_from_cli()