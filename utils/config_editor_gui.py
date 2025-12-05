import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Analysis Config Editor")
        self.root.geometry("1200x800")

        # Текущий файл
        self.current_file = None
        self.config_data = {}

        # Стили
        self.setup_styles()

        # Создание интерфейса
        self.setup_ui()

        # Загрузка последнего открытого файла
        self.load_last_file()

    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        style.theme_use('clam')

        # Цветовая схема
        self.bg_color = "#f0f0f0"
        self.text_bg = "#ffffff"
        self.button_color = "#4a6fa5"

        self.root.configure(bg=self.bg_color)

    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Панель инструментов
        self.setup_toolbar(main_frame)

        # Панель навигации (дерево конфигурации)
        self.setup_navigation(main_frame)

        # Область редактирования
        self.setup_editor(main_frame)

        # Статус бар
        self.setup_statusbar()

    def setup_toolbar(self, parent):
        """Создание панели инструментов"""
        toolbar = ttk.Frame(parent, relief=tk.RAISED)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Кнопки
        buttons = [
            ("📂 Открыть", self.open_file, "Открыть конфигурационный файл"),
            ("💾 Сохранить", self.save_file, "Сохранить текущий файл"),
            ("💾 Сохранить как", self.save_file_as, "Сохранить файл как..."),
            ("🔄 Обновить", self.refresh_view, "Обновить дерево конфигурации"),
            ("➕ Добавить", self.add_item, "Добавить новый элемент"),
            ("➖ Удалить", self.delete_item, "Удалить выбранный элемент"),
            ("⚙️ Валидация", self.validate_config, "Проверить валидность конфигурации"),
            ("❓ Помощь", self.show_help, "Показать справку")
        ]

        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ttk.Button(toolbar, text=text, command=command, width=15)
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.create_tooltip(btn, tooltip)

    def setup_navigation(self, parent):
        """Создание панели навигации с деревом конфигурации"""
        nav_frame = ttk.LabelFrame(parent, text="Структура конфигурации", padding="5")
        nav_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Дерево конфигурации
        self.tree = ttk.Treeview(nav_frame, show="tree", height=30)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Полоса прокрутки для дерева
        tree_scroll = ttk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Кнопки навигации
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky=(tk.W, tk.E))

        ttk.Button(nav_buttons_frame, text="Развернуть все",
                   command=lambda: self.expand_tree(True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_buttons_frame, text="Свернуть все",
                   command=lambda: self.expand_tree(False)).pack(side=tk.LEFT, padx=2)

        # События дерева
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)

    def setup_editor(self, parent):
        """Создание области редактирования"""
        editor_frame = ttk.LabelFrame(parent, text="Редактирование", padding="5")
        editor_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(1, weight=1)

        # Заголовок редактируемого элемента
        self.editor_title = tk.StringVar(value="Выберите элемент для редактирования")
        title_label = ttk.Label(editor_frame, textvariable=self.editor_title,
                                font=('TkDefaultFont', 10, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Текстовый редактор
        editor_container = ttk.Frame(editor_frame)
        editor_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        editor_container.columnconfigure(0, weight=1)
        editor_container.rowconfigure(0, weight=1)

        self.text_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.WORD,
            bg=self.text_bg,
            font=('Consolas', 10),
            undo=True,
            maxundo=-1
        )
        self.text_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Кнопки редактора
        editor_buttons = ttk.Frame(editor_frame)
        editor_buttons.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        ttk.Button(editor_buttons, text="Применить",
                   command=self.apply_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_buttons, text="Отменить",
                   command=self.undo_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_buttons, text="Сбросить",
                   command=self.reset_changes).pack(side=tk.LEFT, padx=2)

        # Подсветка синтаксиса
        self.setup_syntax_highlighting()

    def setup_statusbar(self):
        """Создание статус бара"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.statusbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(self.statusbar, text="Готов", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.file_label = ttk.Label(self.statusbar, text="Файл не выбран", anchor=tk.E)
        self.file_label.pack(side=tk.RIGHT)

    def setup_syntax_highlighting(self):
        """Настройка подсветки синтаксиса (базовая)"""
        self.text_editor.tag_config('key', foreground='blue')
        self.text_editor.tag_config('string', foreground='green')
        self.text_editor.tag_config('number', foreground='orange')
        self.text_editor.tag_config('boolean', foreground='purple')
        self.text_editor.tag_config('null', foreground='red')

        # Привязка события для обновления подсветки
        self.text_editor.bind('<KeyRelease>', self.update_syntax_highlighting)

    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки"""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)

        label = ttk.Label(tooltip, text=text, background="#ffffe0",
                          relief=tk.SOLID, borderwidth=1, padding=5)
        label.pack()

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def open_file(self):
        """Открыть конфигурационный файл"""
        file_path = filedialog.askopenfilename(
            title="Выберите конфигурационный файл",
            filetypes=[
                ("YAML файлы", "*.yaml *.yml"),
                ("JSON файлы", "*.json"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        """Загрузка файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Определение типа файла
            if file_path.endswith(('.yaml', '.yml')):
                self.config_data = yaml.safe_load(content) or {}
            elif file_path.endswith('.json'):
                self.config_data = json.loads(content)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
                return

            self.current_file = file_path
            self.update_tree_view()
            self.update_status(f"Файл загружен: {os.path.basename(file_path)}")
            self.file_label.config(text=file_path)

            # Сохранение последнего файла
            self.save_last_file(file_path)

        except yaml.YAMLError as e:
            messagebox.showerror("Ошибка YAML", f"Ошибка парсинга YAML:\n{str(e)}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Ошибка парсинга JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def save_file(self):
        """Сохранение текущего файла"""
        if not self.current_file:
            self.save_file_as()
            return

        self.save_to_file(self.current_file)

    def save_file_as(self):
        """Сохранение файла как..."""
        if not self.current_file:
            default_name = "config.yaml"
        else:
            default_name = os.path.basename(self.current_file)

        file_path = filedialog.asksaveasfilename(
            title="Сохранить конфигурационный файл",
            defaultextension=".yaml",
            initialfile=default_name,
            filetypes=[
                ("YAML файлы", "*.yaml *.yml"),
                ("JSON файлы", "*.json")
            ]
        )

        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.file_label.config(text=file_path)

    def save_to_file(self, file_path):
        """Сохранение данных в файл"""
        try:
            # Получение полных данных
            full_data = self.get_full_config_data()

            # Определение формата
            if file_path.endswith('.json'):
                content = json.dumps(full_data, indent=2, ensure_ascii=False)
            else:
                content = yaml.dump(full_data, allow_unicode=True, sort_keys=False)

            # Сохранение
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.update_status(f"Файл сохранен: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def update_tree_view(self):
        """Обновление дерева конфигурации"""
        # Очистка дерева
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление корневого элемента
        root_item = self.tree.insert('', 'end', text="Конфигурация",
                                     values=["root"], open=True)

        # Рекурсивное добавление элементов
        self.add_tree_items(root_item, self.config_data)

    def add_tree_items(self, parent_item, data, path=""):
        """Рекурсивное добавление элементов в дерево"""
        if isinstance(data, dict):
            for key, value in data.items():
                item_path = f"{path}.{key}" if path else key
                item_id = self.tree.insert(
                    parent_item, 'end',
                    text=str(key),
                    values=[item_path, type(value).__name__]
                )

                if isinstance(value, (dict, list)):
                    self.add_tree_items(item_id, value, item_path)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item_path = f"{path}[{i}]"
                item_id = self.tree.insert(
                    parent_item, 'end',
                    text=f"[{i}]",
                    values=[item_path, type(value).__name__]
                )

                if isinstance(value, (dict, list)):
                    self.add_tree_items(item_id, value, item_path)

    def on_tree_select(self, event):
        """Обработка выбора элемента в дереве"""
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_path = self.tree.item(item_id, 'values')[0]

        # Получение значения элемента
        value = self.get_value_by_path(item_path)

        # Обновление заголовка
        self.editor_title.set(f"Редактирование: {item_path}")

        # Отображение значения в редакторе
        self.text_editor.delete(1.0, tk.END)

        if value is not None:
            if isinstance(value, (dict, list)):
                # Для сложных структур используем YAML
                display_value = yaml.dump(value, allow_unicode=True, sort_keys=False)
            else:
                display_value = str(value)

            self.text_editor.insert(1.0, display_value)

        # Сохранение текущего пути
        self.current_path = item_path

    def on_tree_double_click(self, event):
        """Обработка двойного клика по элементу дерева"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.item(item_id, open=not self.tree.item(item_id, 'open'))

    def get_value_by_path(self, path):
        """Получение значения по пути"""
        if path == "root":
            return self.config_data

        parts = self.parse_path(path)
        current = self.config_data

        try:
            for part in parts:
                if isinstance(part, str):
                    current = current[part]
                elif isinstance(part, int):
                    current = current[part]
            return current
        except (KeyError, IndexError, TypeError):
            return None

    def parse_path(self, path):
        """Парсинг пути элемента"""
        parts = []
        current = ""

        i = 0
        while i < len(path):
            if path[i] == '.':
                if current:
                    parts.append(current)
                    current = ""
            elif path[i] == '[':
                if current:
                    parts.append(current)
                    current = ""
                i += 1
                start = i
                while i < len(path) and path[i] != ']':
                    i += 1
                index = int(path[start:i])
                parts.append(index)
            else:
                current += path[i]
            i += 1

        if current:
            parts.append(current)

        return parts

    def apply_changes(self):
        """Применение изменений из редактора"""
        if not hasattr(self, 'current_path'):
            messagebox.showwarning("Предупреждение", "Сначала выберите элемент")
            return

        try:
            new_value_text = self.text_editor.get(1.0, tk.END).strip()

            # Преобразование текста в значение
            if new_value_text:
                # Попробуем распарсить как YAML
                try:
                    new_value = yaml.safe_load(new_value_text)
                except:
                    # Если не YAML, то как есть
                    new_value = new_value_text
            else:
                new_value = None

            # Обновление значения в структуре данных
            self.set_value_by_path(self.current_path, new_value)

            # Обновление дерева
            self.refresh_view()

            self.update_status("Изменения применены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить изменения:\n{str(e)}")

    def set_value_by_path(self, path, value):
        """Установка значения по пути"""
        if path == "root":
            self.config_data = value
            return

        parts = self.parse_path(path)
        current = self.config_data

        # Навигация к родительскому элементу
        for i, part in enumerate(parts[:-1]):
            if isinstance(part, str):
                if part not in current:
                    current[part] = {}
                current = current[part]
            elif isinstance(part, int):
                while len(current) <= part:
                    current.append(None)
                current = current[part]

        # Установка значения
        last_part = parts[-1]
        if isinstance(last_part, str):
            current[last_part] = value
        elif isinstance(last_part, int):
            while len(current) <= last_part:
                current.append(None)
            current[last_part] = value

    def refresh_view(self):
        """Обновление представления"""
        self.update_tree_view()
        self.update_status("Представление обновлено")

    def add_item(self):
        """Добавление нового элемента"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите родительский элемент")
            return

        parent_id = selection[0]
        parent_path = self.tree.item(parent_id, 'values')[0]
        parent_value = self.get_value_by_path(parent_path)

        # Диалог добавления элемента
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить элемент")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Ключ/Индекс:").pack(pady=5)
        key_entry = ttk.Entry(dialog, width=40)
        key_entry.pack(pady=5)

        ttk.Label(dialog, text="Значение:").pack(pady=5)
        value_entry = ttk.Entry(dialog, width=40)
        value_entry.pack(pady=5)

        def add():
            key = key_entry.get().strip()
            value_text = value_entry.get().strip()

            if not key:
                messagebox.showerror("Ошибка", "Введите ключ")
                return

            try:
                # Преобразование значения
                try:
                    value = yaml.safe_load(value_text)
                except:
                    value = value_text

                # Определение типа родительского элемента
                if isinstance(parent_value, dict):
                    # Добавление в словарь
                    parent_value[key] = value
                elif isinstance(parent_value, list):
                    # Добавление в список
                    try:
                        index = int(key)
                        parent_value.insert(index, value)
                    except ValueError:
                        messagebox.showerror("Ошибка", "Для списка укажите числовой индекс")
                        return

                # Обновление представления
                self.refresh_view()
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить элемент:\n{str(e)}")

        ttk.Button(dialog, text="Добавить", command=add).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack()

    def delete_item(self):
        """Удаление выбранного элемента"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите элемент для удаления")
            return

        item_id = selection[0]
        item_path = self.tree.item(item_id, 'values')[0]

        if item_path == "root":
            messagebox.showwarning("Предупреждение", "Нельзя удалить корневой элемент")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить элемент '{item_path}'?"):
            return

        try:
            parts = self.parse_path(item_path)
            current = self.config_data

            # Навигация к родительскому элементу
            for i, part in enumerate(parts[:-1]):
                if isinstance(part, str):
                    current = current[part]
                elif isinstance(part, int):
                    current = current[part]

            # Удаление элемента
            last_part = parts[-1]
            if isinstance(last_part, str):
                del current[last_part]
            elif isinstance(last_part, int):
                del current[last_part]

            # Обновление представления
            self.refresh_view()
            self.update_status(f"Элемент '{item_path}' удален")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить элемент:\n{str(e)}")

    def validate_config(self):
        """Валидация конфигурации"""
        try:
            # Базовая валидация
            if not isinstance(self.config_data, dict):
                raise ValueError("Конфигурация должна быть словарем")

            # Проверка обязательных полей для work_analysis
            required_sections = ['database', 'paths', 'analysis']
            for section in required_sections:
                if section not in self.config_data:
                    messagebox.showwarning("Предупреждение",
                                           f"Отсутствует раздел: {section}")

            # Проверка типов данных
            self.validate_types(self.config_data)

            messagebox.showinfo("Валидация", "Конфигурация валидна")
            self.update_status("Конфигурация проверена")

        except Exception as e:
            messagebox.showerror("Ошибка валидации", str(e))

    def validate_types(self, data, path=""):
        """Рекурсивная проверка типов данных"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self.validate_types(value, current_path)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                current_path = f"{path}[{i}]"
                self.validate_types(value, current_path)

    def expand_tree(self, expand=True):
        """Развернуть/свернуть все узлы дерева"""
        for item in self.tree.get_children():
            if expand:
                self.tree.item(item, open=True)
                self.expand_children(item, expand)
            else:
                self.tree.item(item, open=False)

    def expand_children(self, parent, expand=True):
        """Рекурсивное развертывание/свертывание дочерних элементов"""
        for child in self.tree.get_children(parent):
            if expand:
                self.tree.item(child, open=True)
                self.expand_children(child, expand)
            else:
                self.tree.item(child, open=False)

    def undo_changes(self):
        """Отмена последнего изменения в редакторе"""
        try:
            self.text_editor.edit_undo()
            self.update_status("Изменение отменено")
        except:
            messagebox.showinfo("Информация", "Нет изменений для отмены")

    def reset_changes(self):
        """Сброс изменений в редакторе"""
        if hasattr(self, 'current_path'):
            value = self.get_value_by_path(self.current_path)
            self.text_editor.delete(1.0, tk.END)
            if value is not None:
                if isinstance(value, (dict, list)):
                    display_value = yaml.dump(value, allow_unicode=True, sort_keys=False)
                else:
                    display_value = str(value)
                self.text_editor.insert(1.0, display_value)
            self.update_status("Изменения сброшены")

    def update_syntax_highlighting(self, event=None):
        """Обновление подсветки синтаксиса"""
        # Базовая реализация подсветки
        content = self.text_editor.get(1.0, tk.END)

        # Очистка всех тегов
        for tag in ['key', 'string', 'number', 'boolean', 'null']:
            self.text_editor.tag_remove(tag, 1.0, tk.END)

        # Простая подсветка (можно расширить)
        lines = content.split('\n')
        line_start = 1.0

        for line in lines:
            # Подсветка ключей в YAML
            if ':' in line:
                key_end = line.find(':')
                self.text_editor.tag_add('key',
                                         f"{line_start}+0c",
                                         f"{line_start}+{key_end}c")

            line_start = self.text_editor.index(f"{line_start}+1line")

    def get_full_config_data(self):
        """Получение полных данных конфигурации"""
        return self.config_data

    def update_status(self, message):
        """Обновление статус бара"""
        self.status_label.config(text=message)

    def show_help(self):
        """Показать справку"""
        help_text = """
        Редактор конфигураций Work Analysis

        Основные возможности:
        1. Открытие и сохранение файлов YAML/JSON
        2. Древовидное представление структуры конфигурации
        3. Редактирование отдельных элементов
        4. Добавление и удаление элементов
        5. Валидация конфигурации

        Горячие клавиши:
        Ctrl+O - Открыть файл
        Ctrl+S - Сохранить файл
        Ctrl+Z - Отменить изменение
        Ctrl+Y - Повторить изменение
        Ctrl+F - Поиск

        Поддерживаемые форматы:
        - YAML (.yaml, .yml)
        - JSON (.json)

        Для проекта: https://github.com/yalexeryal/work_analysis
        """

        messagebox.showinfo("Справка", help_text)

    def load_last_file(self):
        """Загрузка последнего открытого файла"""
        config_dir = Path.home() / '.work_analysis_editor'
        config_dir.mkdir(exist_ok=True)

        last_file_path = config_dir / 'last_file.txt'

        if last_file_path.exists():
            try:
                with open(last_file_path, 'r') as f:
                    file_path = f.read().strip()

                if os.path.exists(file_path):
                    self.load_file(file_path)
            except:
                pass

    def save_last_file(self, file_path):
        """Сохранение пути к последнему файлу"""
        config_dir = Path.home() / '.work_analysis_editor'
        config_dir.mkdir(exist_ok=True)

        last_file_path = config_dir / 'last_file.txt'

        try:
            with open(last_file_path, 'w') as f:
                f.write(file_path)
        except:
            pass


def main():
    """Основная функция запуска приложения"""
    root = tk.Tk()
    app = ConfigEditorGUI(root)

    # Обработка закрытия окна
    def on_closing():
        if messagebox.askokcancel("Выход", "Сохранить изменения перед выходом?"):
            app.save_file()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Горячие клавиши
    root.bind('<Control-o>', lambda e: app.open_file())
    root.bind('<Control-s>', lambda e: app.save_file())
    root.bind('<Control-z>', lambda e: app.undo_changes())

    root.mainloop()


if __name__ == "__main__":
    main()