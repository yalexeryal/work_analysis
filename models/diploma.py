import pandas as pd
from datetime import datetime, date
import os


def process_diploma_works(diploma_df, output_folder=None):
    """
    Обрабатывает DataFrame с дипломными работами и сохраняет в Excel-файл.

    Args:
        diploma_df (pd.DataFrame): Исходный DataFrame с данными о дипломных работах
        output_folder (str, optional): Папка для сохранения файла.
            Если None — сохраняется в текущую директорию.


    Returns:
        pd.DataFrame: Обработанный DataFrame (без столбца 'Возможные проверяющие')
    """
    # Проверка входных данных
    if not isinstance(diploma_df, pd.DataFrame):
        raise TypeError("diploma_df должен быть объектом pandas.DataFrame")

    if diploma_df.empty:
        print("Предупреждение: входной DataFrame пуст!")
        return diploma_df

    # # Удаление столбца 'Возможные проверяющие'
    # if 'Возможные проверяющие' in diploma_df.columns:
    #     diploma_df = diploma_df.drop(['Возможные проверяющие'], axis=1)
    # else:
    #     print("Столбец 'Возможные проверяющие' не найден — пропуск удаления.")

    # Формирование имени файла с текущей датой
    today_date = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"Дипломные_работы_{today_date}.xlsx"

    # Определение полного пути для сохранения
    if output_folder:
        # Проверяем существование папки
        if not os.path.exists(output_folder):
            raise FileNotFoundError(f"Папка не найдена: {output_folder}")
        output_path = os.path.join(output_folder, output_filename)
    else:
        output_path = output_filename

    # Сохранение в Excel
    try:
        diploma_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Файл успешно сохранён: {output_path}")
        print(f"Сохранено {len(diploma_df)} записей")
    except Exception as e:
        raise IOError(f"Ошибка при сохранении файла: {e}")

    return diploma_df
