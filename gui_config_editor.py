"""
GUI-редактор конфигурационных JSON-файлов.
Позволяет удобно редактировать:
  - data/calendar.json (праздники и рабочие субботы)
  - data/modules.json  (списки модулей)

Запуск:
    python gui_config_editor.py
"""
import datetime
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

from config import CALENDAR_JSON, MODULES_JSON


# ============================================================
# УТИЛИТЫ
# ============================================================
def load_json(path: Path) -> dict:
    """Загружает JSON-файл. Возвращает пустой dict при ошибке."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        messagebox.showerror("Ошибка чтения", f"{path.name}:\n{e}")
        return {}


def save_json(path: Path, data: dict) -> bool:
    """Сохраняет данные в JSON. Возвращает True при успехе."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        messagebox.showerror("Ошибка сохранения", f"{path.name}:\n{e}")
        return False


def is_valid_date(date_str: str) -> bool:
    """Проверяет, что строка — валидная дата в формате YYYY-MM-DD."""
    try:
        datetime.date.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def is_valid_module(module_str: str) -> bool:
    """Проверяет, что модуль — непустая строка без пробелов."""
    return bool(module_str) and module_str.strip() == module_str


# ============================================================
# ВКЛАДКА КАЛЕНДАРЯ
# ============================================================
class CalendarTab(ttk.Frame):
    """Вкладка для редактирования calendar.json."""

    def __init__(self, parent, json_path: Path):
        super().__init__(parent)
        self.json_path = json_path
        self.data = load_json(json_path)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # === Левая часть: Праздники ===
        left = ttk.LabelFrame(self, text="🎉 Праздничные дни (holidays)")
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.holidays_tree = self._make_list_block(
            left, "holidays", on_add=self._add_holiday
        )

        # === Правая часть: Рабочие субботы ===
        right = ttk.LabelFrame(self, text="💼 Рабочие субботы (extra_days)")
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.extra_tree = self._make_list_block(
            right, "extra_days", on_add=self._add_extra_day
        )

    def _make_list_block(self, parent, key: str, on_add):
        """Создаёт блок: список + кнопки управления."""
        # Список
        tree = ttk.Treeview(parent, columns=("date", "weekday"), show="headings",
                            selectmode="browse")
        tree.heading("date", text="Дата")
        tree.heading("weekday", text="День недели")
        tree.column("date", width=120)
        tree.column("weekday", width=150)
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        tree.bind("<Delete>", lambda e: self._delete_selected(tree, key))
        tree.bind("<Double-1>", lambda e: self._edit_selected(tree, key))

        # Кнопки
        btns = ttk.Frame(parent)
        btns.pack(fill="x", padx=5, pady=5)
        ttk.Button(btns, text="➕ Добавить",
                   command=on_add).pack(side="left", padx=2)
        ttk.Button(btns, text="✏️ Редактировать",
                   command=lambda: self._edit_selected(tree, key)).pack(side="left", padx=2)
        ttk.Button(btns, text="🗑 Удалить",
                   command=lambda: self._delete_selected(tree, key)).pack(side="left", padx=2)
        ttk.Button(btns, text="🔄 Сортировать",
                   command=lambda: self._sort_tree(tree, key)).pack(side="left", padx=2)

        return tree

    def _load_data(self):
        """Загружает данные из JSON в таблицы."""
        self._fill_tree(self.holidays_tree, self.data.get("holidays", []))
        self._fill_tree(self.extra_tree, self.data.get("extra_days", []))

    def _fill_tree(self, tree, items: list):
        """Заполняет Treeview списком дат."""
        for item in tree.get_children():
            tree.delete(item)
        for date_str in sorted(items):
            weekday = self._weekday_ru(date_str)
            tree.insert("", "end", values=(date_str, weekday))

    @staticmethod
    def _weekday_ru(date_str: str) -> str:
        """Возвращает название дня недели на русском."""
        try:
            d = datetime.date.fromisoformat(date_str)
            names = ["Понедельник", "Вторник", "Среда", "Четверг",
                     "Пятница", "Суббота", "Воскресенье"]
            return names[d.weekday()]
        except ValueError:
            return "❌ невалидная дата"

    def _ask_date(self, title="Ввод даты", initial="") -> str | None:
        """Диалог ввода даты."""
        return simpledialog.askstring(
            title, "Дата в формате YYYY-MM-DD:",
            initialvalue=initial, parent=self
        )

    def _add_holiday(self):
        date_str = self._ask_date("Добавить праздник")
        if not date_str:
            return
        if not is_valid_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте YYYY-MM-DD.")
            return
        holidays = self.data.setdefault("holidays", [])
        if date_str in holidays:
            messagebox.showinfo("Инфо", "Эта дата уже есть в списке.")
            return
        holidays.append(date_str)
        self._fill_tree(self.holidays_tree, holidays)

    def _add_extra_day(self):
        date_str = self._ask_date("Добавить рабочую субботу")
        if not date_str:
            return
        if not is_valid_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте YYYY-MM-DD.")
            return
        extra = self.data.setdefault("extra_days", [])
        if date_str in extra:
            messagebox.showinfo("Инфо", "Эта дата уже есть в списке.")
            return
        extra.append(date_str)
        self._fill_tree(self.extra_tree, extra)

    def _edit_selected(self, tree, key: str):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите строку для редактирования.")
            return
        old_date = tree.item(sel[0])["values"][0]
        new_date = self._ask_date("Редактировать дату", initial=old_date)
        if not new_date or new_date == old_date:
            return
        if not is_valid_date(new_date):
            messagebox.showerror("Ошибка", "Неверный формат даты.")
            return
        lst = self.data.get(key, [])
        if old_date in lst:
            lst.remove(old_date)
        if new_date not in lst:
            lst.append(new_date)
        self._fill_tree(tree, lst)

    def _delete_selected(self, tree, key: str):
        sel = tree.selection()
        if not sel:
            return
        date_str = tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Подтверждение", f"Удалить дату {date_str}?"):
            return
        lst = self.data.get(key, [])
        if date_str in lst:
            lst.remove(date_str)
        self._fill_tree(tree, lst)

    def _sort_tree(self, tree, key: str):
        lst = self.data.get(key, [])
        lst.sort()
        self._fill_tree(tree, lst)

    def save(self) -> bool:
        """Сохраняет данные в JSON."""
        # Сортируем списки перед сохранением
        if "holidays" in self.data:
            self.data["holidays"] = sorted(self.data["holidays"])
        if "extra_days" in self.data:
            self.data["extra_days"] = sorted(self.data["extra_days"])
        return save_json(self.json_path, self.data)


