"""
Модуль экспорта данных.
Сохраняет результаты в папку output/ в форматах Excel и TXT.
"""
import datetime

import pandas as pd

from config import OUTPUT_DIR


class DataExporter:
    """Экспорт данных в различные форматы в папку output/."""

    @staticmethod
    def _build_path(prefix: str, today: datetime.date, ext: str) -> str:
        """Формирует полный путь к выходному файлу."""
        return str(OUTPUT_DIR / f"{prefix}_{today}.{ext}")

    @staticmethod
    def save_excel(df: pd.DataFrame, prefix: str, today: datetime.date) -> None:
        """Сохраняет DataFrame в Excel в папку output/."""
        if df.empty:
            print(f"⚠️  Нет данных для выгрузки: {prefix}")
            return

        filepath = DataExporter._build_path(prefix, today, "xlsx")
        df.to_excel(filepath, index=False)
        print(f"✅ Сохранён файл: {filepath} ({len(df)} строк)")

    @staticmethod
    def save_kurs_txt(df: pd.DataFrame, today: datetime.date) -> None:
        """
        Сохраняет курсовые работы без проверяющих в TXT в папку output/.
        Формат: группировка по coord_id с табуляцией между полями.
        """
        # Фильтр: Проверяющий пустой И модуль не из self-assignment
        mask_empty = (
            df["Проверяющий"].isna()
            | (df["Проверяющий"].astype(str).str.strip() == "")
        )
        df_filtered = (
            df[mask_empty & ~df["is_self_assign_module"]]
            .dropna(subset=["coord_id"])
            .copy()
        )

        if df_filtered.empty:
            print("⚠️  Нет курсовых без проверяющих для выгрузки в TXT.")
            return

        filepath = DataExporter._build_path(
            "Курсовые_без_проверяющих", today, "txt"
        )
        grouped = df_filtered.groupby("coord_id")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Всем привет! \n")
            f.write("Курсовые работы без проверяющих.\n\n")

            for coord_id, group in grouped:
                coord_str = (
                    str(int(coord_id))
                    if isinstance(coord_id, (int, float))
                    else str(coord_id)
                )
                f.write(f"@{coord_str} \n")

                for _, row in group.iterrows():
                    module = str(row["Модуль"])
                    task = str(row["Название задания"])

                    sent_date = row["Отправлена"]
                    if isinstance(sent_date, pd.Timestamp):
                        sent_date = sent_date.strftime("%d.%m.%Y")
                    else:
                        sent_date = str(sent_date).split(" ")[0]

                    link = str(row["Ссылка на работу в админке"])
                    f.write(f"{module}\t{task}\t{sent_date}\t{link}\n")
                f.write("\n")

        print(f"✅ Сохранён TXT файл: {filepath} ({len(df_filtered)} строк)")
        