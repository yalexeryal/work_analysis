import tkinter as tk
from tkinter import filedialog, messagebox
from main import MainProcessor
import os  # Добавляем импорт для открытия папки
from config.constants import DEFAULT_OUTPUT_FOLDER


class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Обработчик заданий студентов')
        self.geometry('400x250')  # Немного увеличили высоту окна для размещения новой кнопки

        # Метка заголовка
        label_title = tk.Label(self, text="Обработчик заданий студентов", font=("Arial Bold", 18))
        label_title.pack(pady=10)

        # Поле выбора файла
        self.file_entry = tk.Entry(self, width=50)
        self.file_entry.pack(padx=10, pady=10)

        button_browse = tk.Button(self, text='Выбрать файл', command=self.browse_file)
        button_browse.pack(pady=5)

        # Кнопка запуска обработки
        button_process = tk.Button(self, text='Запустить обработку', command=self.start_processing)
        button_process.pack(pady=10)

        # Новая кнопка для открытия папки с результатами
        button_open_output = tk.Button(self, text='Открыть папку с результатами', command=self.open_output_folder)
        button_open_output.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=(("Excel files", "*.xls*"), ("All files", "*.*")))
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def start_processing(self):
        input_file = self.file_entry.get()
        if not input_file.strip():
            messagebox.showwarning("Предупреждение", "Файл не выбран!")
            return

        try:
            processor = MainProcessor(input_file=input_file)
            processor.execute()
            messagebox.showinfo("Готово", "Обработка завершена успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Возникла ошибка: {e}")

    def open_output_folder(self):
        # Получаем путь к папке вывода
        output_folder = os.path.abspath(DEFAULT_OUTPUT_FOLDER)
        # Открываем папку в проводнике ОС
        os.startfile(output_folder)


# Запуск приложения
if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()