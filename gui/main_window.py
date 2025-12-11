import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import threading
from datetime import datetime

# Импортируем наш адаптер
try:
    from core.processor_adapter import AnalysisAdapter
except ImportError:
    # Если модуль не найден, создадим заглушку
    class AnalysisAdapter:
        def __init__(self, input_file, output_folder=None):
            self.input_file = input_file
            self.output_folder = output_folder or os.path.join(os.path.dirname(input_file), "../result_files")

        def validate_file(self):
            return False, "Модуль анализа не установлен"

        def get_file_info(self):
            return {"error": "Модуль анализа не установлен"}

        def process_with_existing_logic(self):
            return {"success": False, "error": "Модуль анализа не установлен"}


class WorkAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Analysis - Анализ рабочего времени")
        self.root.geometry("1000x800")

        # Переменные для данных
        self.excel_data = None
        self.file_path = None
        self.analysis_results = None
        self.processing = False

        # Стили
        self.setup_styles()

        # Создаем меню
        self.create_menu()

        # Создаем панель вкладок
        self.create_notebook()

        # Статус бар
        self.create_status_bar()

    def setup_styles(self):
        """Настройка стилей приложения"""
        style = ttk.Style()
        style.theme_use('clam')

        # Кастомные цвета
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#34495e'
        }

    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть Excel", command=self.load_excel_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Открыть CSV", command=self.load_csv_file)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit, accelerator="Ctrl+Q")

        # Меню Анализ
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)
        analysis_menu.add_command(label="Анализировать данные", command=self.start_analysis, accelerator="F5")
        analysis_menu.add_command(label="Быстрый анализ", command=self.quick_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Показать статистику", command=self.show_statistics)

        # Меню Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Настройки", command=self.show_settings)

        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Документация", command=self.show_documentation)
        help_menu.add_command(label="О программе", command=self.show_about)

        # Бинды клавиш
        self.root.bind('<Control-o>', lambda e: self.load_excel_file())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self.start_analysis())

    def create_notebook(self):
        """Создание вкладок приложения"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка загрузки
        self.create_loader_tab()

        # Вкладка просмотра данных
        self.create_viewer_tab()

        # Вкладка анализа
        self.create_analysis_tab()

        # Вкладка результатов
        self.create_results_tab()

        # Вкладка статистики
        self.create_statistics_tab()

    def create_loader_tab(self):
        """Создание вкладки загрузки файла"""
        self.loader_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loader_frame, text="📁 Загрузка")

        # Контейнер для центрирования
        container = ttk.Frame(self.loader_frame)
        container.pack(expand=True, fill='both', padx=50, pady=50)

        # Заголовок
        title_label = tk.Label(
            container,
            text="Work Analysis - Анализ рабочего времени",
            font=("Arial", 18, "bold"),
            fg=self.colors['primary']
        )
        title_label.pack(pady=(0, 30))

        # Карточка загрузки
        load_card = ttk.LabelFrame(container, text="Загрузка данных", padding=20)
        load_card.pack(fill='x', pady=10)

        # Кнопки загрузки
        btn_frame = ttk.Frame(load_card)
        btn_frame.pack(pady=10)

        self.load_excel_btn = tk.Button(
            btn_frame,
            text="📊 Загрузить Excel",
            command=self.load_excel_file,
            font=("Arial", 11),
            bg=self.colors['secondary'],
            fg="white",
            padx=25,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.load_excel_btn.pack(side='left', padx=5)

        self.load_csv_btn = tk.Button(
            btn_frame,
            text="📄 Загрузить CSV",
            command=self.load_csv_file,
            font=("Arial", 11),
            bg=self.colors['dark'],
            fg="white",
            padx=25,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.load_csv_btn.pack(side='left', padx=5)

        # Информация о файле
        info_card = ttk.LabelFrame(container, text="Информация о файле", padding=15)
        info_card.pack(fill='x', pady=20)

        self.file_info_text = tk.Text(
            info_card,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg=self.colors['light'],
            relief=tk.FLAT
        )
        self.file_info_text.pack(fill='x')

        # Инструкция
        self.create_instructions(container)

    def create_instructions(self, parent):
        """Создание блока с инструкциями"""
        instruction_card = ttk.LabelFrame(parent, text="📋 Инструкция", padding=15)
        instruction_card.pack(fill='x', pady=10)

        instructions = """
        Для корректной работы приложения, файл данных должен содержать следующие столбцы:

        Обязательные:
        • Дата (в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД)
        • Время начала (в формате ЧЧ:ММ)
        • Время окончания (в формате ЧЧ:ММ)

        Рекомендуемые:
        • Тип задачи (например: Диплом, Курсовая, Домашняя работа)
        • Описание (подробное описание задачи)
        • Студент (ФИО студента)
        • Предмет (название предмета)

        Поддерживаемые форматы: .xlsx, .xls, .csv
        """

        instruction_label = tk.Label(
            instruction_card,
            text=instructions,
            font=("Arial", 9),
            justify="left",
            anchor="w"
        )
        instruction_label.pack(fill='x')

    def create_viewer_tab(self):
        """Создание вкладки просмотра данных"""
        self.viewer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viewer_frame, text="👁️ Просмотр")

        # Панель управления
        control_frame = ttk.Frame(self.viewer_frame)
        control_frame.pack(fill='x', padx=10, pady=5)

        # Кнопки управления
        ttk.Button(control_frame, text="🔄 Обновить",
                   command=self.refresh_view).pack(side='left', padx=2)
        ttk.Button(control_frame, text="📊 Анализ",
                   command=self.start_analysis).pack(side='left', padx=2)
        ttk.Button(control_frame, text="📤 Экспорт в CSV",
                   command=self.export_to_csv).pack(side='left', padx=2)

        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side='right', padx=5)

        tk.Label(search_frame, text="Поиск:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)

        # Таблица для отображения данных
        self.create_data_table()

    def create_data_table(self):
        """Создание таблицы для отображения данных"""
        # Фрейм для таблицы и скроллбаров
        table_frame = ttk.Frame(self.viewer_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем Treeview с прокруткой
        columns = ("№", "Дата", "Начало", "Конец", "Длительность", "Тип", "Описание")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # Настройка колонок
        column_widths = {"№": 50, "Дата": 100, "Начало": 80, "Конец": 80,
                         "Длительность": 100, "Тип": 100, "Описание": 200}

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        # Теги для разных типов записей
        self.tree.tag_configure('diploma', background='#e8f4fd')
        self.tree.tag_configure('course', background='#f0f8e8')
        self.tree.tag_configure('homework', background='#fff8e1')

        # Скроллбары
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещение
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def create_analysis_tab(self):
        """Создание вкладки анализа"""
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="🔍 Анализ")

        # Основной контейнер
        main_container = ttk.Frame(self.analysis_frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Левая панель - настройки анализа
        left_panel = ttk.LabelFrame(main_container, text="Настройки анализа", padding=15)
        left_panel.pack(side='left', fill='y', padx=(0, 10))

        # Параметры анализа
        tk.Label(left_panel, text="Тип анализа:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(0, 10))

        self.analysis_type = tk.StringVar(value="auto")
        ttk.Radiobutton(left_panel, text="Авто (по дню недели)",
                        variable=self.analysis_type, value="auto").pack(anchor='w', pady=2)
        ttk.Radiobutton(left_panel, text="Полный анализ",
                        variable=self.analysis_type, value="full").pack(anchor='w', pady=2)
        ttk.Radiobutton(left_panel, text="Только дипломы",
                        variable=self.analysis_type, value="diploma").pack(anchor='w', pady=2)
        ttk.Radiobutton(left_panel, text="Только курсовые",
                        variable=self.analysis_type, value="course").pack(anchor='w', pady=2)

        # Опции
        options_frame = ttk.Frame(left_panel)
        options_frame.pack(fill='x', pady=20)

        self.create_charts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Создавать графики",
                        variable=self.create_charts_var).pack(anchor='w')

        self.export_results_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Экспортировать результаты",
                        variable=self.export_results_var).pack(anchor='w')

        # Кнопка запуска анализа
        self.analyze_btn = tk.Button(
            left_panel,
            text="🚀 Запустить анализ",
            command=self.start_analysis,
            font=("Arial", 11, "bold"),
            bg=self.colors['success'],
            fg="white",
            padx=30,
            pady=12,
            cursor="hand2"
        )
        self.analyze_btn.pack(pady=20)

        # Правая панель - прогресс и результаты
        right_panel = ttk.LabelFrame(main_container, text="Ход выполнения", padding=15)
        right_panel.pack(side='right', fill='both', expand=True)

        # Прогресс бар
        self.progress_label = tk.Label(right_panel, text="Готов к анализу", font=("Arial", 10))
        self.progress_label.pack(anchor='w', pady=(0, 5))

        self.progress_bar = ttk.Progressbar(right_panel, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(0, 20))

        # Лог выполнения
        log_frame = ttk.LabelFrame(right_panel, text="Лог выполнения", padding=10)
        log_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg='#f5f5f5',
            relief=tk.FLAT
        )
        self.log_text.pack(fill='both', expand=True)

        # Скроллбар для лога
        log_scroll = ttk.Scrollbar(self.log_text)
        log_scroll.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=log_scroll.set)
        log_scroll.config(command=self.log_text.yview)

    def create_results_tab(self):
        """Создание вкладки результатов"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📊 Результаты")

        # Здесь будут отображаться результаты анализа
        self.results_text = tk.Text(
            self.results_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg='white'
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Скроллбар для результатов
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side='right', fill='y')
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)

    def create_statistics_tab(self):
        """Создание вкладки статистики"""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📈 Статистика")

        # Будет реализовано позже
        placeholder = tk.Label(
            self.stats_frame,
            text="Статистика будет отображаться здесь после анализа",
            font=("Arial", 12)
        )
        placeholder.pack(pady=50)

    def create_status_bar(self):
        """Создание строки состояния"""
        status_frame = ttk.Frame(self.root, height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        # Левая часть - статус
        self.status_label = tk.Label(
            status_frame,
            text="Готово",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Правая часть - информация о файле
        self.file_status_label = tk.Label(
            status_frame,
            text="Файл не загружен",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.E,
            padx=10
        )
        self.file_status_label.pack(side=tk.RIGHT)

    # Основные методы обработки
    def load_excel_file(self):
        """Загрузка файла Excel"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл Excel",
            filetypes=[
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.load_file(file_path)

    def load_csv_file(self):
        """Загрузка CSV файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        """Общая функция загрузки файла"""
        try:
            self.update_status(f"Загрузка файла...")

            # Чтение файла
            if file_path.endswith('.csv'):
                self.excel_data = pd.read_csv(file_path)
            else:
                self.excel_data = pd.read_excel(file_path)

            self.file_path = file_path

            # Обновление информации о файле
            self.update_file_info()

            # Обновление таблицы
            self.refresh_view()

            # Переключение на вкладку просмотра
            self.notebook.select(1)

            messagebox.showinfo("Успех",
                                f"Файл успешно загружен!\n"
                                f"Строк: {len(self.excel_data)}\n"
                                f"Столбцов: {len(self.excel_data.columns)}")

            self.update_status(f"Файл загружен: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            self.update_status("Ошибка загрузки файла")

    def update_file_info(self):
        """Обновление информации о файле в интерфейсе"""
        if self.file_path and self.excel_data is not None:
            # Создаем адаптер для анализа файла
            adapter = AnalysisAdapter(self.file_path)

            # Получаем информацию о файле
            file_info = adapter.get_file_info()

            # Форматируем информацию для отображения
            info_text = ""

            if "error" not in file_info:
                info_text = f"""Файл: {file_info.get('filename', 'N/A')}
Путь: {file_info.get('path', 'N/A')}
Размер: {file_info.get('size_kb', 0):.1f} КБ
Дата изменения: {file_info.get('modified', 'N/A')}
Записей: {file_info.get('rows', 0)}
Столбцов: {file_info.get('columns', 0)}

Столбцы: {', '.join(file_info.get('column_names', []))}

"""

                # Проверяем обязательные столбцы
                missing = file_info.get('missing_columns', [])
                if missing:
                    info_text += f"\n⚠ Внимание: Отсутствуют столбцы:\n"
                    for col in missing:
                        info_text += f"  • {col}\n"
                else:
                    info_text += "\n✓ Все необходимые столбцы присутствуют\n"
            else:
                info_text = f"Ошибка анализа файла: {file_info['error']}"

            # Обновляем текстовое поле
            self.file_info_text.delete(1.0, tk.END)
            self.file_info_text.insert(1.0, info_text)

            # Обновляем статус бар
            self.file_status_label.config(
                text=f"{os.path.basename(self.file_path)} | {len(self.excel_data)} записей"
            )

    def refresh_view(self):
        """Обновление таблицы с данными"""
        if self.excel_data is not None:
            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Добавление данных
            for index, row in self.excel_data.head(200).iterrows():  # Показываем первые 200 строк
                values = [index + 1]  # Номер записи

                # Формируем значения для колонок
                for col in self.tree["columns"][1:]:  # Пропускаем колонку №
                    if col in self.excel_data.columns:
                        cell_value = str(row[col])
                        # Обрезаем длинные значения
                        if len(cell_value) > 50:
                            cell_value = cell_value[:47] + "..."
                        values.append(cell_value)
                    else:
                        values.append("")

                # Определяем тип записи для цветового кодирования
                tags = ()
                if 'Тип' in row:
                    task_type = str(row['Тип']).lower()
                    if 'диплом' in task_type:
                        tags = ('diploma',)
                    elif 'курс' in task_type:
                        tags = ('course',)
                    elif 'дом' in task_type:
                        tags = ('homework',)

                self.tree.insert("", "end", values=values, tags=tags)

            self.update_status(f"Отображено {min(len(self.excel_data), 200)} из {len(self.excel_data)} строк")

    def on_search(self, *args):
        """Обработка поиска в таблице"""
        if not self.excel_data is None:
            search_term = self.search_var.get().lower()
            if search_term:
                # Фильтруем данные
                mask = self.excel_data.astype(str).apply(
                    lambda row: row.str.contains(search_term, case=False, na=False).any(),
                    axis=1
                )
                filtered_data = self.excel_data[mask].head(200)

                # Очищаем и обновляем таблицу
                for item in self.tree.get_children():
                    self.tree.delete(item)

                for index, row in filtered_data.iterrows():
                    values = [index + 1]
                    for col in self.tree["columns"][1:]:
                        if col in filtered_data.columns:
                            cell_value = str(row[col])
                            if len(cell_value) > 50:
                                cell_value = cell_value[:47] + "..."
                            values.append(cell_value)
                        else:
                            values.append("")

                    tags = ()
                    if 'Тип' in row:
                        task_type = str(row['Тип']).lower()
                        if 'диплом' in task_type:
                            tags = ('diploma',)
                        elif 'курс' in task_type:
                            tags = ('course',)
                        elif 'дом' in task_type:
                            tags = ('homework',)

                    self.tree.insert("", "end", values=values, tags=tags)
            else:
                self.refresh_view()

    def start_analysis(self):
        """Запуск анализа данных в отдельном потоке"""
        if self.excel_data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных")
            return

        if self.processing:
            messagebox.showinfo("Информация", "Анализ уже выполняется")
            return

        # Запускаем в отдельном потоке
        self.processing = True
        self.analyze_btn.config(state='disabled', text="⏳ Анализ выполняется...")
        self.progress_bar.start()
        self.update_status("Выполняется анализ данных...")

        # Очищаем лог
        self.log_text.delete(1.0, tk.END)
        self.log("Начало анализа данных")
        self.log(f"Файл: {os.path.basename(self.file_path)}")
        self.log(f"Записей для анализа: {len(self.excel_data)}")

        # Запускаем анализ в отдельном потоке
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def run_analysis(self):
        """Запуск анализа (выполняется в отдельном потоке)"""
        try:
            # Создаем адаптер для анализа
            adapter = AnalysisAdapter(self.file_path)

            # Проверяем файл
            self.log("Проверка файла...")
            valid, message = adapter.validate_file()
            if not valid:
                self.log(f"Ошибка проверки: {message}")
                raise Exception(message)

            self.log("Файл проверен успешно")

            # Запускаем анализ
            self.log("Запуск обработки данных...")
            results = adapter.process_with_existing_logic()

            # Сохраняем результаты
            self.analysis_results = results

            # Обновляем интерфейс из основного потока
            self.root.after(0, self.on_analysis_complete, results)

        except Exception as e:
            error_msg = f"Ошибка при анализе: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.root.after(0, self.on_analysis_error, error_msg)

    def on_analysis_complete(self, results):
        """Обработка завершения анализа"""
        self.processing = False
        self.progress_bar.stop()
        self.analyze_btn.config(state='normal', text="🚀 Запустить анализ")

        if results.get('success', False):
            self.log("✅ Анализ завершен успешно!")
            self.update_status("Анализ завершен успешно")

            # Отображаем результаты
            self.display_results(results)

            # Показываем сообщение об успехе
            created_files = results.get('created_files', [])
            if created_files:
                file_list = "\n".join([f"• {f['name']} ({f['size_kb']:.1f} КБ)"
                                       for f in created_files])
                messagebox.showinfo(
                    "Анализ завершен",
                    f"Обработка завершена успешно!\n\n"
                    f"Создано файлов: {len(created_files)}\n"
                    f"Папка с результатами: {results.get('output_folder', 'N/A')}\n\n"
                    f"Файлы:\n{file_list}"
                )
            else:
                messagebox.showinfo(
                    "Анализ завершен",
                    results.get('message', 'Обработка завершена')
                )

            # Переключаемся на вкладку результатов
            self.notebook.select(3)
        else:
            error_msg = results.get('error', 'Неизвестная ошибка')
            self.log(f"❌ Ошибка: {error_msg}")
            messagebox.showerror("Ошибка анализа", error_msg)
            self.update_status("Ошибка анализа")

    def on_analysis_error(self, error_msg):
        """Обработка ошибки анализа"""
        self.processing = False
        self.progress_bar.stop()
        self.analyze_btn.config(state='normal', text="🚀 Запустить анализ")
        messagebox.showerror("Ошибка анализа", error_msg)
        self.update_status("Ошибка анализа")

    def display_results(self, results):
        """Отображение результатов анализа"""
        self.results_text.delete(1.0, tk.END)

        # Форматируем результаты
        result_text = "=" * 60 + "\n"
        result_text += "РЕЗУЛЬТАТЫ АНАЛИЗА\n"
        result_text += "=" * 60 + "\n\n"

        # Основная информация
        result_text += f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        result_text += f"Файл: {os.path.basename(self.file_path)}\n"
        result_text += f"Папка с результатами: {results.get('output_folder', 'N/A')}\n\n"

        # Статистика
        stats = results.get('statistics', {})
        if stats:
            result_text += "СТАТИСТИКА:\n"
            result_text += "-" * 40 + "\n"
            result_text += f"Всего записей: {stats.get('total_records', 0)}\n"
            result_text += f"Дипломные работы: {stats.get('diploma_records', 0)}\n"
            result_text += f"Курсовые работы: {stats.get('course_records', 0)}\n"
            result_text += f"Домашние работы: {stats.get('homework_records', 0)}\n"
            result_text += f"День недели: {stats.get('day', 'N/A')}\n\n"

        # Созданные файлы
        created_files = results.get('created_files', [])
        if created_files:
            result_text += "СОЗДАННЫЕ ФАЙЛЫ:\n"
            result_text += "-" * 40 + "\n"
            for file_info in created_files:
                result_text += f"• {file_info['name']}\n"
                result_text += f"  Размер: {file_info['size_kb']:.1f} КБ\n"
                result_text += f"  Путь: {file_info['path']}\n\n"

        # Сообщение
        if 'message' in results:
            result_text += "СООБЩЕНИЕ:\n"
            result_text += "-" * 40 + "\n"
            result_text += results['message'] + "\n\n"

        result_text += "=" * 60 + "\n"
        result_text += "Анализ завершен.\n"

        # Вставляем текст
        self.results_text.insert(1.0, result_text)

    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        # Обновляем из основного потока
        self.root.after(0, self._add_log_message, log_message)

    def _add_log_message(self, message):
        """Добавление сообщения в лог (вызывается из основного потока)"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def export_to_csv(self):
        """Экспорт данных в CSV"""
        if self.excel_data is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.excel_data.to_csv(file_path, index=False, encoding='utf-8')
                    messagebox.showinfo("Успех", f"Данные экспортированы в:\n{file_path}")
                    self.update_status(f"Экспорт завершен: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{str(e)}")

    def export_data(self):
        """Экспорт данных в различные форматы"""
        if self.excel_data is None:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.excel_data.to_csv(file_path, index=False, encoding='utf-8')
                elif file_path.endswith('.json'):
                    self.excel_data.to_json(file_path, orient='records', indent=2)
                else:
                    self.excel_data.to_excel(file_path, index=False)

                messagebox.showinfo("Успех", f"Данные экспортированы в:\n{file_path}")
                self.update_status(f"Экспорт завершен: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{str(e)}")

    def quick_analysis(self):
        """Быстрый анализ данных"""
        if self.excel_data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных")
            return

        try:
            self.update_status("Выполнение быстрого анализа...")

            # Используем адаптер для простого анализа
            adapter = AnalysisAdapter(self.file_path)
            results = adapter.simple_analysis(self.excel_data)

            if 'error' not in results:
                # Формируем отчет
                report = "БЫСТРЫЙ АНАЛИЗ\n" + "=" * 40 + "\n\n"
                report += f"Всего записей: {results.get('total_records', 0)}\n"
                report += f"Колонок: {results.get('total_columns', 0)}\n\n"

                # Анализ по датам
                if 'date_range' in results:
                    date_range = results['date_range']
                    report += "ДИАПАЗОН ДАТ:\n"
                    report += f"  Начало: {date_range.get('min', 'N/A')}\n"
                    report += f"  Конец: {date_range.get('max', 'N/A')}\n"
                    report += f"  Уникальных дней: {date_range.get('unique_days', 0)}\n\n"

                # Анализ по типам задач
                if 'task_types' in results:
                    task_types = results['task_types']
                    report += "РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:\n"
                    for task_type, count in task_types.items():
                        percentage = (count / results['total_records']) * 100
                        report += f"  {task_type}: {count} ({percentage:.1f}%)\n"
                    report += "\n"

                # Анализ времени
                if 'time_analysis' in results:
                    time_analysis = results['time_analysis']
                    report += "АНАЛИЗ ВРЕМЕНИ:\n"
                    report += f"  Всего часов: {time_analysis.get('total_hours', 0):.1f}\n"
                    report += f"  Средняя длительность: {time_analysis.get('avg_duration', 0):.2f} ч\n"
                    report += f"  Макс. длительность: {time_analysis.get('max_duration', 0):.2f} ч\n"
                    report += f"  Мин. длительность: {time_analysis.get('min_duration', 0):.2f} ч\n"

                messagebox.showinfo("Быстрый анализ", report)
            else:
                messagebox.showwarning("Предупреждение", results['error'])

            self.update_status("Быстрый анализ завершен")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе:\n{str(e)}")
            self.update_status("Ошибка анализа")

    def show_statistics(self):
        """Показать статистику"""
        if self.excel_data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных")
            return

        # Временная заглушка - будет реализовано в следующем шаге
        self.quick_analysis()

    def show_settings(self):
        """Показать настройки"""
        # Временная заглушка
        messagebox.showinfo("Настройки", "Раздел настроек находится в разработке")

    def show_documentation(self):
        """Показать документацию"""
        docs = """
        Work Analysis - Документация

        Основные функции:
        1. Загрузка данных - загрузите Excel или CSV файл
        2. Просмотр данных - просмотрите и отфильтруйте данные
        3. Анализ данных - запустите полный анализ
        4. Результаты - просмотрите результаты анализа

        Формат данных:
        Файл должен содержать как минимум столбцы:
        - Дата (в любом формате)
        - Время начала (ЧЧ:ММ)
        - Время окончания (ЧЧ:ММ)

        Рекомендуемые столбцы:
        - Тип задачи
        - Описание
        - Студент
        - Предмет

        Для получения подробной документации посетите:
        https://github.com/yalexeryal/work_analysis
        """

        messagebox.showinfo("Документация", docs)

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        Work Analysis

        Версия: 2.0.0 (GUI Edition)
        Автор: yalexeryal

        Приложение для анализа рабочего времени
        на основе данных из Excel файлов.

        Интегрирует существующую логику обработки
        из проекта work_analysis.

        GitHub: https://github.com/yalexeryal/work_analysis
        """

        messagebox.showinfo("О программе", about_text)

    def update_status(self, message):
        """Обновление строки состояния"""
        self.status_label.config(text=message)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = WorkAnalysisApp(root)
    root.mainloop()