# ============================================================
# ВКЛАДКА МОДУЛЕЙ
# ============================================================
class ModulesTab(ttk.Frame):
    """Вкладка для редактирования modules.json."""

    def __init__(self, parent, json_path: Path):
        super().__init__(parent)
        self.json_path = json_path
        self.data = load_json(json_path)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # === Левая часть: Дипломные модули ===
        left = ttk.LabelFrame(self, text="🎓 Дипломные модули (diploma_modules)")
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.diploma_tree = self._make_module_block(left, "diploma_modules")

        # === Правая часть: Self-assignment модули ===
        right = ttk.LabelFrame(self, text="📝 Self-assignment модули (self_assignment_modules)")
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.self_tree = self._make_module_block(right, "self_assignment_modules")

    def _make_module_block(self, parent, key: str):
        """Создаёт блок: поиск + список + кнопки."""
        # Поиск
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", padx=5, pady=(5, 0))
        ttk.Label(search_frame, text="🔍 Поиск:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_var.trace_add("write", lambda *_: self._filter_tree(tree, key, search_var.get()))

        # Список
        tree = ttk.Treeview(parent, columns=("module",), show="headings",
                            selectmode="browse")
        tree.heading("module", text="Модуль")
        tree.column("module", width=250)
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        tree.bind("<Delete>", lambda e: self._delete_selected(tree, key))
        tree.bind("<Double-1>", lambda e: self._edit_selected(tree, key))

        # Кнопки
        btns = ttk.Frame(parent)
        btns.pack(fill="x", padx=5, pady=5)
        ttk.Button(btns, text="➕ Добавить",
                   command=lambda: self._add_module(tree, key)).pack(side="left", padx=2)
        ttk.Button(btns, text="✏️ Редактировать",
                   command=lambda: self._edit_selected(tree, key)).pack(side="left", padx=2)
        ttk.Button(btns, text="🗑 Удалить",
                   command=lambda: self._delete_selected(tree, key)).pack(side="left", padx=2)
        ttk.Button(btns, text="🔄 Сортировать",
                   command=lambda: self._sort_tree(tree, key)).pack(side="left", padx=2)

        return tree

    def _load_data(self):
        self._fill_tree(self.diploma_tree, self.data.get("diploma_modules", []))
        self._fill_tree(self.self_tree, self.data.get("self_assignment_modules", []))

    def _fill_tree(self, tree, items: list):
        for item in tree.get_children():
            tree.delete(item)
        for module in sorted(items):
            tree.insert("", "end", values=(module,))

    def _filter_tree(self, tree, key: str, query: str):
        """Фильтрует список по подстроке."""
        items = self.data.get(key, [])
        query = query.strip().lower()
        filtered = [m for m in items if query in m.lower()] if query else items
        self._fill_tree(tree, filtered)

    def _add_module(self, tree, key: str):
        module = simpledialog.askstring(
            "Добавить модуль", "Название модуля:", parent=self
        )
        if not module:
            return
        module = module.strip()
        if not is_valid_module(module):
            messagebox.showerror("Ошибка", "Модуль не должен содержать пробелы и быть пустым.")
            return
        lst = self.data.setdefault(key, [])
        if module in lst:
            messagebox.showinfo("Инфо", "Такой модуль уже есть в списке.")
            return
        lst.append(module)
        self._fill_tree(tree, lst)

    def _edit_selected(self, tree, key: str):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите модуль для редактирования.")
            return
        old_module = tree.item(sel[0])["values"][0]
        new_module = simpledialog.askstring(
            "Редактировать модуль", "Новое название:",
            initialvalue=old_module, parent=self
        )
        if not new_module or new_module == old_module:
            return
        new_module = new_module.strip()
        if not is_valid_module(new_module):
            messagebox.showerror("Ошибка", "Модуль не должен содержать пробелы.")
            return
        lst = self.data.get(key, [])
        if old_module in lst:
            lst.remove(old_module)
        if new_module not in lst:
            lst.append(new_module)
        self._fill_tree(tree, lst)

    def _delete_selected(self, tree, key: str):
        sel = tree.selection()
        if not sel:
            return
        module = tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Подтверждение", f"Удалить модуль '{module}'?"):
            return
        lst = self.data.get(key, [])
        if module in lst:
            lst.remove(module)
        self._fill_tree(tree, lst)

    def _sort_tree(self, tree, key: str):
        lst = self.data.get(key, [])
        lst.sort()
        self._fill_tree(tree, lst)

    def save(self) -> bool:
        if "diploma_modules" in self.data:
            self.data["diploma_modules"] = sorted(self.data["diploma_modules"])
        if "self_assignment_modules" in self.data:
            self.data["self_assignment_modules"] = sorted(self.data["self_assignment_modules"])
        return save_json(self.json_path, self.data)


# ============================================================
# ГЛАВНОЕ ОКНО
# ============================================================
class ConfigEditorApp(tk.Tk):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.title("🛠 Редактор конфигурации — Непроверенные работы")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self._build_menu()
        self._build_ui()
        self._build_statusbar()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="💾 Сохранить всё",
                              command=self._save_all, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Выход", command=self._on_close,
                              accelerator="Alt+F4")
        menubar.add_cascade(label="Файл", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="ℹ️ О программе", command=self._show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

        # Горячие клавиши
        self.bind_all("<Control-s>", lambda e: self._save_all())

    def _build_ui(self):
        # Вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.calendar_tab = CalendarTab(self.notebook, CALENDAR_JSON)
        self.modules_tab = ModulesTab(self.notebook, MODULES_JSON)

        self.notebook.add(self.calendar_tab, text="📅 Календарь")
        self.notebook.add(self.modules_tab, text="📚 Модули")

        # Нижняя панель с кнопками
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="💾 Сохранить всё",
                   command=self._save_all).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="🔄 Перезагрузить",
                   command=self._reload).pack(side="right", padx=5)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Готово")
        status = ttk.Label(self, textvariable=self.status_var,
                           relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

    def _save_all(self):
        """Сохраняет оба JSON-файла."""
        ok1 = self.calendar_tab.save()
        ok2 = self.modules_tab.save()
        if ok1 and ok2:
            self.status_var.set("✅ Все изменения сохранены")
            messagebox.showinfo("Успех", "Все изменения сохранены!")
        else:
            self.status_var.set("❌ Ошибка при сохранении")

    def _reload(self):
        """Перезагружает данные из файлов."""
        if not messagebox.askyesno(
            "Подтверждение",
            "Перезагрузить данные из файлов?\nНесохранённые изменения будут потеряны."
        ):
            return
        self.calendar_tab.data = load_json(CALENDAR_JSON)
        self.calendar_tab._load_data()
        self.modules_tab.data = load_json(MODULES_JSON)
        self.modules_tab._load_data()
        self.status_var.set("🔄 Данные перезагружены")

    def _on_close(self):
        """Обработка закрытия окна."""
        if messagebox.askyesno("Выход", "Выйти из приложения?\nНесохранённые изменения будут потеряны."):
            self.destroy()

    def _show_about(self):
        messagebox.showinfo(
            "О программе",
            "Редактор конфигурации\n\n"
            "Позволяет удобно редактировать:\n"
            "• data/calendar.json — праздники и рабочие субботы\n"
            "• data/modules.json  — списки модулей\n\n"
            "Горячие клавиши:\n"
            "• Ctrl+S — сохранить всё\n"
            "• Delete — удалить выбранную строку\n"
            "• Двойной клик — редактировать"
        )


# ============================================================
# ТОЧКА ВХОДА
# ============================================================
if __name__ == "__main__":
    app = ConfigEditorApp()
    app.mainloop()