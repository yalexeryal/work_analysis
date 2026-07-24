"""Тесты производственного календаря."""
import datetime
import json

import pytest

from calendar_module import RussianCalendar, CalendarConfigError


@pytest.fixture
def sample_calendar_json(tmp_path):
    data = {
        "holidays": ["2026-01-01", "2026-01-07", "2026-05-01"],
        "extra_days": ["2026-02-28"],
    }
    path = tmp_path / "calendar.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_weekday_is_working(sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    assert cal.is_working_day(datetime.date(2026, 7, 21)) is True


def test_weekend_is_not_working(sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    assert cal.is_working_day(datetime.date(2026, 7, 25)) is False
    assert cal.is_working_day(datetime.date(2026, 7, 26)) is False


def test_holiday_is_not_working(sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    assert cal.is_working_day(datetime.date(2026, 1, 1)) is False


def test_working_weekend(sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    assert cal.is_working_day(datetime.date(2026, 2, 28)) is True


def test_count_working_days(sample_calendar_json):
    cal = RussianCalendar(json_path=sample_calendar_json)
    assert cal.count_working_days(
        datetime.date(2026, 7, 20),
        datetime.date(2026, 7, 24),
    ) == 4


def test_missing_json(tmp_path):
    with pytest.raises(CalendarConfigError):
        RussianCalendar(json_path=tmp_path / "no.json")


def test_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{broken", encoding="utf-8")
    with pytest.raises(CalendarConfigError):
        RussianCalendar(json_path=bad)
