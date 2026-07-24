"""Тесты экспорта данных."""
import datetime

import pandas as pd
import pytest

from exporter import DataExporter


def test_save_excel_creates_file(tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    import exporter
    monkeypatch.setattr(exporter, "OUTPUT_DIR", tmp_path)

    df = pd.DataFrame({"a": [1, 2, 3]})
    today = datetime.date(2026, 7, 24)
    DataExporter.save_excel(df, "test", today)

    assert (tmp_path / f"test_{today}.xlsx").exists()


def test_save_excel_empty_df(capsys):
    df = pd.DataFrame()
    DataExporter.save_excel(df, "empty", datetime.date.today())
    captured = capsys.readouterr()
    assert "⚠️" in captured.out
    