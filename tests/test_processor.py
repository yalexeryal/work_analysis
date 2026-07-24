"""Тесты процессора данных."""
import datetime
import json

import pandas as pd
import pytest

from calendar_module import RussianCalendar
from processor import DataProcessor, ModulesConfigError


@pytest.fixture
def sample_modules_json(tmp_path):
    data = {
        "diploma_modules": ["dip-abi", "dip-dmar", "diplom-abu"],
        "self_assignment_modules": ["abd", "tab", "sql"],
    }
    path = tmp_path / "modules.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def sample_calendar_json(tmp_path):
    data = {"holidays": ["2026-01-01"], "extra_days": []}
    path = tmp_path / "calendar.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_module_matching_diploma(sample_modules_json, sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    processor = DataProcessor(cal, modules_json_path=sample_modules_json)

    data = {"Модуль": ["dip-abi", "dip-abi-123", "DIP-ABI", "dip-abigail"]}
    df = pd.DataFrame(data)
    df = processor.add_module_flags(df)

    # ✅ Используем == вместо is (pandas возвращает numpy.bool_)
    assert df.iloc[0]["is_diploma_module"] == True   # точное совпадение
    assert df.iloc[1]["is_diploma_module"] == True   # с номером потока
    assert df.iloc[2]["is_diploma_module"] == True   # игнор регистра
    assert df.iloc[3]["is_diploma_module"] == False  # НЕ должно матчиться


def test_module_matching_self_assignment(sample_modules_json, sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    processor = DataProcessor(cal, modules_json_path=sample_modules_json)

    data = {"Модуль": ["abd", "abd-pro", "random", "tab"]}
    df = pd.DataFrame(data)
    df = processor.add_module_flags(df)

    # ✅ Используем == вместо is
    assert df.iloc[0]["is_self_assign_module"] == True
    assert df.iloc[1]["is_self_assign_module"] == True
    assert df.iloc[2]["is_self_assign_module"] == False
    assert df.iloc[3]["is_self_assign_module"] == True


def test_missing_modules_json(tmp_path, sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    with pytest.raises(ModulesConfigError):
        DataProcessor(cal, modules_json_path=tmp_path / "no.json")


def test_sla_dz_passed(sample_modules_json, sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    processor = DataProcessor(cal, modules_json_path=sample_modules_json)
    processor.today = datetime.date(2026, 7, 22)  # Ср

    data = {
        "Тип задания": ["ДЗ"],
        "Модуль": ["tab"],
        "Отправлена": [datetime.date(2026, 7, 20)],  # Пн
    }
    df = pd.DataFrame(data)
    df = processor.add_module_flags(df)
    df = processor.add_sla_flags(df)
    datasets = processor.get_datasets(df)

    assert len(datasets["dz"]) == 1


def test_sla_kurs_passed(sample_modules_json, sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    processor = DataProcessor(cal, modules_json_path=sample_modules_json)
    processor.today = datetime.date(2026, 7, 24)  # Пт

    data = {
        "Тип задания": ["Диплом"],
        "Модуль": ["some-kurs-module"],
        "Отправлена": [datetime.date(2026, 7, 13)],
    }
    df = pd.DataFrame(data)
    df = processor.add_module_flags(df)
    df = processor.add_sla_flags(df)
    datasets = processor.get_datasets(df)

    assert len(datasets["kurs"]) == 1