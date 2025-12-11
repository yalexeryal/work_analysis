"""
Конфигурация для GUI приложения
"""

import os
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent.parent
GUI_DIR = BASE_DIR / "gui"
# DATA_DIR = BASE_DIR / "data"
DATA_DIR = "../original_files"
# OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR = "../result_files"

# Создаем необходимые директории
for directory in [DATA_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True)

# Настройки GUI
GUI_CONFIG = {
    "window_title": "Work Analysis",
    "default_size": "1100x800",
    "min_size": (900, 600),
    "theme": "clam",
    "font_family": "Arial",
    "font_size_normal": 10,
    "font_size_large": 12,
    "font_size_title": 16,
}

# Цветовая схема
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#17a2b8',
    'light': '#ecf0f1',
    'dark': '#34495e',
    'white': '#ffffff',
    'gray': '#95a5a6',
}

# Настройки анализа
ANALYSIS_CONFIG = {
    'max_display_rows': 200,
    'default_output_folder': str(OUTPUT_DIR),
    'supported_formats': ['.xlsx', '.xls', '.csv'],
    'log_max_lines': 1000,
}

def get_version():
    """Получить версию приложения"""
    version_file = BASE_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "2.0.0"